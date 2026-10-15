/**
 * Confere cada slide: nada fora da margem, nenhuma imagem quebrada, e imagem + texto em todos.
 *
 * Todo slide precisa de um bloco com a classe "visual" (foto, print, ilustracao ou tela desenhada),
 * ocupando pelo menos 12% do slide (20% na capa). O avatar do topo nao conta.
 *
 * Uso: node scripts/checar_slides.js <caminho/para/vN>
 * Saida 0 = aprovado. Saida 1 = reprovado (uma linha "FALHA ..." por problema).
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const dir = process.argv[2];
  const html = path.resolve(dir || '.', 'carrossel.html');
  if (!dir || !fs.existsSync(html)) {
    console.error('Uso: node scripts/checar_slides.js <caminho/para/vN> (precisa ter carrossel.html)');
    process.exit(2);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto('file://' + html.split(path.sep).join('/'));
  await page.waitForLoadState('load');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);

  const problemas = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.slide').forEach((s, i) => {
      const r = s.getBoundingClientRect();
      const n = i + 1;
      const capa = s.classList.contains('capa');
      if (Math.round(r.width) !== 1080 || Math.round(r.height) !== 1350) {
        out.push(`slide ${n}: tamanho ${Math.round(r.width)}x${Math.round(r.height)}, esperado 1080x1350`);
      }

      // texto: nada para fora, e tem que existir texto alem da identidade
      const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
      let node, pior = 0, trecho = '', letras = 0;
      while ((node = w.nextNode())) {
        const t = node.textContent.trim();
        if (!t) continue;
        const pai = node.parentElement;
        if (pai.closest('svg, script, style')) continue;
        if (!pai.closest('.identidade')) letras += t.length;
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const q of range.getClientRects()) {
          const fora = Math.max(q.bottom - r.bottom, r.top - q.top, q.right - r.right, r.left - q.left);
          if (fora > pior) { pior = fora; trecho = t.slice(0, 50); }
        }
      }
      if (pior > 2) out.push(`slide ${n}: texto ${Math.round(pior)}px para fora ("${trecho}")`);
      if (letras < 8) out.push(`slide ${n}: sem texto (todo slide precisa de imagem e texto)`);

      // imagens quebradas
      s.querySelectorAll('img').forEach(img => {
        if (!img.complete || img.naturalWidth === 0) out.push(`slide ${n}: imagem quebrada (${img.getAttribute('src')})`);
      });

      // imagem: bloco .visual com conteudo de verdade e tamanho minimo
      const visuais = [...s.querySelectorAll('.visual')].filter(v => !v.closest('.identidade'));
      const minimo = capa ? 0.20 : 0.12;
      let area = 0, comConteudo = false;
      visuais.forEach(v => {
        const q = v.getBoundingClientRect();
        const lx = Math.max(0, Math.min(q.right, r.right) - Math.max(q.left, r.left));
        const ly = Math.max(0, Math.min(q.bottom, r.bottom) - Math.max(q.top, r.top));
        area += lx * ly;
        const img = v.matches('img') ? v : v.querySelector('img');
        const svg = v.matches('svg') ? v : v.querySelector('svg');
        const fundo = getComputedStyle(v).backgroundImage;
        if ((img && img.naturalWidth > 0) || (svg && svg.querySelector('path, rect, circle, ellipse, polygon, line, polyline, image, text')) ||
            (fundo && fundo.startsWith('url(')) || v.querySelectorAll('*').length >= 3) comConteudo = true;  // 3+ elementos = desenho em HTML (card, tela)
      });
      const fracao = area / (r.width * r.height);
      if (!visuais.length || !comConteudo) {
        out.push(`slide ${n}: sem imagem (falta um bloco class="visual" com foto, print ou ilustracao)` + (capa ? ' - na capa isso e obrigatorio' : ''));
      } else if (fracao < minimo) {
        out.push(`slide ${n}: imagem pequena demais (${Math.round(fracao * 100)}% do slide, minimo ${Math.round(minimo * 100)}%)`);
      }
    });
    return out;
  });
  await browser.close();

  if (problemas.length) {
    problemas.forEach(p => console.log('FALHA ' + p));
    process.exit(1);
  }
  console.log('OK: imagem e texto em todos os slides, nada fora da margem');
})().catch(e => { console.error(e.message); process.exit(2); });
