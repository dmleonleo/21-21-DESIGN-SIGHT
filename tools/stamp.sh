#!/bin/sh
# After each build: version app.js and app.css in index.html by their content, so browsers never keep an old copy.
cd "$(dirname "$0")/../docs" || exit 1
J=$(md5sum js/app.js | cut -c1-8); C=$(md5sum css/app.css | cut -c1-8)
sed -i -E "s#js/app\.js(\?v=[0-9a-f]+)?\"#js/app.js?v=$J\"#; s#css/app\.css(\?v=[0-9a-f]+)?\"#css/app.css?v=$C\"#" index.html
grep -o 'app\.[cj]ss*?v=[0-9a-f]*' index.html
