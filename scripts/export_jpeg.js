/**
 * Exporta os slides de um carrossel.html em JPEG 1080x1350, o formato que o
 * Instagram aceita por API. O PNG 2160x2700 que a skill de imagem gera continua
 * sendo o arquivo de arquivo; este aqui e so para publicacao.
 *
 * Uso:
 *   node scripts/export_jpeg.js <caminho/para/vN>
 *
 * Le  <vN>/carrossel.html
 * Grava <vN>/upload/slide-NN.jpg
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const QUALITY = 92;
const VIEWPORT = { width: 1080, height: 1350 };

(async () => {
  const dir = process.argv[2];
  if (!dir) {
    console.error('Uso: node scripts/export_jpeg.js <caminho/para/vN>');
    process.exit(1);
  }
  const html = path.resolve(dir, 'carrossel.html');
  if (!fs.existsSync(html)) {
    console.error('Nao achei carrossel.html em ' + path.resolve(dir));
    process.exit(1);
  }
  const out = path.resolve(dir, 'upload');
  fs.mkdirSync(out, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: VIEWPORT, deviceScaleFactor: 1 });
  await page.goto('file://' + html.split(path.sep).join('/'));
  await page.waitForLoadState('load');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1200);

  const slides = await page.$$('.slide');
  if (slides.length === 0) throw new Error('Nenhum .slide encontrado em carrossel.html');
  if (slides.length > 10) {
    console.error(`AVISO: ${slides.length} slides. O Instagram aceita no maximo 10 por carrossel.`);
  }

  let total = 0;
  for (let i = 0; i < slides.length; i++) {
    const n = String(i + 1).padStart(2, '0');
    const file = path.join(out, `slide-${n}.jpg`);
    await slides[i].screenshot({ path: file, type: 'jpeg', quality: QUALITY });
    const kb = fs.statSync(file).size / 1024;
    total += kb;
    console.log(`slide-${n}.jpg  ${Math.round(kb)}KB`);
  }
  await browser.close();

  console.log(`\n${slides.length} JPEGs em ${VIEWPORT.width}x${VIEWPORT.height}, total ${Math.round(total)}KB`);
  console.log(`Pasta: ${out}`);
  console.log('\nProximo passo:');
  console.log(`  python scripts/r2_upload.py carrosseis/<slug> "${out}/slide-"*.jpg`);
})().catch(e => { console.error(e.message); process.exit(1); });
