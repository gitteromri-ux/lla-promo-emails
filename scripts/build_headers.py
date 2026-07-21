"""Rebuild email header/footer at multiple widths for desktop + mobile.
Sizes: 600 desktop, 320 mobile, plus 2x retina versions of each.
Also generates a wider LP hero banner if needed.
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/home/user/workspace/lla-lp-emails/assets/emails"
DL = "/home/user/workspace/lla-lp-emails/downloads/email-images"
os.makedirs(OUT, exist_ok=True)
os.makedirs(DL, exist_ok=True)

# Brand colors
NAVY = (5, 12, 34)
CREAM = (245, 239, 230)
TEAL = (70, 227, 198)
INK = (11, 21, 51)
MUTED = (183, 192, 208)

# Use the official transparent logo, composited on navy
from PIL import Image
_LOGO_RGBA = Image.open("/home/user/workspace/lla-lp-emails/assets/images/lla-logo-official.png").convert("RGBA")
# Reuse as RGB when needed
LOGO_RGBA = _LOGO_RGBA

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def sans(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size)

def make_header(width, height, logo_h_pct=0.55, teal_bar_h=6):
    """Navy header with transparent-official logo centered, teal underline."""
    img = Image.new("RGBA", (width, height), NAVY + (255,))
    d = ImageDraw.Draw(img)
    logo_h = int(height * logo_h_pct)
    ratio = logo_h / LOGO_RGBA.size[1]
    logo_w = int(LOGO_RGBA.size[0] * ratio)
    logo = LOGO_RGBA.resize((logo_w, logo_h), Image.LANCZOS)
    x = (width - logo_w) // 2
    y = (height - logo_h) // 2 - teal_bar_h // 2
    img.alpha_composite(logo, (x, y))
    bar_y = height - teal_bar_h
    d.rectangle([0, bar_y, width, height], fill=TEAL + (255,))
    return img.convert("RGB")

def make_footer(width, height):
    """Navy footer with logo + tagline + brand + unsubscribe row."""
    img = Image.new("RGB", (width, height), NAVY)
    d = ImageDraw.Draw(img)
    # Top teal accent bar
    bar_h = 6
    d.rectangle([0, 0, width, bar_h], fill=TEAL)
    # Logo top center (transparent official)
    logo_h = int(height * 0.22)
    ratio = logo_h / LOGO_RGBA.size[1]
    logo_w = int(LOGO_RGBA.size[0] * ratio)
    logo = LOGO_RGBA.resize((logo_w, logo_h), Image.LANCZOS)
    x = (width - logo_w) // 2
    y = int(height * 0.14)
    img_rgba = img.convert("RGBA")
    img_rgba.alpha_composite(logo, (x, y))
    img = img_rgba.convert("RGB")
    d = ImageDraw.Draw(img)
    # Tagline (small)
    tagline = "The Longevity Blueprint. Powered by eTeacher Group."
    f_tag = sans(int(height * 0.075))
    tw = d.textlength(tagline, font=f_tag)
    d.text(((width - tw) / 2, y + logo_h + int(height * 0.06)), tagline, font=f_tag, fill=MUTED)
    # Brand field
    brand = "Brand · LGV"
    f_b = sans(int(height * 0.065), bold=True)
    bw = d.textlength(brand, font=f_b)
    d.text(((width - bw) / 2, y + logo_h + int(height * 0.20)), brand, font=f_b, fill=TEAL)
    # Divider
    dy = int(height * 0.78)
    d.line([(int(width*0.1), dy), (int(width*0.9), dy)], fill=(255,255,255,80), width=1)
    # Unsubscribe row
    unsub = "You received this because you subscribed at longevitylifeacademy.com    ·    Unsubscribe    ·    Update preferences"
    f_u = sans(int(height * 0.055))
    uw = d.textlength(unsub, font=f_u)
    if uw > width * 0.94:
        # smaller
        f_u = sans(int(height * 0.045))
        uw = d.textlength(unsub, font=f_u)
    d.text(((width - uw) / 2, dy + int(height * 0.05)), unsub, font=f_u, fill=(155, 165, 185))
    return img

# Desktop: 600w standard + 1200w retina
# Mobile: 320w + 640w retina
sizes = [
    ("desktop", 600, 120, 200),   # (label, width, header_h, footer_h)
    ("desktop-2x", 1200, 240, 400),
    ("mobile", 320, 80, 140),
    ("mobile-2x", 640, 160, 280),
]

for label, w, hh, fh in sizes:
    hdr = make_header(w, hh)
    ftr = make_footer(w, fh)
    hp = f"{OUT}/lla-email-header-{label}.png"
    fp = f"{OUT}/lla-email-footer-{label}.png"
    hdr.save(hp, optimize=True)
    ftr.save(fp, optimize=True)
    # Also copy to downloads
    hdr.save(f"{DL}/lla-email-header-{label}.png", optimize=True)
    ftr.save(f"{DL}/lla-email-footer-{label}.png", optimize=True)
    print(f"  {label:12s}  header {w}x{hh}  footer {w}x{fh}")

# Keep legacy names too (used by already-deployed emails)
make_header(600, 120).save(f"{OUT}/lla-email-header-600.png", optimize=True)
make_header(1200, 240).save(f"{OUT}/lla-email-header.png", optimize=True)
make_footer(600, 200).save(f"{OUT}/lla-email-footer-600.png", optimize=True)
make_footer(1200, 400).save(f"{OUT}/lla-email-footer.png", optimize=True)
print("Legacy 600/1200 preserved.")
