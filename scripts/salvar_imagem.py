"""Grava uma imagem enviada pelo usuario no lugar certo do projeto.

    python scripts/salvar_imagem.py avatar "<origem>"   -> assets/perfil/avatar.jpg  (rosto: corta em quadrado, min. 400)
    python scripts/salvar_imagem.py marca  "<origem>"   -> assets/perfil/logo.png e assets/perfil/avatar.jpg
                                                           (logo no topo dos slides: encaixa inteiro num quadrado, sem cortar)
    python scripts/salvar_imagem.py logo   "<origem>"   -> assets/perfil/logo.png   (so o logo, mantem transparencia)
    python scripts/salvar_imagem.py foto   "<origem>"   -> assets/perfil/fotos/NN.jpg
    python scripts/salvar_imagem.py cores  "<origem>"   -> nao grava nada: lista as cores dominantes da imagem
    python scripts/salvar_imagem.py marca-texto "<nome da marca>" "<#cor de fundo>" "<#cor da letra>"
                                                        -> assets/perfil/avatar.jpg com as iniciais (negocio sem logo)

Imprime o caminho gravado, relativo a raiz do projeto. O usuario nao mexe em pasta.
Durante o /instaflow novo as imagens ficam em assets/perfil/rascunho/ ate o cadastro ser confirmado.
Saida 1 = imagem recusada (motivo na tela): pedir outra.
"""
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Durante o cadastro (existe rascunho) as imagens vao para uma pasta de rascunho: o perfil em uso
# so muda quando o cliente aprova a revisao e o cadastro e confirmado.
EM_CADASTRO = (ROOT / "contexto" / "cadastro-rascunho.md").exists()
PERFIL = ROOT / "assets" / "perfil" / "rascunho" if EM_CADASTRO else ROOT / "assets" / "perfil"
MODOS = ("avatar", "marca", "logo", "foto", "cores")
LIGACAO = {"de", "da", "do", "das", "dos", "e", "em", "a", "o"}


def rel(p):
    return p.relative_to(ROOT).as_posix()


def luminancia(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def cores_dominantes(im, n=6):
    """Cores mais presentes, do maior para o menor uso, sem quase-duplicatas."""
    base = Image.new("RGBA", im.size, (255, 255, 255, 255))
    base.alpha_composite(im.convert("RGBA"))
    p = base.convert("RGB").resize((160, 160)).quantize(colors=12, method=Image.MEDIANCUT)
    pal = p.getpalette()
    usadas = sorted(p.getcolors(), reverse=True)
    saida = []
    for qtd, idx in usadas:
        cor = tuple(pal[idx * 3: idx * 3 + 3])
        if all(sum(abs(a - b) for a, b in zip(cor, o[0])) > 60 for o in saida):
            saida.append((cor, qtd / (160 * 160)))
        if len(saida) == n:
            break
    return saida


def fonte_grossa(tamanho):
    """Uma letra grossa que exista na maquina; se nao achar, a padrao do Pillow."""
    for nome in ("arialbd.ttf", "Arial Bold.ttf", "segoeuib.ttf", "Helvetica.ttc", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default(tamanho)


def marca_de_texto(nome, fundo, letra):
    def rgb(h):
        h = h.strip().lstrip("#")
        if len(h) != 6:
            raise ValueError(h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    try:
        cor_fundo, cor_letra = rgb(fundo), rgb(letra)
    except ValueError:
        print("RECUSADA: as cores precisam ser codigos de 6 digitos, como #0B2C56")
        return 1
    palavras = [p for p in nome.replace("-", " ").split() if p.lower() not in LIGACAO] or nome.split()
    iniciais = "".join(p[0] for p in palavras[:2]).upper() or "?"
    lado = 800
    im = Image.new("RGB", (lado, lado), cor_fundo)
    d = ImageDraw.Draw(im)
    f = fonte_grossa(400 if len(iniciais) == 1 else 320)
    x0, y0, x1, y1 = d.textbbox((0, 0), iniciais, font=f)
    d.text(((lado - (x1 - x0)) / 2 - x0, (lado - (y1 - y0)) / 2 - y0), iniciais, font=f, fill=cor_letra)
    PERFIL.mkdir(parents=True, exist_ok=True)
    im.save(PERFIL / "avatar.jpg", quality=92)
    print(rel(PERFIL / "avatar.jpg"))
    return 0


def main():
    if len(sys.argv) == 5 and sys.argv[1] == "marca-texto":
        return marca_de_texto(sys.argv[2], sys.argv[3], sys.argv[4])
    if len(sys.argv) != 3 or sys.argv[1] not in MODOS:
        sys.exit(__doc__)
    tipo, origem = sys.argv[1], pathlib.Path(sys.argv[2].strip().strip('"'))
    if not origem.is_file():
        print(f"RECUSADA: arquivo nao encontrado: {origem}")
        return 1
    try:
        im = ImageOps.exif_transpose(Image.open(origem))
        im.load()
    except Exception as e:
        print(f"RECUSADA: nao e uma imagem valida ({e})")
        return 1
    PERFIL.mkdir(parents=True, exist_ok=True)

    if tipo == "cores":
        for cor, fracao in cores_dominantes(im):
            hexa = "#%02X%02X%02X" % cor
            tom = "escura" if luminancia(cor) < 80 else ("clara" if luminancia(cor) > 200 else "media")
            print(f"{hexa}  {fracao:5.1%}  {tom}")
        return 0

    if tipo == "avatar":
        lado = min(im.size)
        if lado < 400:
            print(f"RECUSADA: a foto tem {im.size[0]}x{im.size[1]}. Precisa de pelo menos 400 no lado menor.")
            return 1
        esq, topo = (im.size[0] - lado) // 2, (im.size[1] - lado) // 2
        im = im.crop((esq, topo, esq + lado, topo + lado)).convert("RGB")
        if lado > 1080:
            im = im.resize((1080, 1080), Image.LANCZOS)
        im.save(PERFIL / "avatar.jpg", quality=92)
        print(rel(PERFIL / "avatar.jpg"))
        return 0

    if tipo in ("marca", "logo"):
        if max(im.size) < 300:
            print(f"RECUSADA: o logo tem {im.size[0]}x{im.size[1]}. Precisa de pelo menos 300 no lado maior.")
            return 1
        logo = im.convert("RGBA")
        logo.save(PERFIL / "logo.png")
        print(rel(PERFIL / "logo.png"))
        if tipo == "marca":
            # fundo: a cor do canto se o logo for opaco; branco ou escuro, por contraste, se for transparente
            canto = logo.getpixel((0, 0))
            if canto[3] > 200:
                fundo = canto[:3]
            else:
                bruto = logo.resize((60, 60)).tobytes()
                visiveis = [tuple(bruto[i:i + 3]) for i in range(0, len(bruto), 4) if bruto[i + 3] > 128]
                media = sum(luminancia(c) for c in visiveis) / max(len(visiveis), 1)
                fundo = (255, 255, 255) if media < 150 else (17, 17, 17)
            lado = 800
            quadro = Image.new("RGBA", (lado, lado), fundo + (255,))
            miolo = logo.copy()
            miolo.thumbnail((int(lado * 0.72), int(lado * 0.72)), Image.LANCZOS)
            quadro.alpha_composite(miolo, ((lado - miolo.size[0]) // 2, (lado - miolo.size[1]) // 2))
            quadro.convert("RGB").save(PERFIL / "avatar.jpg", quality=92)
            print(rel(PERFIL / "avatar.jpg"))
        return 0

    if min(im.size) < 600:
        print(f"RECUSADA: a foto tem {im.size[0]}x{im.size[1]}. Precisa de pelo menos 600 no lado menor.")
        return 1
    pasta = PERFIL / "fotos"
    pasta.mkdir(parents=True, exist_ok=True)
    usados = [int(p.stem) for p in pasta.glob('*.jpg') if p.stem.isdigit()]
    destino = pasta / f"{max(usados, default=0) + 1:02d}.jpg"
    im = im.convert("RGB")
    if max(im.size) > 2400:
        im.thumbnail((2400, 2400), Image.LANCZOS)
    im.save(destino, quality=90)
    print(rel(destino))
    return 0


if __name__ == "__main__":
    sys.exit(main())
