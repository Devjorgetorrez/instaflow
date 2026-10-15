/**
 * Gera a amostra da identidade visual: um slide escuro e um claro, lado a lado,
 * com o nome, o @ e a imagem do topo que estao no rascunho do cadastro.
 *
 * Uso: node scripts/amostra_identidade.js <letra> <fundo escuro> <fundo claro> <destaque> "<letra titulo>" "<letra texto>"
 * Grava: contexto/amostras/opcao-<letra>.png
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const raiz = path.resolve(__dirname, '..');
const [letra, escuro, claro, destaque, fTitulo = 'Inter Tight', fTexto = 'Inter'] = process.argv.slice(2);
const hex = c => /^#[0-9A-Fa-f]{6}$/.test(c || '');
if (!letra || !hex(escuro) || !hex(claro) || !hex(destaque)) {
  console.error('Uso: node scripts/amostra_identidade.js <letra> <#escuro> <#claro> <#destaque> "<letra titulo>" "<letra texto>"');
  process.exit(2);
}

function campo(nome) {
  for (const arq of ['cadastro-rascunho.md', 'cadastro.md']) {
    const p = path.join(raiz, 'contexto', arq);
    if (!fs.existsSync(p)) continue;
    const m = fs.readFileSync(p, 'utf8').match(new RegExp('^' + nome + ':[ \\t]*(.+)$', 'm'));
    if (m && m[1].trim()) return m[1].trim();
  }
  return '';
}
const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const nome = campo('perfil_nome') || 'Seu nome';
const arroba = '@' + (campo('perfil_arroba') || 'seuperfil').replace(/^@/, '');
const avatarRel = campo('avatar');
const avatar = avatarRel && fs.existsSync(path.join(raiz, avatarRel))
  ? 'data:image/jpeg;base64,' + fs.readFileSync(path.join(raiz, avatarRel)).toString('base64') : '';

const familia = f => f.trim().replace(/ /g, '+');
const css = fs.readFileSync(path.join(raiz, '.claude/skills/instaflow-designer/css/base.css'), 'utf8')
  .replace(/^@import.*$/gm, '');   // a linha inteira: o endereco das fontes tem ponto e virgula no meio
const ident = `<div class="identidade">${avatar ? `<img src="${avatar}" alt="">` : ''}<div><div class="nome">${esc(nome)}</div><div class="arroba">${esc(arroba)}</div></div></div>`;
const tela = cor => `<svg viewBox="0 0 900 420"><rect x="3" y="3" width="894" height="414" rx="18" fill="#fff" stroke="rgba(0,0,0,.18)" stroke-width="4"/>
<rect x="40" y="44" width="430" height="34" rx="8" fill="#222"/><rect x="40" y="112" width="820" height="24" rx="6" fill="#ddd"/>
<rect x="40" y="170" width="820" height="72" rx="10" fill="none" stroke="${cor}" stroke-width="8"/>
<rect x="64" y="194" width="360" height="24" rx="6" fill="${cor}"/><rect x="40" y="280" width="600" height="24" rx="6" fill="#ddd"/><rect x="40" y="330" width="700" height="24" rx="6" fill="#ddd"/></svg>`;

const html = `<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=${familia(fTitulo)}:wght@700;800;900&family=${familia(fTexto)}:wght@400;600;700&display=swap">
<style>${css}
:root{--cor-escura:${escuro};--cor-clara:${claro};--cor-destaque:${destaque};
--fonte-titulo:'${fTitulo}',system-ui,sans-serif;--fonte-texto:'${fTexto}',system-ui,sans-serif;}
html,body{margin:0;padding:0}body{display:flex;flex-direction:row;align-items:flex-start;gap:0;width:2160px;height:1350px;background:#888}
.selo{position:absolute;right:40px;top:40px;font:800 44px/1 system-ui;color:${destaque};z-index:9}
</style></head><body>
<section class="slide capa escura objeto"><div class="selo">${esc(letra)}</div>${ident}
<h1 class="titulo">Assim fica o título dos seus posts</h1><p class="apoio">E assim fica o texto de apoio.</p>
<div class="visual">${tela(destaque)}</div></section>
<section class="slide conteudo">${ident}<span class="rotulo">Destaque</span><div class="traco"></div>
<h2 class="titulo">O slide claro alterna com o escuro</h2>
<div class="texto"><p>Este é o tamanho do texto corrido.</p><p>A cor de destaque marca o que importa.</p></div>
<div class="visual">${tela(destaque)}</div></section>
</body></html>`;

(async () => {
  const pasta = path.join(raiz, 'contexto', 'amostras');
  fs.mkdirSync(pasta, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2160, height: 1350 } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(900);
  const saida = path.join(pasta, `opcao-${letra}.png`);
  await page.screenshot({ path: saida });
  await browser.close();
  console.log(path.relative(raiz, saida).split(path.sep).join('/'));
})().catch(e => { console.error(e.message); process.exit(1); });
