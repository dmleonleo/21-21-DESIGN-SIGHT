// Ambient sound and narration. Everything is synthesised in the browser: no recordings, no licences.
// Sound: a slow, airy pad (D lydian), far glass bells, a breath of air outside, drops in Still Water.
// Voice: the chapter text read aloud with the best English voice the device has (Web Speech API).

const PAD = [73.42, 110.0, 164.81, 185.0, 277.18, 415.3];          // D2 A2 E3 F#3 C#4 G#4
const BELLS = [587.33, 659.25, 739.99, 880.0, 987.77, 1108.73, 1318.5, 1479.98];
const rnd = (a, b) => a + Math.random() * (b - a);
// rooms by decay time (s), brightness (0..1) and wet level; values are judged by ear, not measured
const ROOMS = {
  outside: { rt: 0.7, bright: 0.7, wet: 0.25 }, lobby: { rt: 1.7, bright: 0.55, wet: 0.55 }, stair: { rt: 3.4, bright: 0.45, wet: 0.8 },
  g1: { rt: 2.3, bright: 0.5, wet: 0.65 }, g2: { rt: 3.0, bright: 0.45, wet: 0.75 }, court: { rt: 1.3, bright: 0.7, wet: 0.45 }, g3: { rt: 2.0, bright: 0.5, wet: 0.6 },
};

export function createSound() {
  let ctx = null, master, duckG, padBus, padF, airG, airF, bellBus, verb, started = false;
  let fxBus, roomA, roomB, roomAG, roomBG, roomSend, noiseBuf, roomName = '', roomFlip = false, voices = 0;
  const S = { on: false, under: 0, day: 0, water: false, ducked: false, hidden: false };
  let bellT = 0, dropT = 0, timer = null;

  function impulse(sec, decay) {
    const n = Math.floor(ctx.sampleRate * sec), b = ctx.createBuffer(2, n, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = b.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, decay); }
    return b;
  }
  function build() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = 0;
    duckG = ctx.createGain(); duckG.gain.value = 1;
    const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -20; comp.ratio.value = 3;
    master.connect(duckG).connect(comp).connect(ctx.destination);
    verb = ctx.createConvolver(); verb.buffer = impulse(6, 2.6);
    // spatial effects: each sound sits at its place in the model (HRTF), then goes dry + into the room it is in
    fxBus = ctx.createGain(); fxBus.gain.value = 1; fxBus.connect(master);
    roomA = ctx.createConvolver(); roomB = ctx.createConvolver(); roomAG = ctx.createGain(); roomBG = ctx.createGain(); roomBG.gain.value = 0;
    roomSend = ctx.createGain(); roomSend.gain.value = 1; roomSend.connect(roomA); roomSend.connect(roomB);
    roomA.connect(roomAG).connect(master); roomB.connect(roomBG).connect(master);
    setRoomNow(ROOMS.outside);
    noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate); { const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
    const wet = ctx.createGain(); wet.gain.value = 0.9; verb.connect(wet).connect(master);

    // pad: each note is two slightly detuned voices that breathe in and out on their own slow cycle
    padBus = ctx.createGain(); padBus.gain.value = 0.11;
    padF = ctx.createBiquadFilter(); padF.type = 'lowpass'; padF.frequency.value = 900; padF.Q.value = 0.3;
    padBus.connect(padF); padF.connect(master); padF.connect(verb);
    const fl = ctx.createOscillator(), flg = ctx.createGain(); fl.frequency.value = 0.021; flg.gain.value = 320;
    fl.connect(flg).connect(padF.frequency); fl.start();
    PAD.forEach((f, i) => {
      const g = ctx.createGain(); g.gain.value = 0;
      const pan = ctx.createStereoPanner ? ctx.createStereoPanner() : null;
      for (const det of [-4, 5]) {
        const o = ctx.createOscillator(); o.type = i < 2 ? 'sine' : 'triangle'; o.frequency.value = f; o.detune.value = det + rnd(-2, 2);
        o.connect(g); o.start();
      }
      const lfo = ctx.createOscillator(), lg = ctx.createGain();
      lfo.frequency.value = rnd(0.018, 0.05); lg.gain.value = i < 2 ? 0.35 : 0.5;
      const bias = ctx.createConstantSource ? ctx.createConstantSource() : null;
      lfo.connect(lg).connect(g.gain); lfo.start();
      if (bias) { bias.offset.value = i < 2 ? 0.5 : 0.35; bias.connect(g.gain); bias.start(); }
      const vg = ctx.createGain(); vg.gain.value = i < 2 ? 1 : 0.55 / (1 + (i - 2) * 0.4);
      if (pan) { pan.pan.value = (i % 2 ? 1 : -1) * rnd(0.15, 0.5); g.connect(vg).connect(pan).connect(padBus); } else g.connect(vg).connect(padBus);
    });

    // air: filtered noise, outside only
    const nb = ctx.createBuffer(1, ctx.sampleRate * 4, ctx.sampleRate), nd = nb.getChannelData(0);
    let last = 0; for (let i = 0; i < nd.length; i++) { last = 0.985 * last + 0.015 * (Math.random() * 2 - 1); nd[i] = last * 6; }
    const ns = ctx.createBufferSource(); ns.buffer = nb; ns.loop = true;
    airF = ctx.createBiquadFilter(); airF.type = 'bandpass'; airF.frequency.value = 520; airF.Q.value = 0.6;
    airG = ctx.createGain(); airG.gain.value = 0;
    const al = ctx.createOscillator(), alg = ctx.createGain(); al.frequency.value = 0.07; alg.gain.value = 0.018;
    al.connect(alg).connect(airG.gain); al.start();
    ns.connect(airF).connect(airG).connect(master); ns.start();

    bellBus = ctx.createGain(); bellBus.gain.value = 0.05;
    bellBus.connect(verb); const dry = ctx.createGain(); dry.gain.value = 0.35; bellBus.connect(dry).connect(master);
  }
  function bell(fx, amp, pan, at = 0) {
    const t = ctx.currentTime + at, f = fx || BELLS[Math.floor(Math.random() * BELLS.length)] * (S.under > 0.5 ? 0.5 : 1);
    const g = ctx.createGain(); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(amp || rnd(0.35, 0.7), t + 0.02); g.gain.exponentialRampToValueAtTime(0.0008, t + rnd(5, 8));
    const p = ctx.createStereoPanner ? ctx.createStereoPanner() : null; if (p) p.pan.value = pan ?? rnd(-0.8, 0.8);
    for (const [m, a] of [[1, 1], [2.76, 0.18], [5.4, 0.05]]) {
      const o = ctx.createOscillator(), og = ctx.createGain(); o.frequency.value = f * m; og.gain.value = a;
      o.connect(og).connect(g); o.start(t); o.stop(t + 8);
    }
    (p ? g.connect(p) : g).connect(bellBus);
  }
  function drop() {                         // a single drop on still water
    const t = ctx.currentTime, f = rnd(900, 1700);
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.frequency.setValueAtTime(f, t); o.frequency.exponentialRampToValueAtTime(f * 2.2, t + 0.06);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.12, t + 0.004); g.gain.exponentialRampToValueAtTime(0.0005, t + 0.16);
    const p = ctx.createStereoPanner ? ctx.createStereoPanner() : null; if (p) p.pan.value = rnd(-0.6, 0.6);
    o.connect(g); (p ? g.connect(p) : g).connect(verb); if (p) p.connect(master); else g.connect(master);
    o.start(t); o.stop(t + 0.2);
  }
  // ---------- rooms: a synthetic impulse per space (seconds of decay, brightness, wet level) ----------
  function roomIR(rt, bright) {
    const sr = ctx.sampleRate, n = Math.floor(sr * Math.min(6, rt * 1.2 + 0.2)), b = ctx.createBuffer(2, n, sr);
    for (let c = 0; c < 2; c++) {
      const d = b.getChannelData(c); let lp = 0; const k = 0.15 + 0.8 * bright;
      for (let i = 0; i < n; i++) { const t = i / sr; lp += k * ((Math.random() * 2 - 1) - lp); d[i] = lp * Math.exp(-6.9 * t / rt) * (t < 0.006 ? t / 0.006 : 1); }
      // a few early reflections, distinct per channel
      for (let r = 0; r < 6; r++) { const at = Math.floor(sr * (0.008 + Math.random() * 0.05 * Math.min(1.6, rt))); if (at < n) d[at] += (Math.random() < 0.5 ? -1 : 1) * 0.5 * (1 - r / 7); }
    }
    return b;
  }
  function setRoomNow(R) { roomA.buffer = roomIR(R.rt, R.bright); roomAG.gain.value = R.wet; roomBG.gain.value = 0; roomFlip = false; }
  function setRoom(name) {
    if (!ctx || name === roomName || !ROOMS[name]) return; roomName = name; const R = ROOMS[name], t = ctx.currentTime;
    const [inC, inG, outG] = roomFlip ? [roomA, roomAG, roomBG] : [roomB, roomBG, roomAG];
    inC.buffer = roomIR(R.rt, R.bright);
    inG.gain.cancelScheduledValues(t); inG.gain.setValueAtTime(inG.gain.value, t); inG.gain.linearRampToValueAtTime(R.wet, t + 0.8);
    outG.gain.cancelScheduledValues(t); outG.gain.setValueAtTime(outG.gain.value, t); outG.gain.linearRampToValueAtTime(0, t + 0.8);
    roomFlip = !roomFlip;
  }
  // ---------- a sound at a place ----------
  const L = { x: 0, y: 0, z: 0 };
  function out(pos, amp, wet = 1) {          // -> node to connect a voice into; null when too far or too busy
    const dx = pos.x - L.x, dy = pos.y - L.y, dz = pos.z - L.z, dist = Math.hypot(dx, dy, dz);
    if (dist > 34 || voices > 48) return null;
    const g = ctx.createGain(); g.gain.value = amp;
    const p = ctx.createPanner(); p.panningModel = 'HRTF'; p.distanceModel = 'inverse'; p.refDistance = 1.6; p.rolloffFactor = 1.1; p.maxDistance = 60;
    if (p.positionX) { p.positionX.value = pos.x; p.positionY.value = pos.y; p.positionZ.value = pos.z; } else p.setPosition(pos.x, pos.y, pos.z);
    g.connect(p); p.connect(fxBus);
    const send = ctx.createGain(); send.gain.value = 0.55 * wet; p.connect(send).connect(roomSend);
    voices++; setTimeout(() => { voices--; try { g.disconnect(); p.disconnect(); send.disconnect(); } catch (e) {} }, 12000);
    return g;
  }
  function env(g, t, a, peak, dec) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + dec); }
  function osc(type, f, t, stop, to) { const o = ctx.createOscillator(); o.type = type; o.frequency.setValueAtTime(f, t); o.connect(to); o.start(t); o.stop(t + stop); return o; }
  function noise(t, dur, to, rate = 1) { const n = ctx.createBufferSource(); n.buffer = noiseBuf; n.playbackRate.value = rate; n.connect(to); n.start(t, Math.random() * 0.5, dur); return n; }
  const KINDS = {
    // a drop on still water: a short rising "plip" over a small hollow body
    drop(o, t, { f = rnd(800, 1500), a = 1 }) {
      const g1 = ctx.createGain(); g1.connect(o); env(g1, t, 0.002, 0.5 * a, 0.09);
      const p = osc('sine', f, t, 0.15, g1); p.frequency.exponentialRampToValueAtTime(f * 2.1, t + 0.07);
      const g2 = ctx.createGain(); g2.connect(o); env(g2, t + 0.01, 0.004, 0.25 * a, 0.28);
      osc('sine', f * 0.42, t + 0.01, 0.35, g2).frequency.exponentialRampToValueAtTime(f * 0.6, t + 0.2);
    },
    // a hand moving through water: a soft bandpassed swish
    stir(o, t, { a = 1 }) {
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.setValueAtTime(rnd(900, 1600), t); bp.frequency.exponentialRampToValueAtTime(rnd(2200, 3200), t + 0.2); bp.Q.value = 1.6;
      const g = ctx.createGain(); bp.connect(g).connect(o); env(g, t, 0.05, 0.22 * a, 0.25); noise(t, 0.35, bp);
    },
    // a tuned ring: water basins, pendulums, anything with a pitch
    note(o, t, { f = 440, a = 1, d = 2.6 }) {
      for (const [m, k, dd] of [[1, 1, 1], [2.01, 0.22, 0.5], [3.02, 0.06, 0.3]]) { const g = ctx.createGain(); g.connect(o); env(g, t, 0.004, 0.32 * a * k, d * dd); osc('sine', f * m, t, d * dd + 0.1, g); }
    },
    // long glass or steel: inharmonic partials that beat slowly
    glass(o, t, { f = 660, a = 1, d = 7 }) {
      for (const [m, k, dd] of [[1, 1, 1], [2.32, 0.4, 0.6], [4.25, 0.18, 0.35], [6.63, 0.07, 0.2]]) { const g = ctx.createGain(); g.connect(o); env(g, t, 0.003, 0.26 * a * k, d * dd); const x = osc('sine', f * m, t, d * dd + 0.1, g); x.detune.value = rnd(-4, 4); }
    },
    // a knock on plywood, pitched by size
    wood(o, t, { f = 300, a = 1 }) {
      const g = ctx.createGain(); g.connect(o); env(g, t, 0.001, 0.6 * a, 0.12 + 60 / f);
      osc('triangle', f, t, 0.6, g).frequency.exponentialRampToValueAtTime(f * 0.92, t + 0.2);
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f * 4; bp.Q.value = 2; const gn = ctx.createGain(); bp.connect(gn).connect(o); env(gn, t, 0.001, 0.4 * a, 0.03); noise(t, 0.05, bp);
    },
    // a soft thud: a bag set down, a ball on the floor
    thud(o, t, { f = 90, a = 1 }) {
      const g = ctx.createGain(); g.connect(o); env(g, t, 0.002, 0.8 * a, 0.18);
      osc('sine', f * 1.8, t, 0.25, g).frequency.exponentialRampToValueAtTime(f, t + 0.08);
      const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; const gn = ctx.createGain(); lp.connect(gn).connect(o); env(gn, t, 0.001, 0.3 * a, 0.05); noise(t, 0.06, lp);
    },
    // a tick: the pendulum's second
    tick(o, t, { a = 1, f = 2600 }) {
      const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 1800; const g = ctx.createGain(); hp.connect(g).connect(o); env(g, t, 0.0008, 0.5 * a, 0.02); noise(t, 0.03, hp, 1.5);
      const g2 = ctx.createGain(); g2.connect(o); env(g2, t, 0.001, 0.12 * a, 0.05); osc('sine', f, t, 0.08, g2);
    },
    // small metal discs, a handful
    clink(o, t, { a = 1, n = 5 }) { for (let i = 0; i < n; i++) KINDS.glass(o, t + i * rnd(0.03, 0.09), { f: rnd(2400, 4200), a: a * rnd(0.25, 0.5), d: 0.5 }); },
    // a clap: short noise into the room
    clap(o, t, { a = 1 }) {
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = rnd(1000, 1500); bp.Q.value = 0.9; const g = ctx.createGain(); bp.connect(g).connect(o);
      env(g, t, 0.0015, 0.9 * a, 0.06); noise(t, 0.09, bp);
    },
    // a struck bell: minor-third partials (hum, prime, tierce, quint, nominal...), long, slowly beating
    bell(o, t, { f = 440, a = 1, d = 9 }) {
      for (const [m, k, dd] of [[0.5, 0.35, 1.2], [1, 1, 1], [1.183, 0.45, 0.7], [1.506, 0.25, 0.5], [2, 0.32, 0.45], [2.51, 0.12, 0.3], [3.01, 0.08, 0.22], [4.1, 0.05, 0.14]]) {
        const g = ctx.createGain(); g.connect(o); env(g, t, 0.002, 0.22 * a * k, d * dd); const x = osc('sine', f * m, t, d * dd + 0.1, g); x.detune.value = rnd(-3, 3);
      }
      const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 2500; const gn = ctx.createGain(); hp.connect(gn).connect(o); env(gn, t, 0.0005, 0.2 * a, 0.02); noise(t, 0.03, hp);
    },
    // a marimba bar: fundamental, the tuned 4th partial, a soft mallet
    marimba(o, t, { f = 440, a = 1 }) {
      for (const [m, k, dd] of [[1, 1, 1], [3.99, 0.28, 0.25], [10.6, 0.06, 0.08]]) { const g = ctx.createGain(); g.connect(o); env(g, t, 0.0015, 0.45 * a * k, (0.35 + 180 / f) * dd); osc('sine', f * m, t, 1.6, g); }
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f * 2; bp.Q.value = 3; const gn = ctx.createGain(); bp.connect(gn).connect(o); env(gn, t, 0.0008, 0.18 * a, 0.015); noise(t, 0.02, bp);
    },
    // a plucked string (Karplus-Strong: a noise burst circulating in a tuned delay that loses its highs)
    pluck(o, t, { f = 220, a = 1, d = 3, bright = 0.5 }) {
      const dl = ctx.createDelay(0.05); dl.delayTime.value = 1 / f; const fb = ctx.createGain(); fb.gain.value = Math.pow(0.001, 1 / (f * d)); const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 1200 + 5000 * bright + f * 2;
      const ex = ctx.createGain(); env(ex, t, 0.0005, 0.6 * a, 1 / f * 2.2); const bp = ctx.createBiquadFilter(); bp.type = 'lowpass'; bp.frequency.value = 2000 + 6000 * bright; noise(t, 0.04, bp); bp.connect(ex);
      ex.connect(dl); dl.connect(lp); lp.connect(fb); fb.connect(dl); const g = ctx.createGain(); g.gain.value = 0.9; lp.connect(g).connect(o);
      g.gain.setValueAtTime(0.9, t + d); g.gain.linearRampToValueAtTime(0, t + d + 0.3);
      setTimeout(() => { try { fb.disconnect(); dl.disconnect(); } catch (e) {} }, (t - ctx.currentTime + d + 0.6) * 1000);
    },
    // a footstep on concrete: heel, then the sole
    step(o, t, { a = 1 }) {
      for (const [dt, f, k] of [[0, rnd(300, 420), 1], [rnd(0.05, 0.08), rnd(900, 1400), 0.5]]) { const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f; bp.Q.value = 1.1; const g = ctx.createGain(); bp.connect(g).connect(o); env(g, t + dt, 0.002, 0.5 * a * k, 0.07); noise(t + dt, 0.1, bp); }
      KINDS.thud(o, t, { f: 70, a: 0.25 * a });
    },
    // wood blocks (hyoshigi-like clappers), dry and high
    block(o, t, { f = 1700, a = 1 }) {
      for (const [m, k] of [[1, 1], [2.7, 0.35], [5.1, 0.12]]) { const g = ctx.createGain(); g.connect(o); env(g, t, 0.0006, 0.5 * a * k, 0.05 + 30 / f); osc('sine', f * m, t, 0.3, g); }
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f * 1.5; bp.Q.value = 4; const gn = ctx.createGain(); bp.connect(gn).connect(o); env(gn, t, 0.0005, 0.35 * a, 0.012); noise(t, 0.02, bp);
    },
    // one split-flap leaf falling: a plastic tick with a little hollow body
    flap(o, t, { a = 1, f = rnd(2200, 3400) }) {
      const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f; bp.Q.value = 2.2; const g = ctx.createGain(); bp.connect(g).connect(o); env(g, t, 0.0006, 0.45 * a, 0.018); noise(t, 0.03, bp, 1.3);
      const g2 = ctx.createGain(); g2.connect(o); env(g2, t, 0.001, 0.1 * a, 0.03); osc('triangle', rnd(480, 620), t, 0.06, g2);
    },
    // a crossing signal's bird call: two quick rising sweeps
    chirp(o, t, { a = 1, f = 2100 }) {
      for (const [dt, k] of [[0, 1], [0.11, 0.8]]) { const g = ctx.createGain(); g.connect(o); env(g, t + dt, 0.004, 0.3 * a * k, 0.07); const x = osc('sine', f * 0.78, t + dt, 0.12, g); x.frequency.exponentialRampToValueAtTime(f * 1.18, t + dt + 0.07); }
    },
    // a camera shutter: open and close
    shutter(o, t, { a = 1 }) {
      for (const [dt, f, k] of [[0, 3200, 1], [0.045, 2400, 0.7]]) { const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f; bp.Q.value = 1.4; const g = ctx.createGain(); bp.connect(g).connect(o); env(g, t + dt, 0.0005, 0.35 * a * k, 0.022); noise(t + dt, 0.04, bp, 1.2); }
    },
    // a soft click for UI-like objects: vote pads, squares
    click(o, t, { a = 1, f = 1400 }) { const g = ctx.createGain(); g.connect(o); env(g, t, 0.001, 0.25 * a, 0.06); osc('sine', f, t, 0.1, g); KINDS.tick(o, t, { a: a * 0.4, f: f * 2 }); },
  };
  function play(kind, pos, opt = {}) {
    if (!ctx || !S.on || S.hidden || !KINDS[kind]) return false;
    const o = out(pos, opt.gain ?? 1, opt.wet ?? 1); if (!o) return false;
    KINDS[kind](o, ctx.currentTime + (opt.delay || 0), opt); return true;
  }
  // ---------- drones: a held tone at a place, its level set by the caller ----------
  function drone(pos, f, type = 'sine') {
    if (!ctx) return null;
    const g = ctx.createGain(); g.gain.value = 0;
    const p = ctx.createPanner(); p.panningModel = 'HRTF'; p.distanceModel = 'inverse'; p.refDistance = 1.2; p.rolloffFactor = 1.6; p.maxDistance = 50;
    if (p.positionX) { p.positionX.value = pos.x; p.positionY.value = pos.y; p.positionZ.value = pos.z; } else p.setPosition(pos.x, pos.y, pos.z);
    const srcs = [];
    const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = rnd(0.08, 0.2); lg.gain.value = 0.25;
    const vg = ctx.createGain(); vg.gain.value = 0.75; lfo.connect(lg).connect(vg.gain); srcs.push(lfo);
    let tone = null;
    if (type === 'voice') {
      // a sung vowel: two detuned saws with vibrato through three formant bands; the vowel can morph (ah -> oo)
      const vib = ctx.createOscillator(), vibG = ctx.createGain(); vib.frequency.value = rnd(4.6, 5.6); vibG.gain.value = f * 0.006; vib.connect(vibG); srcs.push(vib);
      const mix = ctx.createGain(); mix.gain.value = 0.22;
      for (const dt of [1, 1.004, 0.997]) { const o = ctx.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f * dt; vibG.connect(o.frequency); o.connect(mix); srcs.push(o); }
      const F = [[730, 1, 9], [1090, 0.5, 11], [2440, 0.18, 14]], bands = [];
      for (const [ff, k, q] of F) { const b = ctx.createBiquadFilter(); b.type = 'bandpass'; b.frequency.value = ff; b.Q.value = q; const bg = ctx.createGain(); bg.gain.value = k * 3.2; mix.connect(b).connect(bg).connect(vg); bands.push(b); }
      tone = (k, tc = 2) => { const A = [730, 1090, 2440], O = [300, 870, 2240]; bands.forEach((b, i) => b.frequency.setTargetAtTime(A[i] + (O[i] - A[i]) * k, ctx.currentTime, tc)); };
    } else if (type === 'wind' || type === 'city') {
      const n = ctx.createBufferSource(); n.buffer = noiseBuf; n.loop = true; const b = ctx.createBiquadFilter(); b.type = type === 'wind' ? 'bandpass' : 'lowpass'; b.frequency.value = f; b.Q.value = type === 'wind' ? 0.7 : 0.5;
      n.connect(b).connect(vg); srcs.push(n); lg.gain.value = 0.6; lfo.frequency.value = rnd(0.05, 0.12);
    } else {
      const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(); o1.type = o2.type = type; o1.frequency.value = f; o2.frequency.value = f * 1.0035; o1.connect(vg); o2.connect(vg); srcs.push(o1, o2);
    }
    vg.connect(g).connect(p); p.connect(fxBus); const send = ctx.createGain(); send.gain.value = 0.4; p.connect(send).connect(roomSend);
    srcs.forEach((x) => x.start());
    return { set(v, tc = 0.4) { g.gain.setTargetAtTime(v, ctx.currentTime, tc); }, vowel(k, tc) { if (tone) tone(k, tc); }, stop() { g.gain.setTargetAtTime(0, ctx.currentTime, 0.3); setTimeout(() => { try { srcs.forEach((x) => x.stop()); p.disconnect(); } catch (e) {} }, 2000); } };
  }
  function tick() {                         // ~4 times a second: scene follows the camera, events are scheduled
    if (!ctx || !S.on) return;
    const t = ctx.currentTime, night = 1 - S.day;
    padF.frequency.setTargetAtTime(S.under > 0.5 ? 520 : 760 + 380 * S.day, t, 2.5);
    airG.gain.setTargetAtTime((1 - S.under) * (0.018 + 0.02 * S.day), t, 2);
    airF.frequency.setTargetAtTime(380 + 260 * S.day, t, 3);
    if (t > bellT) { bell(); bellT = t + rnd(5, 11) * (1 + 0.4 * night); }
    if (S.water && t > dropT) { drop(); dropT = t + rnd(1.4, 4.5); }
  }
  function level() { return S.on && !S.hidden ? 0.9 : 0; }
  function apply() {
    if (!ctx) return;
    const t = ctx.currentTime;
    master.gain.cancelScheduledValues(t); master.gain.setTargetAtTime(level(), t, S.on ? 1.6 : 0.35);
    duckG.gain.setTargetAtTime(S.ducked ? 0.45 : 1, t, 0.6);
    if (S.on && !S.hidden && ctx.state !== 'running') ctx.resume();
  }
  document.addEventListener('visibilitychange', () => { S.hidden = document.hidden; apply(); if (ctx && document.hidden) setTimeout(() => document.hidden && ctx.suspend(), 600); });

  return {
    get on() { return S.on; },
    // must be called from a user gesture the first time (autoplay rules)
    set(on) {
      S.on = on;
      if (on && !started) { build(); started = true; bellT = ctx.currentTime + 3; timer = setInterval(tick, 250); }
      apply();
    },
    scene(o) { Object.assign(S, o); },
    welcome() {                             // the arrival: three bells rising (D, A, E) over the pad as it swells in
      if (!ctx || !S.on) return;
      [[587.33, 1.0, -0.35, 0.25], [880, 0.85, 0.3, 0.95], [1318.5, 0.7, 0, 1.75]].forEach(([f, a, p, at]) => bell(f, a, p, at));
      bellT = ctx.currentTime + 9;
    },
    get ready() { return !!ctx && S.on; },
    get time() { return ctx ? ctx.currentTime : 0; },
    listen(px, py, pz, fx, fy, fz) {           // three.js camera position and forward
      if (!ctx) return; L.x = px; L.y = py; L.z = pz; const l = ctx.listener;
      if (l.positionX) { const t = ctx.currentTime; l.positionX.setTargetAtTime(px, t, 0.03); l.positionY.setTargetAtTime(py, t, 0.03); l.positionZ.setTargetAtTime(pz, t, 0.03); l.forwardX.setTargetAtTime(fx, t, 0.03); l.forwardY.setTargetAtTime(fy, t, 0.03); l.forwardZ.setTargetAtTime(fz, t, 0.03); l.upX.value = 0; l.upY.value = 1; l.upZ.value = 0; }
      else { l.setPosition(px, py, pz); l.setOrientation(fx, fy, fz, 0, 1, 0); }
    },
    room: setRoom, play, drone,
    quiet(k, tc = 1.2) { if (ctx) padBus.gain.setTargetAtTime(0.11 * k, ctx.currentTime, tc); },   // the pad steps back for listening rooms
    duck(on) { if (S.ducked !== on) { S.ducked = on; apply(); } },
  };
}

// ---------- narration ----------
// Pre-recorded clips (Kokoro-82M, Apache 2.0, its af_heart voice pitched lower), one per chapter: voice/<program>/<nn>.mp3
export function createVoice() {
  const el = new Audio(); el.preload = 'auto';
  const V = { on: false, busy: false, i: -1, t: null, onEnd: null, unlocked: false };
  let tok = 0;
  const src = (p, i) => `voice/${p}/${String(i).padStart(2, '0')}.mp3`;
  el.addEventListener('ended', () => { V.busy = false; V.onEnd && V.onEnd(V.i); });
  el.addEventListener('error', () => { V.busy = false; });
  return {
    supported: true,
    get on() { return V.on; },
    get busy() { return V.busy || !!V.t; },
    get index() { return V.i; },
    set onEnd(f) { V.onEnd = f; },
    set(on) { V.on = on; if (!on) this.stop(); },
    unlock() {                              // mobile browsers only let audio start from a gesture: prime the element once
      if (V.unlocked) return; V.unlocked = true;
      try { el.muted = true; el.src = src('building', 0); const p = el.play(); if (p) p.then(() => { if (!V.busy) el.pause(); el.muted = false; }).catch(() => { el.muted = false; }); else el.muted = false; } catch (e) { el.muted = false; }
    },
    say(program, i, delay = 450) {
      if (!V.on) return;
      this.stop(); V.i = i; const my = ++tok;
      V.t = setTimeout(() => {
        V.t = null; if (my !== tok) return;
        el.muted = false; el.src = src(program, i); el.currentTime = 0; V.busy = true;
        const p = el.play(); if (p) p.catch(() => { if (my === tok) V.busy = false; });
        if (program !== 'intro') { const nx = new Audio(); nx.preload = 'auto'; nx.src = src(program, i + 1); }   // warm the next chapter
      }, delay);
    },
    stop() { tok++; clearTimeout(V.t); V.t = null; V.busy = false; V.i = -1; try { el.pause(); } catch (e) {} },
  };
}
