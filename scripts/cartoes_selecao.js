/**
 * Fotografa cada cartao do relatorio de capas: um arquivo por hook, com a referencia, o motivo,
 * a URL e as 3 opcoes juntos. E o que o agente mostra na conversa.
 *
 * Uso: node scripts/cartoes_selecao.js <pasta da selecao>
 * Grava: <pasta>/cartao-hook-N.jpg
 */
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

(async () => {
  const pasta = path.resolve(process.argv[2] || '.');
  const relatorio = path.join(pasta, 'relatorio.html');
  if (!fs.existsSync(relatorio)) { console.error('nao achei relatorio.html em ' + pasta); process.exit(2); }
  const navegador = await chromium.launch();
  try {
    const pagina = await navegador.newPage({ viewport: { width: 1580, height: 1000 }, deviceScaleFactor: 1 });
    await pagina.goto(pathToFileURL(relatorio).href, { waitUntil: 'load' });
    await pagina.waitForTimeout(400);
    const cartoes = pagina.locator('section.cartao');
    const total = await cartoes.count();
    for (let i = 0; i < total; i++) {
      const id = await cartoes.nth(i).getAttribute('id');
      const arquivo = path.join(pasta, `cartao-${id}.jpg`);
      await cartoes.nth(i).screenshot({ path: arquivo, type: 'jpeg', quality: 88 });
      console.log(path.relative(process.cwd(), arquivo).split(path.sep).join('/'));
    }
  } finally {
    await navegador.close();
  }
})().catch(erro => { console.error(erro.message); process.exit(1); });
