// Ambient sound and narration. Everything is synthesised in the browser: no recordings, no licences.
// Sound: a slow, airy pad (D lydian), far glass bells, a breath of air outside, drops in Still Water.
// Voice: the chapter text read aloud with the best English voice the device has (Web Speech API).

const PAD = [73.42, 110.0, 164.81, 185.0, 277.18, 415.3];          // D2 A2 E3 F#3 C#4 G#4
const BELLS = [587.33, 659.25, 739.99, 880.0, 987.77, 1108.73, 1318.5, 1479.98];
const rnd = (a, b) => a + Math.random() * (b - a);

export function createSound() {
  let ctx = null, master, duckG, padBus, padF, airG, airF, bellBus, verb, started = false;
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
  function bell() {
    const t = ctx.currentTime, f = BELLS[Math.floor(Math.random() * BELLS.length)] * (S.under > 0.5 ? 0.5 : 1);
    const g = ctx.createGain(); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(rnd(0.35, 0.7), t + 0.02); g.gain.exponentialRampToValueAtTime(0.0008, t + rnd(4, 7));
    const p = ctx.createStereoPanner ? ctx.createStereoPanner() : null; if (p) p.pan.value = rnd(-0.8, 0.8);
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
        const nx = new Audio(); nx.preload = 'auto'; nx.src = src(program, i + 1);   // warm the next chapter
      }, delay);
    },
    stop() { tok++; clearTimeout(V.t); V.t = null; V.busy = false; V.i = -1; try { el.pause(); } catch (e) {} },
  };
}
