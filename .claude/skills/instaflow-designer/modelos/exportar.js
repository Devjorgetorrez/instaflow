/**
 * Exporta cada slide do carrossel.html desta pasta como slide-NN.png (2160 x 2700).
 * Uso: node <pasta>/exportar.js
 */
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const LARGURA = 1080, ALTURA = 1350, DENSIDADE = 2;

async function exportar() {
  const pasta = __dirname;
  const navegador = await chromium.launch();
  try {
    const pagina = await navegador.newPage({ viewport: { width: LARGURA, height: ALTURA }, deviceScaleFactor: DENSIDADE });
    await pagina.goto(pathToFileURL(path.join(pasta, 'carrossel.html')).href, { waitUntil: 'networkidle' });
    await pagina.evaluate(() => document.fonts.ready);
    await pagina.waitForTimeout(1000);

    const slides = pagina.locator('.slide');
    const total = await slides.count();
    if (total === 0) throw new Error('carrossel.html nao tem nenhum .slide');
    for (let i = 0; i < total; i++) {
      const nome = `slide-${String(i + 1).padStart(2, '0')}.png`;
      await slides.nth(i).screenshot({ path: path.join(pasta, nome) });
      console.log(nome);
    }
    console.log(`Exportados ${total} slides`);
  } finally {
    await navegador.close();
  }
}

exportar().catch(erro => { console.error(erro.message); process.exit(1); });
