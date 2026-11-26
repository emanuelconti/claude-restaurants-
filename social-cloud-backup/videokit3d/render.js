// Renders a scene frame by frame. The scene page defines window.render(t)
// and sets window.ready = true; every frame is one call and one screenshot.
//   node render.js <scene.html> <seconds> [width height] [from to] [outdir]
// Serve the folder first: python3 -m http.server 8765 (from the cache folder).
const { chromium } = require('playwright');
const fs = require('fs');
const [,, scene, secs, w = '1080', h = '1920', from = '0', to, out = 'frames'] = process.argv;
(async () => {
  const W = Number(w), H = Number(h), FPS = 30;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto(`http://localhost:8765/${scene}`, { waitUntil: 'networkidle' });
  await p.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  fs.mkdirSync(out, { recursive: true });
  const z = to ? Number(to) : Math.round(Number(secs) * FPS);
  for (let f = Number(from); f < z; f++) {
    await p.evaluate((t) => window.render(t), f / FPS);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  if (errs.length) console.log('page errors', errs.slice(0, 5));
  await b.close();
})();
