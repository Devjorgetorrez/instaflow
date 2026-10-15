"""Recorta o fundo de uma foto e devolve PNG com transparencia.

Uso:
    python scripts/recortar_fundo.py <entrada> <saida.png> [brilho]

Notas:
- Usa o modelo u2net explicitamente. O modelo padrao do rembg (birefnet) estoura a
  memoria em algumas maquinas com imagens de ~1100x1400 ("Failed to allocate memory for
  requested buffer of size 822083584").
- A saida ja vem cortada na bounding box do recorte, e opcionalmente clareada — foto
  escura some em fundo escuro. 1.30 costuma resolver.
"""
import sys

from PIL import Image, ImageEnhance
from rembg import new_session, remove


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    entrada, saida = sys.argv[1], sys.argv[2]
    brilho = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    origem = Image.open(entrada).convert("RGB")
    recorte = remove(origem, session=new_session("u2net"))
    recorte = recorte.crop(recorte.getbbox())

    if brilho != 1.0:
        rgb = ImageEnhance.Brightness(recorte.convert("RGB")).enhance(brilho)
        rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
        recorte = Image.merge("RGBA", (*rgb.split(), recorte.split()[3]))

    recorte.save(saida)
    print(f"{saida} {recorte.size[0]}x{recorte.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
