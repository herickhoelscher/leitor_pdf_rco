"""Gera assets/logo.ico e assets/logo.png para o Leitor RCO."""
from PIL import Image, ImageDraw, ImageFont
import os

def criar_icone():
    SIZE = 256

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Fundo círculo azul escuro
    d.ellipse([4, 4, SIZE - 4, SIZE - 4], fill="#1E3A6E")

    # Folha de papel (retângulo branco com canto dobrado)
    px, py = 68, 52
    pw, ph = 120, 148
    fold = 24
    papel = [
        (px, py),
        (px + pw - fold, py),
        (px + pw, py + fold),
        (px + pw, py + ph),
        (px, py + ph),
    ]
    d.polygon(papel, fill="white")
    # Canto dobrado
    d.polygon([
        (px + pw - fold, py),
        (px + pw, py + fold),
        (px + pw - fold, py + fold),
    ], fill="#BFD4F5")

    # Linhas simulando texto
    line_x = px + 14
    line_w = pw - 32
    for i, (ly, lw_pct) in enumerate([
        (py + 42, 1.0),
        (py + 60, 0.85),
        (py + 78, 0.90),
        (py + 96, 0.75),
    ]):
        d.rounded_rectangle(
            [line_x, ly, line_x + int(line_w * lw_pct), ly + 8],
            radius=4, fill="#2563EB"
        )

    # Check mark verde no canto inferior direito
    cx, cy, cr = SIZE - 58, SIZE - 58, 30
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill="#16A34A")
    # Desenha um ✓ simples
    ck = [
        (cx - 14, cy),
        (cx - 4, cy + 12),
        (cx + 16, cy - 12),
    ]
    d.line(ck, fill="white", width=5, joint="curve")

    # Salva PNG
    out_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, "logo.png")
    img.save(png_path, "PNG")

    # Salva ICO com múltiplos tamanhos
    ico_path = os.path.join(out_dir, "logo.ico")
    sizes = [16, 32, 48, 64, 128, 256]
    imgs = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    imgs[0].save(ico_path, format="ICO", sizes=[(s, s) for s in sizes],
                 append_images=imgs[1:])

    print(f"Ícone gerado: {ico_path}")
    print(f"PNG gerado:   {png_path}")

if __name__ == "__main__":
    criar_icone()
