"""Build tiga arah mockup Dessert by Anyha.

Sumber:
  data/site.json    identitas, tautan Instagram, alamat, catatan pratinjau
  data/menu.json    tiga produk, harga, dan rincian isian dari pemilik
  assets-src/*.jpeg foto dari pemilik akun
  assets/css/*.css  satu berkas per arah plus pemilih
  assets/js/site.js menu mobile dan lightbox foto

Halaman per arah: beranda, menu, tentang, kontak. Plus pemilih di / dan 404.
Hasil: dist/ siap diunggah ke Cloudflare Pages.

Jalankan: python build.py
"""

import json
import os
import shutil
from html import escape
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets-src")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")

SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8-sig"))
MENU = json.load(open(os.path.join(ROOT, "data", "menu.json"), encoding="utf-8-sig"))

NAMA = SITE["nama"]
USAHA = SITE.get("nama_usaha") or SITE["nama"]

FONTS = {
    1: "family=Fraunces:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700",
    2: "family=Anton&family=Plus+Jakarta+Sans:wght@400;500;700",
    3: "family=Cormorant+Garamond:ital,wght@0,300;0,500;1,400&family=Karla:wght@400;500;700",
    4: "family=Plus+Jakarta+Sans:wght@400;500;700;800",
}
PEMILIH_FONTS = "family=Fraunces:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700"

DESKRIPSI = {
    "beranda": "Mango Sago, Fruit Punch, dan Asinan Kiamboy buatan rumahan dari Dessert by Anyha di Simpang IV Sipin, Jambi. Lihat harga dan isiannya, lalu pesan lewat WhatsApp +62 852-1084-1113. Buka 09.00 sampai 17.00. Halaman ini masih mockup desain.",
    "menu": "Menu Dessert by Anyha: Mango Sago Rp12.000, Fruit Punch Rp12.000, Asinan Kiamboy Rp15.000, lengkap dengan isiannya. Pesan lewat WhatsApp +62 852-1084-1113. Halaman ini masih mockup desain.",
    "tentang": "Cerita Dessert by Anyha, dessert dan minuman rumahan di Simpang IV Sipin, Jambi, yang diracik per pesanan. Buka 09.00 sampai 17.00. Halaman ini masih mockup desain.",
    "kontak": "Cara pesan Dessert by Anyha lewat WhatsApp +62 852-1084-1113, jam buka 09.00 sampai 17.00, plus peta lokasi di Simpang IV Sipin, Jambi City. Halaman ini masih mockup desain.",
}

IKON_IG = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
    '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="12" cy="12" r="4.4" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="17.6" cy="6.6" r="1.2" fill="currentColor"/></svg>'
)

IKON_WA = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12.04 2A9.9 9.9 0 0 0 2.1 11.9c0 1.75.46 3.45 1.32 4.95L2 22l5.3-1.38a9.9 9.9 0 0 0 4.74 1.2h.01A9.9 9.9 0 0 0 22 11.9 9.9 9.9 0 0 0 12.04 2Zm0 18.15h-.01a8.2 8.2 0 0 1-4.18-1.14l-.3-.18-3.11.81.83-3.03-.19-.31a8.2 8.2 0 0 1-1.26-4.4 8.23 8.23 0 0 1 8.23-8.21 8.2 8.2 0 0 1 5.82 2.41 8.18 8.18 0 0 1 2.4 5.82 8.23 8.23 0 0 1-8.23 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.7-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.15.16-.29.18-.54.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.24-1.47-1.38-1.72-.15-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.15.16-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.48c-.16 0-.43.06-.65.31-.23.25-.86.84-.86 2.05s.88 2.38 1 2.54c.12.17 1.73 2.64 4.19 3.7.59.25 1.04.4 1.4.51.59.19 1.12.16 1.55.1.47-.07 1.47-.6 1.67-1.18.21-.58.21-1.08.15-1.18-.06-.11-.23-.17-.48-.29Z"/>'
    '</svg>'
)

IKON_ZOOM = (
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">'
    '<circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<path d="M15.4 15.4l4.1 4.1M10.5 8v5M8 10.5h5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
)


def tautan_pesan(produk=None):
    dasar = SITE.get("wa") or SITE["wa_cadangan"]
    pesan = SITE["wa_pesan"] if not produk else "Halo Dessert by Anyha, saya mau pesan %s." % produk
    if dasar.startswith("https://wa.me/"):
        return dasar + "?text=" + quote(pesan)
    return dasar


def kanal_utama():
    """Teks kanal yang dipakai di copy: WhatsApp kalau nomornya sudah ada."""
    return "WhatsApp" if SITE.get("wa") else "Instagram"


def nomor_wa():
    return SITE.get("wa_tampil", "")


def jam_buka():
    return SITE.get("jam_buka_hari") or SITE.get("jam_buka", "")


def peta_semat():
    """Peta Google yang bisa digeser tanpa membuka tab baru."""
    src = SITE.get("peta_semat")
    if not src:
        return ""
    return (
        '<div class="peta">'
        '<iframe src="%s" title="Peta lokasi %s" loading="lazy" '
        'referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
        '</div>' % (escape(src), escape(SITE.get("alamat", "")))
    )


def tombol_maps(kelas="tombol tombol--garis"):
    maps = SITE.get("maps")
    if not maps:
        return ""
    return ('<a class="%s" href="%s" target="_blank" rel="noopener">Buka di Google Maps</a>'
            % (kelas, escape(maps)))


def pesan(kelas, teks, produk=None, ikon=False):
    """Ikon menyesuaikan kanal tujuan: WhatsApp kalau nomornya sudah diisi."""
    if ikon:
        isi = ("%s " % (IKON_WA if SITE.get("wa") else IKON_IG)) if ikon else ""
    else:
        isi = ""
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s%s</a>' % (
        kelas, escape(tautan_pesan(produk)), isi, teks)


# ------------------------------------------------------------------ produk
_PETA_FOTO = {"mango-sago": "cup", "fruit-punch": "punch", "asinan-kiamboy": "asinan"}


def kunci_foto(p, gaya):
    """Nama kunci gambar per arah, misal a2_asinan."""
    return "a%d_%s" % (gaya, _PETA_FOTO[p["slug"]])


def rincian(p, kelas="rincian"):
    """Blok rincian isian. Tiap kelompok jadi satu kolom berjudul."""
    kolom = []
    for k in p.get("kelompok", []):
        butir = "".join("<li>%s</li>" % escape(t) for t in k["isi"])
        kolom.append(f'<div class="{kelas}__kolom"><p class="{kelas}__judul">{escape(k["judul"])}</p>'
                     f'<ul class="{kelas}__daftar">{butir}</ul></div>')
    if not kolom:
        return ""
    catatan = ""
    if p.get("catatan"):
        catatan = '<p class="%s__catatan">%s</p>' % (kelas, escape(p["catatan"]))
    return '<div class="%s">%s</div>%s' % (kelas, "".join(kolom), catatan)


def semua_kartu(kartu, g):
    """Semua produk berurutan. Fungsi kartu arah 2 menerima nomor urut,
    jadi dicoba dengan nomor dulu lalu tanpa nomor."""
    hasil = []
    for i, p in enumerate(MENU, 1):
        try:
            hasil.append(kartu(p, g, i))
        except TypeError:
            hasil.append(kartu(p, g))
    return "".join(hasil)


# ------------------------------------------------------------------ gambar
def potong(im, rasio, fokus=0.5):
    w, h = im.size
    if w / h > rasio:
        baru = int(round(h * rasio))
        kiri = int(round((w - baru) * fokus))
        return im.crop((kiri, 0, kiri + baru, h))
    baru = int(round(w / rasio))
    atas = int(round((h - baru) * fokus))
    return im.crop((0, atas, w, atas + baru))


def webp(im, nama, mutu=84):
    im.save(os.path.join(IMG, nama), "WEBP", quality=mutu, method=6)
    return {"berkas": "assets/img/" + nama, "w": im.width, "h": im.height}


def sumber(nama):
    return Image.open(os.path.join(SRC, nama)).convert("RGB")


def sumber_bersih(nama, potong_bawah=0.0):
    """Foto kiriman pemilik: satu berkas membawa watermark generator AI di
    sudut bawah, jadi bagian itu dibuang sebelum dipotong ke rasio apa pun."""
    im = sumber(nama)
    if potong_bawah:
        im = im.crop((0, 0, im.width, int(im.height * (1 - potong_bawah))))
    return im


def logo_transparan(nama, sisi, tinta, mutu=92, margin=0.08):
    """Logo kiriman pemilik: JPEG bergaris hitam di atas kertas putih, tersimpan
    miring 90 derajat. Kertasnya dibuang jadi transparan dan tinta diwarnai
    ulang sesuai latar arah, jadi logo menyatu dengan halaman, bukan tampil
    sebagai kotak putih."""
    im = sumber(nama).convert("L").rotate(-90, expand=True)

    # pangkas kertas putih di luar bingkai label
    kotak = im.point(lambda v: 255 if v < 245 else 0).getbbox()
    if kotak:
        tepi = 8
        im = im.crop((
            max(0, kotak[0] - tepi), max(0, kotak[1] - tepi),
            min(im.width, kotak[2] + tepi), min(im.height, kotak[3] + tepi),
        ))

    # alfa dari gelapnya piksel: putih hilang, tepi garis tetap halus
    alfa = im.point(lambda v: 0 if v >= 246 else min(255, (246 - v) * 255 // 210))
    tinta_im = Image.new("RGBA", im.size, tuple(tinta) + (255,))
    tinta_im.putalpha(alfa)

    kanvas_sisi = int(round(max(im.width, im.height) * (1 + 2 * margin)))
    kanvas = Image.new("RGBA", (kanvas_sisi, kanvas_sisi), (0, 0, 0, 0))
    kanvas.paste(tinta_im, ((kanvas_sisi - im.width) // 2, (kanvas_sisi - im.height) // 2))
    return kanvas.resize((sisi, sisi), Image.LANCZOS)


def siapkan_gambar():
    if os.path.isdir(IMG):
        shutil.rmtree(IMG)
    os.makedirs(IMG, exist_ok=True)
    hasil = {}

    cup_sun = sumber_bersih("mango-sago-sunlit.jpeg", 0.09)
    cup_hand = sumber("mango-sago-hand.jpeg")
    punch = sumber("fruit-punch.jpeg")
    asinan = sumber("asinan-kiamboy.jpeg")
    logo = sumber("logo-anyha.jpeg")

    hasil["a1_hero"] = webp(potong(cup_sun, 4 / 5, 0.5).resize((900, 1125), Image.LANCZOS), "a1-hero.webp")
    hasil["a1_cup"] = webp(potong(cup_hand, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-cup.webp")
    hasil["a1_punch"] = webp(potong(punch, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-punch.webp")
    hasil["a1_asinan"] = webp(potong(asinan, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-asinan.webp")
    hasil["a1_logo"] = webp(logo_transparan("logo-anyha.jpeg", 520, (42, 29, 21)), "a1-logo.webp")
    hasil["a2_logo"] = webp(logo_transparan("logo-anyha.jpeg", 520, (255, 248, 236)), "a2-logo.webp")

    hasil["a2_panggung"] = webp(potong(cup_sun, 16 / 9, 0.5).resize((1600, 900), Image.LANCZOS), "a2-panggung.webp", 82)
    hasil["a2_cup"] = webp(potong(cup_hand, 1, 0.5).resize((360, 360), Image.LANCZOS), "a2-cup.webp")
    hasil["a2_punch"] = webp(potong(punch, 1, 0.5).resize((360, 360), Image.LANCZOS), "a2-punch.webp")
    hasil["a2_asinan"] = webp(potong(asinan, 1, 0.5).resize((360, 360), Image.LANCZOS), "a2-asinan.webp")
    hasil["a2_panggung_menu"] = webp(potong(asinan, 16 / 9, 0.4).resize((1600, 900), Image.LANCZOS), "a2-panggung-menu.webp", 82)

    hasil["a3_hero"] = webp(potong(cup_sun, 16 / 10, 0.5).resize((1440, 900), Image.LANCZOS), "a3-hero.webp")
    hasil["a3_cup"] = webp(potong(cup_hand, 1, 0.5).resize((640, 640), Image.LANCZOS), "a3-cup.webp")
    hasil["a3_punch"] = webp(potong(punch, 1, 0.5).resize((640, 640), Image.LANCZOS), "a3-punch.webp")
    hasil["a3_asinan"] = webp(potong(asinan, 1, 0.5).resize((640, 640), Image.LANCZOS), "a3-asinan.webp")
    hasil["a3_logo"] = webp(logo_transparan("logo-anyha.jpeg", 480, (38, 43, 34)), "a3-logo.webp")

    # arah 4 mengikuti tata letak situs referensi: foto produk 4/3, bingkai putih
    hasil["a4_logo"] = webp(logo_transparan("logo-anyha.jpeg", 560, (18, 63, 42)), "a4-logo.webp")
    hasil["a4_hero"] = webp(potong(cup_sun, 4 / 3, 0.45).resize((1100, 825), Image.LANCZOS), "a4-hero.webp")
    hasil["a4_cup"] = webp(potong(cup_hand, 4 / 3, 0.5).resize((720, 540), Image.LANCZOS), "a4-cup.webp")
    hasil["a4_punch"] = webp(potong(punch, 4 / 3, 0.5).resize((720, 540), Image.LANCZOS), "a4-punch.webp")
    hasil["a4_asinan"] = webp(potong(asinan, 4 / 3, 0.5).resize((720, 540), Image.LANCZOS), "a4-asinan.webp")
    hasil["a4_cerita"] = webp(potong(asinan, 1, 0.45).resize((820, 820), Image.LANCZOS), "a4-cerita.webp")
    hasil["a4_proses"] = webp(potong(cup_hand, 1, 0.5).resize((820, 820), Image.LANCZOS), "a4-proses.webp")

    og = potong(cup_sun, 1200 / 630, 0.45).resize((1200, 630), Image.LANCZOS)
    og.save(os.path.join(IMG, "og.jpg"), "JPEG", quality=84, optimize=True, progressive=True)

    hasil["og"] = {"berkas": "assets/img/og.jpg", "w": 1200, "h": 630}

    # favicon tiga arah: huruf A dengan warna latar berbeda
    for nama, warna, tinta in (
        ("favicon.png", (251, 244, 231), (42, 29, 21)),
        ("favicon-2.png", (20, 16, 14), (255, 179, 40)),
        ("favicon-3.png", (245, 242, 234), (70, 82, 58)),
        ("favicon-4.png", (251, 247, 238), (18, 63, 42)),
    ):
        ikon = Image.new("RGB", (128, 128), warna)
        g = ImageDraw.Draw(ikon)
        try:
            font = ImageFont.truetype("georgiab.ttf", 86)
        except OSError:
            try:
                font = ImageFont.truetype("arialbd.ttf", 84)
            except OSError:
                font = ImageFont.load_default()
        kotak = g.textbbox((0, 0), "A", font=font)
        g.text(((128 - (kotak[2] - kotak[0])) / 2 - kotak[0],
                (128 - (kotak[3] - kotak[1])) / 2 - kotak[1]),
               "A", font=font, fill=tinta)
        ikon.save(os.path.join(DIST, "assets", nama), "PNG")

    return hasil


def gambar(d, alt, kelas="", lazy=True, prioritas=False):
    muat = 'loading="eager" ' if prioritas else ""
    if lazy and not prioritas:
        muat = 'loading="lazy" decoding="async" '
    return '<img src="/%s" alt="%s" width="%d" height="%d" %s%s>' % (
        d["berkas"], escape(alt), d["w"], d["h"],
        muat, ('fetchpriority="high" decoding="async" ' if prioritas else ""))


# ------------------------------------------------------------------ kepala dan kaki
def pita_mockup():
    return """
<div class="pita-mockup" role="note">
  <span>Mockup desain</span>
  <p>Pratinjau desain, belum situs resmi. Harga dan jam buka sudah sesuai data pemilik.</p>
</div>"""


def kepala(judul, deskripsi, css, tema, fonts, kanonikal, ikon):
    kanon = og_url = ""
    if SITE.get("url"):
        kanon = '<link rel="canonical" href="%s%s">' % (SITE["url"], kanonikal)
        og_url = '<meta property="og:url" content="%s%s">' % (SITE["url"], kanonikal)
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="{tema}">
<title>{escape(judul)}</title>
<meta name="description" content="{escape(deskripsi)}">
{kanon}
<meta property="og:type" content="website">
<meta property="og:locale" content="id_ID">
<meta property="og:site_name" content="{escape(NAMA)}">
<meta property="og:title" content="{escape(judul)}">
<meta property="og:description" content="{escape(deskripsi)}">
<meta property="og:image" content="/assets/img/og.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{og_url}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/{ikon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="/assets/css/{css}">
</head>
<body>
<a class="lewati" href="#utama">Lewati ke isi utama</a>
"""


def tutup(melayang=True):
    tombol = ""
    if melayang:
        tombol = ('<a class="wa-melayang" href="%s" target="_blank" rel="noopener" '
                  'aria-label="Pesan lewat WhatsApp %s">%s</a>\n'
                  % (escape(tautan_pesan()), escape(USAHA), IKON_IG))
    return f"""
{tombol}<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


_CACHE_LOGO_KAKI = {}


def kaki(gaya):
    # tinta logo mengikuti warna teks footer tiap arah
    if gaya not in _CACHE_LOGO_KAKI:
        tinta = {1: (42, 29, 21), 2: (255, 248, 236), 3: (38, 43, 34), 4: (203, 218, 208)}.get(gaya, (42, 29, 21))
        _CACHE_LOGO_KAKI[gaya] = webp(logo_transparan("logo-anyha.jpeg", 420, tinta), "kaki-logo-%d.webp" % gaya)
    logo = _CACHE_LOGO_KAKI[gaya]
    isi = f"""
<footer class="kaki">
  <div class="wrap kaki__{'grid' if gaya in (1, 4) else 'isi'}">
    <div>
      <a class="kaki__merek" href="/arah-{gaya}/">
        <img src="/{logo['berkas']}" alt="Logo Fruit Punch by Anyha" width="{logo['w']}" height="{logo['h']}" loading="lazy" decoding="async">
      </a>
      <strong>{escape(NAMA)}</strong>
      <p>Dessert dan minuman buah rumahan di {escape(SITE.get('alamat', 'Jambi'))}. Buka {escape(jam_buka())}.</p>
    </div>
    <div>
      <ul>
        <li><a href="/arah-{gaya}/menu/">Menu</a></li>
        <li><a href="/arah-{gaya}/tentang/">Tentang</a></li>
        <li><a href="/arah-{gaya}/kontak/">Cara pesan</a></li>
        <li><a href="{escape(tautan_pesan())}" target="_blank" rel="noopener">WhatsApp {escape(nomor_wa())}</a></li>
        <li><a href="{escape(SITE['instagram'])}" target="_blank" rel="noopener">Instagram {escape(SITE['handle'])}</a></li>
        <li><a href="{escape(SITE.get('maps', SITE['instagram']))}" target="_blank" rel="noopener">{escape(SITE.get('alamat', 'Lokasi'))}</a></li>
        <li>Buka {escape(jam_buka())}</li>
      </ul>
    </div>
  </div>
  <div class="wrap kaki__bawah">
    <span>&copy; 2026 {escape(USAHA)}.</span>
    <span>{escape(SITE['catatan_pratinjau'])}</span>
  </div>
</footer>"""
    if gaya == 1:
        isi = isi.replace('<div class="wrap kaki__bawah">', '<div class="wrap kaki__bawah">')
    return isi


def kepala_dalam(nomor, label, h1, intro):
    return f"""
<section class="d-kepala">
  <div class="wrap">
    <p class="label"><span>{nomor}</span> {escape(label)}</p>
    <h1>{escape(h1)}</h1>
    <p class="d-intro">{escape(intro)}</p>
  </div>
</section>"""


# ------------------------------------------------------------------ arah 1
def nav_1(aktif):
    def item(kunci, href, teks):
        tanda = ' aria-current="page"' if aktif == kunci else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)
    return pita_mockup() + f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-1/">
      <strong>{escape(NAMA)}</strong>
      <span>Rumahan</span>
    </a>
    <button class="menu-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="menu-tombol__garis" aria-hidden="true"></span>Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {item("menu", "/arah-1/menu/", "Menu")}
        {item("tentang", "/arah-1/tentang/", "Tentang")}
        {item("kontak", "/arah-1/kontak/", "Cara pesan")}
        <li>{pesan("nav__cta", "Pesan")}</li>
      </ul>
    </nav>
  </div>
</header>"""


def kartu_1(p, g):
    kunci = kunci_foto(p, 1)
    return f"""
      <article class="kartu">
        <div class="kartu__foto">
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </div>
        <div class="kartu__isi">
          <p class="kartu__label">{escape(p['label'])}</p>
          <h3>{escape(p['nama'])}</h3>
          <p class="kartu__harga">{escape(p['harga'])}</p>
          <p>{escape(p['deskripsi'])}</p>
          {rincian(p, "rincian")}
          <div class="kartu__kaki">
            <span>{escape(p['catatan'])}</span>
            {pesan("tautan-kecil", "Pesan", p["nama"] + " " + p["harga"])}
          </div>
        </div>
      </article>"""


def langkah_1():
    langkah = [
        ("Pilih menunya", "Lihat tiga menu beserta harganya, lalu tentukan jumlahnya."),
        ("Chat WhatsApp", "Kirim pesan berisi menu, jumlah, dan tanggal ambil atau kirim."),
        ("Konfirmasi", "Pemilik membalas harga dan jadwal. Pesanan disiapkan setelah itu."),
    ]
    return "".join(f"""
        <li>
          <span class="langkah__no">{i:02d}</span>
          <h3>{escape(j)}</h3>
          <p>{escape(t)}</p>
        </li>""" for i, (j, t) in enumerate(langkah, 1))


def arah_1(g):
    return kepala(
        "Mockup Dessert by Anyha, dessert cup mangga rumahan",
        DESKRIPSI["beranda"] + " Tiga menu: Mango Sago, Fruit Punch, dan Asinan Kiamboy.",
        "arah-1.css", "#FBF4E7", FONTS[1], "/arah-1/", "favicon.png",
    ) + nav_1("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="kicker">Dessert rumahan</p>
      <h1>Mangga manis, <em>dirakit per pesanan.</em></h1>
      <p class="hero__p">Dessert cup berisi potongan mangga, sagu mutiara, dan susu. Ada juga fruit punch botolan dari campuran buah segar. Semua dibuat setelah pesanan masuk, jadi datangnya masih segar.</p>
      <div class="aksi">
        {pesan("tombol", "Pesan lewat WhatsApp", ikon=True)}
        <a class="tombol tombol--garis" href="/arah-1/menu/">Lihat menu</a>
      </div>
      <ul class="poin">
        <li>Mangga potong asli</li>
        <li>Dibuat per pesanan</li>
        <li>Less sugar</li>
      </ul>
    </div>
    <figure class="hero__foto">
      {gambar(g["a1_hero"], "Dessert cup mangga dengan lapisan susu di atas piring batu, disinari matahari pagi")}
      <button class="tombol-zoom" type="button" data-zoom="/{g['a1_hero']['berkas']}" data-zoom-alt="Dessert cup mangga dengan lapisan susu" aria-label="Perbesar foto dessert cup">{IKON_ZOOM}</button>
    </figure>
  </div>
</section>

<section class="bagian bagian--garis" id="menu">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>01</span> Menu</p>
        <h2>Tiga menu, semua dirakit setelah pesanan masuk.</h2>
      </div>
      <p>Harga per cup atau botol. Isian lengkap tiap menu ada di bawah, supaya tidak perlu tanya dulu.</p>
    </div>
    <div class="menu-grid">{semua_kartu(kartu_1, g)}</div>
  </div>
</section>

<section class="bagian bagian--garis" id="cara">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>02</span> Cara pesan</p>
        <h2>Tiga langkah, lewat WhatsApp.</h2>
      </div>
      <p>Belum ada aplikasi atau keranjang. Cukup chat, lalu pesanan disiapkan.</p>
    </div>
    <ol class="langkah">{langkah_1()}</ol>
  </div>
</section>

<section class="cta">
  <div class="wrap cta__isi">
    <div>
      <h2>Mau pesan untuk hari ini?</h2>
      <p>Sebutkan menu, jumlah, dan mau diambil atau dikirim. Balasan berisi harga dan jadwal siapnya.</p>
    </div>
    <div class="aksi">
      {pesan("tombol tombol--mangga", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
</main>
""" + kaki(1) + tutup()


def halaman_1(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-1.css", "#FBF4E7", FONTS[1], path, "favicon.png") + \
        nav_1(aktif) + '<main id="utama">' + isi + "</main>" + kaki(1) + tutup()


def isi_menu_1(g):
    return kepala_dalam("01", "Menu", "Menu hari ini.", "Tiga menu yang tersedia sekarang, lengkap dengan harga dan isiannya.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="menu-grid">{semua_kartu(kartu_1, g)}</div>
    <div class="d-catatan">
      <p><strong>Pesan lewat WhatsApp.</strong> Sebutkan menu, jumlah, dan tanggal.</p>
      {pesan("tombol", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>02</span> Cara pesan</p>
        <h2>Tiga langkah, lewat WhatsApp.</h2>
      </div>
    </div>
    <ol class="langkah">{langkah_1()}</ol>
  </div>
</section>"""


def isi_tentang_1(g):
    return kepala_dalam("01", "Tentang", "Dibuat di rumah, dikirim hari itu.", "Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Sekarang menunya bertambah fruit punch, dengan cara kerja yang sama: dirakit setelah pesanan masuk.") + f"""
<section class="bagian">
  <div class="wrap d-dua">
    <div>
      <p class="label"><span>02</span> Cara kami bekerja</p>
      <h2>Tidak ada stok menganggur.</h2>
      <p>Mangga dipotong setelah pesanan masuk, lalu cup dirakit dan langsung disimpan dingin. Fruit punch diracik dengan takaran gula yang lebih ringan dari minuman buah biasa.</p>
      <p>Karena itu, pesanan sebaiknya masuk sehari sebelum mau diambil. Untuk jumlah banyak, tanyakan lebih awal lewat WhatsApp.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga potong, sagu mutiara, susu, campuran buah segar.</span></li>
        <li><strong>Kemasan</strong><span>Cup plastik bening dan botol, siap makan langsung.</span></li>
        <li><strong>Pemesanan</strong><span>Lewat chat Instagram, tanpa minimum yang rumit.</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure class="d-foto">
      {gambar(g["a1_logo"], "Logo Dessert by Anyha bertuliskan Fruit Punch by Anyha dengan keterangan mix fruit, fresh, less sugar")}
    </figure>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>03</span> Foto produk</p>
        <h2>Seperti ini bentuknya.</h2>
      </div>
      <p>Foto dari pemilik akun, tanpa penyuntingan warna.</p>
    </div>
    <div class="menu-grid">
      <figure class="kartu" style="padding:1rem">
        {gambar(g["a1_cup"], "Dessert cup mangga digenggam, tampak lapisan mangga dan sagu")}
      </figure>
      <figure class="kartu" style="padding:1rem">
        {gambar(g["a1_punch"], "Botol Fruit Punch oranye dengan label Fruit Punch by Anyha")}
      </figure>
    </div>
  </div>
</section>"""


def isi_kontak_1():
    return kepala_dalam("01", "Cara pesan", "Chat, konfirmasi, lalu ambil atau kirim.", f"Pesanan diterima lewat WhatsApp {nomor_wa()} atau DM Instagram. Jam buka {jam_buka()}.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="d-grid3">
      <div class="d-kartu">
        <h2>Instagram</h2>
        <p>Cara utama memesan. Kirim menu, jumlah, dan tanggal.</p>
        <p class="d-kecil">{escape(SITE['handle'])}</p>
        {pesan("tombol tombol--garis", "Buka Instagram", ikon=True)}
      </div>
      <div class="d-kartu">
        <h2>WhatsApp</h2>
        <p>Cara tercepat memesan. Balasan di jam buka.</p>
        <p class="d-kecil">{escape(nomor_wa())}</p>
        {pesan("tombol tombol--garis", "Chat WhatsApp")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Buka {escape(jam_buka())}. Bisa diambil langsung atau dikirim.</p>
        <p class="d-kecil">Sebutkan alamat saat chat, pemilik membalas ongkirnya.</p>
      </div>
    </div>
    <div class="d-catatan">
      <p><strong>Siapkan pesanan sehari sebelumnya</strong> untuk jumlah banyak.</p>
      {pesan("tombol", "Tanya jadwal")}
    </div>
    <div class="d-dua" style="margin-top:2.5rem">
      <div>
        <p class="label"><span>02</span> Yang perlu disebut</p>
        <h2>Agar balasan langsung berisi total.</h2>
        <ul class="d-daftar">
          <li><strong>Menu</strong><span>Mango Sago, Fruit Punch, atau Asinan Kiamboy</span></li>
          <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
          <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
          <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
        </ul>
      </div>
      <div>
        <p class="label"><span>03</span> Pembayaran</p>
        <h2>Menyusul.</h2>
        <p>Metode pembayaran dan ketentuan DP belum dikirim pemilik. Halaman ini akan diperbarui begitu informasinya ada, supaya tidak ada janji yang tidak benar.</p>
      </div>
    </div>
  </div>
</section>"""


# ------------------------------------------------------------------ arah 2
def nav_2(aktif):
    def item(kunci, href, teks):
        tanda = ' aria-current="page"' if aktif == kunci else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)
    return pita_mockup() + f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-2/"><strong>Mockup</strong><span>Anyha Dessert</span></a>
    <button class="menu-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="menu-tombol__garis" aria-hidden="true"></span>Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {item("menu", "/arah-2/menu/", "Menu")}
        {item("tentang", "/arah-2/tentang/", "Cerita")}
        {item("kontak", "/arah-2/kontak/", "Order")}
        <li>{pesan("nav__cta", "Pesan")}</li>
      </ul>
    </nav>
  </div>
</header>"""


def baris_menu_2(p, g, nomor):
    kunci = kunci_foto(p, 2)
    return f"""
      <li>
        <div class="baris-menu__isi">
          <div class="baris-menu__foto">
            {gambar(g[kunci], p['foto_alt'])}
            <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
          </div>
          <div class="baris-menu__teks">
            <p class="baris-menu__nomor">{nomor:02d}</p>
            <h3>{escape(p['nama'])}</h3>
            <p>{escape(p['deskripsi'])}</p>
            {rincian(p, "rincian-2")}
          </div>
          <div class="baris-menu__kanan">
            <span class="baris-menu__harga">{escape(p['harga'])}</span>
            <a class="tautan-kecil" href="{escape(tautan_pesan(p['nama'] + ' ' + p['harga']))}" target="_blank" rel="noopener">Pesan</a>
          </div>
        </div>
      </li>"""


def langkah_2():
    langkah = [
        ("Chat masuk", "Sebut menu, jumlah, dan kapan mau diambil."),
        ("Balasan harga", "Pemilik mengonfirmasi total dan jadwal siap."),
        ("Ambil atau kirim", "Pesanan disiapkan hari itu supaya masih segar."),
    ]
    return "".join(f"""
        <li>
          <span class="langkah__no">{i:02d}</span>
          <h3>{escape(j)}</h3>
          <p>{escape(t)}</p>
        </li>""" for i, (j, t) in enumerate(langkah, 1))


def arah_2(g):
    return kepala(
        "Mockup Dessert by Anyha, dessert cup mangga dan fruit punch",
        DESKRIPSI["beranda"] + " Pesan lewat WhatsApp.",
        "arah-2.css", "#14100E", FONTS[2], "/arah-2/", "favicon-2.png",
    ) + nav_2("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap">
    <p class="kicker">Dessert rumahan</p>
    <h1>Mangga<em>tengah malam.</em></h1>
    <div class="hero__bawah">
      <div>
        <p class="hero__p">Dessert cup mangga dan fruit punch botolan. Dibuat setelah pesanan masuk, jadi tidak ada yang menginap di kulkas.</p>
        <div class="aksi">
          {pesan("tombol", "Pesan sekarang", ikon=True)}
          <a class="tombol tombol--garis" href="/arah-2/menu/">Lihat menu</a>
        </div>
      </div>
      <ul class="poin">
        <li>Mangga asli</li>
        <li>Less sugar</li>
        <li>Per pesanan</li>
      </ul>
    </div>
  </div>
  <figure class="panggung">
    {gambar(g["a2_panggung"], "Dessert cup mangga dengan lapisan susu di atas piring batu dan cahaya matahari", prioritas=True)}
    <button class="tombol-zoom" type="button" data-zoom="/{g['a2_panggung']['berkas']}" data-zoom-alt="Dessert cup mangga dengan lapisan susu" aria-label="Perbesar foto dessert cup">{IKON_ZOOM}</button>
  </figure>
</section>

<div class="pita">
  <div class="wrap">
    <ul>
      <li>Mangga potong</li>
      <li>Sagu mutiara</li>
      <li>Susu</li>
      <li>Campuran buah</li>
      <li>Less sugar</li>
    </ul>
  </div>
</div>

<section class="bagian" id="menu">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label"><span>01</span> Menu</p>
      <h2>Tiga barang.</h2>
      <p>Harga per cup atau botol, isian lengkap di tiap baris.</p>
    </div>
    <ul class="baris-menu">{semua_kartu(baris_menu_2, g)}</ul>
  </div>
</section>

<section class="bagian bagian--garis">
  <div class="wrap d-dua">
    <div>
      <p class="label"><span>02</span> Cerita</p>
      <h2>Dirakit setelah kamu bilang pesan.</h2>
      <p>Dessert by Anyha tidak menumpuk stok. Mangga dipotong setelah pesanan masuk, cup dirakit, lalu langsung dingin. Fruit punch diracik dengan gula yang lebih ringan.</p>
      <ul class="d-daftar">
        <li><strong>Bahan</strong><span>Mangga, sagu mutiara, susu, buah</span></li>
        <li><strong>Kemasan</strong><span>Cup bening dan botol</span></li>
        <li><strong>Pesan</strong><span>Instagram, tanpa aplikasi</span></li>
      </ul>
    </div>
    <figure class="d-foto">
      {gambar(g["a2_panggung_menu"], "Dessert cup mangga digenggam dengan latar dinding kuning")}
    </figure>
  </div>
</section>

<section class="bagian">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label"><span>03</span> Order</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah_2()}</ol>
  </div>
</section>

<section class="cta">
  <div class="wrap cta__isi">
    <div>
      <h2>Lapar?<br>Chat sekarang.</h2>
      <p>Sebut menu, jumlah, dan tanggal. Balasan berisi harga dan jadwal siap.</p>
    </div>
    <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki(2) + tutup()


def halaman_2(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-2.css", "#14100E", FONTS[2], path, "favicon-2.png") + \
        nav_2(aktif) + '<main id="utama">' + isi + "</main>" + kaki(2) + tutup()


def isi_menu_2(g):
    return kepala_dalam("01", "Menu", "Tiga barang, harga jelas.", "Daftar ini yang tersedia sekarang, lengkap dengan harga dan isiannya.") + f"""
<section class="bagian">
  <div class="wrap">
    <ul class="baris-menu">{semua_kartu(baris_menu_2, g)}</ul>
    <div class="d-catatan">
      <p>Pesan lewat WhatsApp, sebutkan menu dan jumlahnya.</p>
      {pesan("tombol", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label"><span>02</span> Order</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah_2()}</ol>
  </div>
</section>"""


def isi_tentang_2(g):
    return kepala_dalam("01", "Cerita", "Dari satu cup, lalu pesan ulang.", "Dessert by Anyha mulai dari dessert cup mangga yang sering diminta lagi oleh pembeli pertama. Cara kerjanya tetap sama sampai sekarang: dirakit setelah pesanan masuk.") + f"""
<section class="bagian">
  <div class="wrap d-dua">
    <div>
      <p class="label"><span>02</span> Cara kerja</p>
      <h2>Tidak ada yang menginap semalam.</h2>
      <p>Mangga dipotong dan cup dirakit pada hari pesanan. Fruit punch diracik dengan gula lebih ringan, jadi rasanya lebih dekat ke buah aslinya.</p>
      <p>Pesanan jumlah banyak sebaiknya masuk sehari sebelumnya. Tanyakan lewat Instagram.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga potong, sagu mutiara, susu, campuran buah segar.</span></li>
        <li><strong>Kemasan</strong><span>Cup plastik bening dan botol, siap makan langsung.</span></li>
        <li><strong>Pemesanan</strong><span>Chat WhatsApp, tanpa minimum yang rumit.</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure class="d-foto">
      {gambar(g["a2_logo"], "Label Fruit Punch by Anyha dengan teks mix fruit, fresh, less sugar")}
    </figure>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label"><span>03</span> Foto</p>
      <h2>Bentuk aslinya.</h2>
      <p>Foto dari pemilik akun, tanpa penyuntingan warna.</p>
    </div>
    <div class="d-dua">
      <figure>
        {gambar(g["a2_cup"], "Dessert cup mangga digenggam, tampak lapisan mangga dan sagu")}
      </figure>
      <figure>
        {gambar(g["a2_punch"], "Botol fruit punch oranye dengan label Fruit Punch by Anyha")}
      </figure>
    </div>
  </div>
</section>"""


def isi_kontak_2():
    return kepala_dalam("01", "Order", "Chat, konfirmasi, ambil.", f"Pesanan lewat WhatsApp {nomor_wa()} atau DM Instagram. Jam buka {jam_buka()}.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="d-grid3">
      <div class="d-kartu">
        <h2>Instagram</h2>
        <p>Cara utama memesan. Kirim menu, jumlah, dan tanggal.</p>
        <p class="d-kecil">{escape(SITE['handle'])}</p>
        {pesan("tombol tombol--garis", "Buka Instagram", ikon=True)}
      </div>
      <div class="d-kartu">
        <h2>WhatsApp</h2>
        <p>Cara tercepat memesan, dibalas di jam buka.</p>
        <p class="d-kecil">{escape(nomor_wa())}</p>
        {pesan("tombol tombol--garis", "Chat WhatsApp")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Buka {escape(jam_buka())}. Bisa diambil langsung atau dikirim.</p>
        <p class="d-kecil">Sebut alamat saat chat, ongkir dibalas pemilik.</p>
      </div>
    </div>
    <div class="d-catatan">
      <p><strong>Jumlah banyak</strong> sebaiknya dipesan sehari sebelumnya.</p>
      {pesan("tombol", "Tanya jadwal")}
    </div>
    <div class="d-dua" style="margin-top:2.5rem">
      <div>
        <p class="label"><span>02</span> Isi chat</p>
        <h2>Supaya balasan langsung berisi total.</h2>
        <ul class="d-daftar">
          <li><strong>Menu</strong><span>Mango Sago, Fruit Punch, atau Asinan Kiamboy</span></li>
          <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
          <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
          <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
        </ul>
      </div>
      <div>
        <p class="label"><span>03</span> Pembayaran</p>
        <h2>Menyusul.</h2>
        <p>Metode pembayaran belum dikirim pemilik. Halaman ini diperbarui begitu informasinya ada.</p>
      </div>
    </div>
  </div>
</section>"""


# ------------------------------------------------------------------ arah 3
def nav_3(aktif):
    def item(kunci, href, teks):
        tanda = ' aria-current="page"' if aktif == kunci else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)
    return pita_mockup() + f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-3/"><strong>{escape(NAMA)}</strong><span>Est. rumahan</span></a>
    <button class="menu-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="menu-tombol__garis" aria-hidden="true"></span>Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {item("menu", "/arah-3/menu/", "Menu")}
        {item("tentang", "/arah-3/tentang/", "Tentang")}
        {item("kontak", "/arah-3/kontak/", "Pesan")}
        <li>{pesan("nav__cta", "Pesan")}</li>
      </ul>
    </nav>
  </div>
</header>"""


def daftar_3(p, g):
    kunci = kunci_foto(p, 3)
    return f"""
      <li>
        <div class="daftar-menu__isi">
          <h3>{escape(p['nama'])}</h3>
          <span class="daftar-menu__harga">{escape(p['harga'])}</span>
        </div>
        <p>{escape(p['deskripsi'])}</p>
        {rincian(p, "rincian-3")}
        <figure class="daftar-menu__foto">
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </figure>
        <a class="tautan-kecil" href="{escape(tautan_pesan(p['nama'] + ' ' + p['harga']))}" target="_blank" rel="noopener">Pesan {escape(p['nama'])}</a>
      </li>"""


def langkah_3():
    langkah = [
        ("Pilih dan chat", "Tentukan menu dan jumlah, lalu kirim pesan lewat WhatsApp."),
        ("Konfirmasi harga", "Pemilik membalas total, ongkir, dan jadwal siap."),
        ("Ambil atau terima", "Pesanan disiapkan hari itu dan sebaiknya langsung disantap dingin."),
    ]
    return "".join(f"""
        <li>
          <span class="langkah__no">{i:02d}</span>
          <div>
            <h3>{escape(j)}</h3>
            <p>{escape(t)}</p>
          </div>
        </li>""" for i, (j, t) in enumerate(langkah, 1))


def arah_3(g):
    return kepala(
        "Mockup Dessert by Anyha, dessert cup mangga",
        DESKRIPSI["beranda"] + " Tiga menu: Mango Sago, Fruit Punch, dan Asinan Kiamboy.",
        "arah-3.css", "#F5F2EA", FONTS[3], "/arah-3/", "favicon-3.png",
    ) + nav_3("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap">
    <p class="kicker">Dessert rumahan</p>
    <h1>Manis yang <em>tenang.</em></h1>
    <p class="hero__p">Dessert cup mangga dan fruit punch, dirakit setelah pesanan masuk. Mangga potong, sagu mutiara, susu, dan campuran buah dengan gula yang lebih ringan.</p>
    <div class="aksi">
      {pesan("tombol", "Pesan lewat WhatsApp", ikon=True)}
      <a class="tombol tombol--garis" href="/arah-3/menu/">Lihat menu</a>
    </div>
    <figure class="hero__foto">
      <div class="tombol-zoom-wrap">
        {gambar(g["a3_hero"], "Dessert cup mangga dengan lapisan susu di atas piring batu, disinari matahari pagi", prioritas=True)}
        <button class="tombol-zoom" type="button" data-zoom="/{g['a3_hero']['berkas']}" data-zoom-alt="Dessert cup mangga dengan lapisan susu" aria-label="Perbesar foto dessert cup">{IKON_ZOOM}</button>
      </div>
    </figure>
  </div>
</section>

<section class="bagian bagian--garis" id="menu">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label">01 / Menu</p>
      <h2>Yang tersedia hari ini.</h2>
      <p>Harga per cup atau botol. Isian lengkap tiap menu ada di bawah.</p>
    </div>
    <ul class="daftar-menu">{semua_kartu(daftar_3, g)}</ul>
  </div>
</section>

<section class="bagian bagian--matcha">
  <div class="wrap cerita">
    <p class="label">02 / Cara kerja</p>
    <h2 style="text-align:center;margin-bottom:1.5rem">Tidak ada stok menganggur.</h2>
    <p>Mangga dipotong setelah pesanan masuk, lalu cup dirakit dan langsung disimpan dingin. Fruit punch diracik dengan takaran gula yang lebih ringan dari minuman buah biasa.</p>
    <p>Karena itu, pesanan jumlah banyak sebaiknya masuk sehari sebelumnya. Untuk pesanan mendadak, tanyakan dulu ketersediaannya.</p>
    <blockquote>Dessert yang paling enak adalah yang baru dirakit.</blockquote>
  </div>
</section>

<section class="bagian">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label">03 / Pesan</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah_3()}</ol>
  </div>
</section>

<section class="cta bagian--matcha">
  <div class="wrap">
    <h2>Mau pesan?</h2>
    <p>Sebutkan menu, jumlah, dan tanggal. Balasan berisi harga dan jadwal siap.</p>
    <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki(3) + tutup()


def halaman_3(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-3.css", "#F5F2EA", FONTS[3], path, "favicon-3.png") + \
        nav_3(aktif) + '<main id="utama">' + isi + "</main>" + kaki(3) + tutup()


def isi_menu_3(g):
    return kepala_dalam("01", "Menu", "Yang tersedia hari ini.", "Tiga menu dengan harga dan isian lengkap.") + f"""
<section class="bagian">
  <div class="wrap">
    <ul class="daftar-menu">{semua_kartu(daftar_3, g)}</ul>
    <div class="d-catatan">
      <p>Pesan lewat WhatsApp, sebutkan menu dan jumlahnya.</p>
      {pesan("tombol", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label">02 / Pesan</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah_3()}</ol>
  </div>
</section>"""


def isi_tentang_3(g):
    return kepala_dalam("01", "Tentang", "Dibuat di rumah, dikirim hari itu.", "Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Sekarang menunya bertambah fruit punch, dengan cara kerja yang sama: dirakit setelah pesanan masuk.") + f"""
<section class="bagian">
  <div class="wrap d-dua">
    <div>
      <p class="label">02 / Bahan</p>
      <h2>Sedikit bahan, dipilih yang manis.</h2>
      <p>Cup berisi mangga potong, sagu mutiara, dan susu. Fruit punch memakai campuran buah segar. Tidak ada pemanis tambahan yang berlebihan, jadi rasanya lebih dekat ke buahnya.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga, sagu mutiara, susu, buah</span></li>
        <li><strong>Kemasan</strong><span>Cup bening dan botol</span></li>
        <li><strong>Pesan</strong><span>Instagram, tanpa aplikasi</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure class="d-foto">
      {gambar(g["a3_punch"], "Botol Fruit Punch oranye dengan label Fruit Punch by Anyha")}
    </figure>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="label">03 / Label</p>
      <h2>Label yang dipakai di botol.</h2>
      <p>Foto dari pemilik akun.</p>
    </div>
    <figure style="max-width:420px;margin-inline:auto">
      {gambar(g["a3_logo"], "Label Fruit Punch by Anyha bertuliskan mix fruit, fresh, less sugar")}
    </figure>
  </div>
</section>"""


def isi_kontak_3():
    return kepala_dalam("01", "Pesan", "Chat, konfirmasi, ambil.", f"Pesanan lewat WhatsApp {nomor_wa()} atau DM Instagram. Jam buka {jam_buka()}.") + f"""
<section class="bagian">
  <div class="wrap wrap--sempit">
    <div class="d-grid3">
      <div class="d-kartu">
        <h2>Instagram</h2>
        <p>Cara utama memesan.</p>
        <p class="d-kecil">{escape(SITE['handle'])}</p>
        {pesan("tombol tombol--garis", "Buka Instagram", ikon=True)}
      </div>
      <div class="d-kartu">
        <h2>WhatsApp</h2>
        <p>Cara tercepat memesan, dibalas di jam buka.</p>
        <p class="d-kecil">{escape(nomor_wa())}</p>
        {pesan("tombol tombol--garis", "Chat WhatsApp")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Buka {escape(jam_buka())}.</p>
        <p class="d-kecil">Sebut alamat saat chat.</p>
      </div>
    </div>
    <div class="d-catatan">
      <p><strong>Jumlah banyak</strong> dipesan sehari sebelumnya.</p>
      {pesan("tombol", "Tanya jadwal")}
    </div>
    <div style="margin-top:2.5rem">
      <p class="label">02 / Isi chat</p>
      <h2 style="font-size:1.5rem;margin-bottom:1rem">Supaya balasan langsung berisi total.</h2>
      <ul class="d-fakta">
        <li><strong>Menu</strong><span>Mango Sago, Fruit Punch, atau Asinan Kiamboy</span></li>
        <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
        <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
        <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
      </ul>
      <p class="d-kecil" style="margin-top:1.5rem">Metode pembayaran menyusul dari pemilik.</p>
    </div>
  </div>
</section>"""


# ------------------------------------------------------------------ arah 4
def nav_4(aktif):
    def item(kunci, href, teks):
        tanda = ' aria-current="page"' if aktif == kunci else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)
    return pita_mockup() + f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-4/"><strong>{escape(NAMA)}</strong><span>Dessert &amp; minuman buah</span></a>
    <button class="menu-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="menu-tombol__garis" aria-hidden="true"></span>Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {item("menu", "/arah-4/menu/", "Menu")}
        {item("tentang", "/arah-4/tentang/", "Tentang")}
        {item("kontak", "/arah-4/kontak/", "Pesan")}
        <li>{pesan("nav__cta", "Pesan Sekarang")}</li>
      </ul>
    </nav>
  </div>
</header>"""


def kartu_4(p, g, nomor=None):
    kunci = kunci_foto(p, 4)
    unggulan = ' produk--favorit' if p["slug"] == "mango-sago" else ""
    label = '<span class="produk__label">Favorit</span>' if unggulan else ""
    return f"""
      <article class="produk{unggulan}">
        <div class="produk__foto">
          {label}
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </div>
        <div class="produk__isi">
          <p class="produk__kategori">{escape(p['label'])}</p>
          <h3>{escape(p['nama'])}</h3>
          <p class="produk__harga">{escape(p['harga'])}</p>
          <p class="produk__ket">{escape(p['deskripsi'])}</p>
          {rincian(p, "rincian-4")}
          <div class="produk__kaki">
            {pesan("tombol", "Pesan " + p['nama'], p["nama"] + " seharga " + p["harga"])}
          </div>
        </div>
      </article>"""


def langkah_4():
    langkah = [
        ("Pilih menunya", "Lihat tiga menu beserta harga dan isiannya, lalu tentukan jumlah."),
        ("Chat WhatsApp", "Sebut menu, jumlah, dan kapan mau diambil atau dikirim."),
        ("Konfirmasi", "Pemilik membalas total dan jadwal siap. Pesanan dirakit setelah itu."),
    ]
    return "".join(f"""
        <li>
          <span class="langkah__no">{i:02d}</span>
          <div>
            <h3>{escape(j)}</h3>
            <p>{escape(t)}</p>
          </div>
        </li>""" for i, (j, t) in enumerate(langkah, 1))


def blok_lokasi():
    alamat = SITE.get("alamat", "")
    return f"""
<section class="bagian bagian--krim2" id="lokasi">
  <div class="wrap">
    <div class="bagian__kepala bagian__kepala--kiri">
      <p class="eyebrow">Lokasi &amp; jam buka</p>
      <h2>Ambil di {escape(alamat)}.</h2>
      <p>Buka setiap hari, {escape(SITE.get('jam_buka', ''))}. Sebelum berangkat, chat dulu lewat WhatsApp {escape(nomor_wa())} supaya pesanan sudah siap.</p>
    </div>
    <div class="lokasi">
      <div class="lokasi__info">
        <ul class="d-fakta">
          <li><strong>Alamat</strong><span>{escape(alamat)}</span></li>
          <li><strong>Jam buka</strong><span>Setiap hari, {escape(SITE.get('jam_buka', ''))}</span></li>
          <li><strong>WhatsApp</strong><span>{escape(nomor_wa())}</span></li>
          <li><strong>Ambil atau kirim</strong><span>Bisa diambil langsung, atau dikirim dengan ongkir dari pemilik.</span></li>
        </ul>
        <div class="aksi">{tombol_maps()}{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
      </div>
      {peta_semat()}
    </div>
  </div>
</section>"""


def arah_4(g):
    return kepala(
        "Mockup Dessert by Anyha, Mango Sago, Fruit Punch, dan Asinan Kiamboy",
        DESKRIPSI["beranda"],
        "arah-4.css", "#FBF7EE", FONTS[4], "/arah-4/", "favicon-4.png",
    ) + nav_4("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="eyebrow">Dessert rumahan, Jambi</p>
      <h1>Segarnya buah,<em>dirakit saat dipesan.</em></h1>
      <p class="hero__p">Mango Sago, Fruit Punch, dan Asinan Kiamboy. Semua diracik setelah pesanan masuk, jadi tidak ada yang menginap di kulkas. Pesan lewat WhatsApp, ambil di Simpang IV Sipin.</p>
      <div class="aksi">
        {pesan("tombol", "Pesan lewat WhatsApp", ikon=True)}
        <a class="tombol tombol--garis" href="#menu">Lihat menu</a>
      </div>
    </div>
    <figure class="hero__foto">
      {gambar(g["a4_hero"], "Mango Sago dengan lapisan mangga dan kuah susu di atas piring batu, disinari matahari pagi", prioritas=True)}
      <button class="tombol-zoom" type="button" data-zoom="/{g['a4_hero']['berkas']}" data-zoom-alt="Mango Sago dengan lapisan susu" aria-label="Perbesar foto Mango Sago">{IKON_ZOOM}</button>
      <figcaption class="stiker">
        <span class="stiker__ikon" aria-hidden="true">A</span>
        <span class="stiker__teks"><strong>Segar, asli, nikmat</strong><span>Tiga menu, satu standar</span></span>
      </figcaption>
      <figcaption class="stiker stiker--kanan"><span class="stiker__teks"><strong>Dibuat saat dipesan</strong><span>Bukan stok kulkas</span></span></figcaption>
    </figure>
  </div>
</section>

<div class="strip">
  <div class="wrap">
    <ul>
      <li>Mangga potong asli</li>
      <li>Sagu mutiara</li>
      <li>Buah segar</li>
      <li>Dirakit per pesanan</li>
    </ul>
  </div>
</div>

<section class="bagian" id="menu">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Menu &amp; harga</p>
      <h2>Pilih yang paling kamu suka.</h2>
      <p>Harga per cup atau botol. Isian lengkap tiap menu ada di kartunya, supaya tidak perlu tanya dulu.</p>
    </div>
    <div class="produk-grid">{semua_kartu(kartu_4, g)}</div>
  </div>
</section>

<section class="bagian bagian--putih">
  <div class="wrap dua">
    <div>
      <p class="eyebrow">Tentang</p>
      <h2>Ketika buah segar bertemu kuah yang pas.</h2>
      <p>Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Sekarang menunya bertambah fruit punch dan asinan kiamboy, dengan cara kerja yang sama: dirakit setelah pesanan masuk.</p>
      <p>Mangga dipotong hari itu, sagu dimasak sampai kenyal, dan kuah susu diracik dengan gula yang lebih ringan supaya rasa buahnya tetap terasa.</p>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure>
      {gambar(g["a4_cerita"], "Asinan Kiamboy dalam cup bening berisi potongan buah dan kuah")}
      <figcaption class="stiker stiker--kanan"><span class="stiker__teks"><strong>Asinan Kiamboy</strong><span>Segar, manis, pedas, asin, gurih</span></span></figcaption>
    </figure>
  </div>
</section>

<section class="bagian bagian--krim2">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Kenapa Anyha</p>
      <h2>Bukan sekadar minuman buah.</h2>
    </div>
    <div class="unggul-grid">
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">01</span>
        <h3>Buah dipotong hari itu</h3>
        <p>Tidak ada buah yang disiapkan berhari-hari sebelumnya, karena itu rasanya masih segar saat sampai.</p>
      </div>
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">02</span>
        <h3>Gula lebih ringan</h3>
        <p>Kuah susu dan jus diracik dengan takaran gula yang tidak menutupi rasa buahnya.</p>
      </div>
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">03</span>
        <h3>Dirakit per pesanan</h3>
        <p>Pesanan disiapkan setelah chat masuk, jadi tidak ada stok menganggur di kulkas.</p>
      </div>
    </div>
  </div>
</section>

<section class="bagian bagian--putih">
  <div class="wrap dua--proses">
    <div>
      <p class="eyebrow">Cara pesan</p>
      <h2>Tiga langkah, lewat WhatsApp.</h2>
      <ol class="langkah" style="margin-top:1.75rem">{langkah_4()}</ol>
    </div>
    <figure>
      {gambar(g["a4_proses"], "Mango Sago digenggam, tampak lapisan mangga dan sagu mutiara")}
    </figure>
  </div>
</section>
{blok_lokasi()}

<section class="cta">
  <div class="wrap cta__isi">
    <p class="eyebrow">Saatnya pesan</p>
    <h2>Segarnya bikin pesan lagi.</h2>
    <p>Sebut menu, jumlah, dan tanggal. Balasan berisi total dan jadwal siap.</p>
    <div class="aksi">{pesan("tombol tombol--putih", "Pesan lewat WhatsApp", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki(4) + tutup()


def halaman_4(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-4.css", "#FBF7EE", FONTS[4], path, "favicon-4.png") + \
        nav_4(aktif) + '<main id="utama">' + isi + "</main>" + kaki(4) + tutup()


def isi_menu_4(g):
    return kepala_dalam("01", "Menu", "Tiga menu, harga jelas.", "Harga per cup atau botol. Isian lengkap di tiap kartu.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="produk-grid">{semua_kartu(kartu_4, g)}</div>
    <div class="d-catatan">
      <p><strong>Pesan lewat Instagram.</strong> Sebutkan menu, jumlah, dan tanggal ambil atau kirim.</p>
      {pesan("tombol", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--putih">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Cara pesan</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah_4()}</ol>
  </div>
</section>"""


def isi_tentang_4(g):
    return kepala_dalam("01", "Tentang", "Dibuat di rumah, dirakit saat dipesan.", "Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Cara kerjanya tetap sama: dirakit setelah pesanan masuk.") + f"""
<section class="bagian">
  <div class="wrap dua">
    <div>
      <p class="eyebrow">Cara kerja</p>
      <h2>Tidak ada stok menganggur.</h2>
      <p>Mangga dipotong setelah pesanan masuk, lalu cup dirakit dan langsung disimpan dingin. Fruit punch diracik dari jus dan irisan buah, dan asinan kiamboy memakai kuah segar berasa manis, pedas, asin, dan gurih.</p>
      <p>Pesanan jumlah banyak sebaiknya masuk sehari sebelumnya, supaya semua bisa disiapkan tepat waktu.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga, sagu mutiara, nata de coco, jus jeruk, nanas, lemon, dan buah segar.</span></li>
        <li><strong>Kemasan</strong><span>Cup plastik bening dan botol, siap disantap langsung.</span></li>
        <li><strong>Lokasi</strong><span>{escape(SITE.get('alamat', ''))}</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure>
      {gambar(g["a4_logo"], "Label Fruit Punch by Anyha bertuliskan mix fruit, fresh, less sugar")}
    </figure>
  </div>
</section>
<section class="bagian bagian--krim2">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Foto produk</p>
      <h2>Seperti ini bentuknya.</h2>
      <p>Foto dari pemilik akun, tanpa penyuntingan warna.</p>
    </div>
    <div class="unggul-grid">
      <figure style="margin:0">
        {gambar(g["a4_cup"], "Mango Sago digenggam, tampak mangga dan sagu mutiara")}
      </figure>
      <figure style="margin:0">
        {gambar(g["a4_punch"], "Botol Fruit Punch oranye dengan label Fruit Punch by Anyha")}
      </figure>
      <figure style="margin:0">
        {gambar(g["a4_asinan"], "Asinan Kiamboy dalam cup bening berisi potongan buah")}
      </figure>
    </div>
  </div>
</section>"""


def isi_kontak_4():
    alamat = SITE.get("alamat", "")
    return kepala_dalam("01", "Pesan", "Chat, konfirmasi, ambil di Sipin.", "Pesanan lewat WhatsApp atau DM Instagram. Lokasi pengambilan di " + escape(alamat) + ".") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="grid3">
      <div class="kartu-info">
        <h2>Instagram</h2>
        <p>Cara utama memesan. Kirim menu, jumlah, dan tanggal.</p>
        <p class="kecil">{escape(SITE['handle'])}</p>
        {pesan("tombol tombol--garis", "Buka Instagram", ikon=True)}
      </div>
      <div class="kartu-info">
        <h2>Lokasi</h2>
        <p>{escape(alamat)}</p>
        <p class="kecil">Buka setiap hari, {escape(SITE.get('jam_buka', ''))}</p>
        {tombol_maps("tombol tombol--garis")}
      </div>
      <div class="kartu-info">
        <h2>Ambil atau kirim</h2>
        <p>Bisa diambil langsung di lokasi, atau dikirim.</p>
        <p class="kecil">Sebutkan alamat saat chat, ongkir dibalas pemilik.</p>
      </div>
    </div>
    <div class="d-catatan">
      <p><strong>Jumlah banyak</strong> sebaiknya dipesan sehari sebelumnya.</p>
      {pesan("tombol", "Tanya jadwal")}
    </div>
    {peta_semat()}
    <div class="dua" style="margin-top:2.75rem">
      <div>
        <p class="eyebrow">Isi chat</p>
        <h2>Supaya balasan langsung berisi total.</h2>
        <ul class="d-fakta">
          <li><strong>Menu</strong><span>Mango Sago, Fruit Punch, atau Asinan Kiamboy</span></li>
          <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
          <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
          <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
        </ul>
      </div>
      <div>
        <p class="eyebrow">Pembayaran</p>
        <h2>Menyusul.</h2>
        <p>Metode pembayaran belum dikirim pemilik. Halaman ini diperbarui begitu informasinya ada, supaya tidak ada janji yang tidak benar.</p>
      </div>
    </div>
  </div>
</section>"""


# ------------------------------------------------------------------ pemilih dan 404
def halaman_pemilih(g):
    arah = [
        {
            "slug": "arah-1", "nomor": "01", "nama": "Mangga Mentega",
            "dial": "Energi 2 / Ritme 2 / Gerak 1",
            "ringkas": "Krem hangat, judul serif lembut, foto produk membulat. Terasa seperti toko kue kecil yang ramah.",
            "cocok": "Cocok kalau ingin terlihat hangat dan ramah, mudah dipercaya ibu-ibu.",
            "palet": [("Krem", "#FBF4E7"), ("Tinta", "#2A1D15"), ("Coklat", "#8A4A12"), ("Mangga", "#F2B45A")],
        },
        {
            "slug": "arah-2", "nomor": "02", "nama": "Pasar Malam",
            "dial": "Energi 4 / Ritme 3 / Gerak 2",
            "ringkas": "Latar hampir hitam, judul kapital raksasa, mangga sebagai lampu. Paling berani di feed Instagram.",
            "cocok": "Cocok kalau ingin tampil beda dan terasa seperti brand, bukan jualan rumahan.",
            "palet": [("Malam", "#14100E"), ("Panel", "#221B16"), ("Krem", "#FFF8EC"), ("Mangga", "#FFB328")],
        },
        {
            "slug": "arah-3", "nomor": "03", "nama": "Washi",
            "dial": "Energi 1 / Ritme 2 / Gerak 1",
            "ringkas": "Kertas washi, serif tipis, hijau matcha dan terakota, hampir tanpa kotak. Tenang dan rapi.",
            "cocok": "Cocok kalau ingin terlihat mahal dan bersih tanpa ramai.",
            "palet": [("Washi", "#F5F2EA"), ("Tinta", "#262B22"), ("Matcha", "#46523A"), ("Terakota", "#8E4318")],
        },
        {
            "slug": "arah-4", "nomor": "04", "nama": "Kebun Buah",
            "dial": "Energi 3 / Ritme 3 / Gerak 2",
            "ringkas": "Krem dan putih berselang-seling, aksen hijau tua dan oranye mangga, eyebrow bergaris, foto berbingkai putih dengan label yang keluar bingkai.",
            "cocok": "Cocok kalau ingin terlihat seperti toko yang sudah mapan, dengan harga dan isian tampil jelas di kartu.",
            "palet": [("Krim", "#FBF7EE"), ("Putih", "#FFFFFF"), ("Hutan", "#123F2A"), ("Mangga", "#E9681C")],
        },
    ]
    kartu = []
    for a in arah:
        swatch = "".join(
            '<li><span class="contoh" style="background:%s" aria-hidden="true"></span>%s <code>%s</code></li>'
            % (escape(w), escape(n), escape(w)) for n, w in a["palet"]
        )
        kartu.append(f"""
      <article class="kartu">
        <p class="kartu__nomor">{a['nomor']}</p>
        <h2>{escape(a['nama'])}</h2>
        <p class="kartu__dial">{escape(a['dial'])}</p>
        <p class="kartu__ringkas">{escape(a['ringkas'])}</p>
        <p class="kartu__cocok">{escape(a['cocok'])}</p>
        <ul class="palet">{swatch}</ul>
        <a class="tombol" href="/{a['slug']}/">Buka mockup {escape(a['nama'])}</a>
      </article>""")
    return kepala(
        "Mockup empat arah desain untuk Dessert by Anyha",
        "Pratinjau empat arah desain situs Dessert by Anyha: Mangga Mentega, Pasar Malam, Washi, dan Kebun Buah. Isi dan foto sama, arah visual berbeda.",
        "pemilih.css", "#F7F1E4", PEMILIH_FONTS, "/", "favicon.png",
    ) + pita_mockup() + f"""
<main id="utama" class="pilih">
  <div class="wrap">
    <p class="kicker">Pratinjau desain</p>
    <h1>Mockup empat arah untuk Dessert by Anyha.</h1>
    <p class="pilih__intro">Isi dan foto sama di keempatnya. Yang berbeda palet, tipografi, susunan bagian, dan cara menonjolkan pemesanan. Pilih satu, lalu arah itu yang dibangun penuh.</p>
    <div class="pilih__grid">{''.join(kartu)}</div>
    <div class="pilih__catatan">
      <div>
        <h2>Yang sama di keempatnya</h2>
        <ul>
          <li>Empat halaman: beranda, menu, tentang, cara pesan.</li>
          <li>Tiga menu dengan harga dan isian lengkap dari pemilik.</li>
          <li>Data menu dan foto berasal dari berkas yang dikirim pemilik.</li>
          <li>Tombol pesan menuju DM Instagram, lokasi di Simpang IV Sipin.</li>
          <li>Nomor WhatsApp dan jam pesanan menunggu konfirmasi pemilik.</li>
        </ul>
        <p>{escape(SITE['catatan_pratinjau'])}</p>
      </div>
      <figure>
        {gambar(g["a3_hero"], "Dessert cup mangga dengan lapisan susu di atas piring batu", prioritas=True)}
      </figure>
    </div>
  </div>
</main>
<footer class="kaki">
  <div class="wrap kaki__isi">
    <p>{escape(NAMA)} / pratinjau desain</p>
    <p><a href="{escape(SITE['instagram'])}" target="_blank" rel="noopener">Instagram {escape(SITE['handle'])}</a></p>
  </div>
</footer>
""" + tutup(False)


def halaman_404():
    return kepala(
        "Halaman tidak ditemukan, Mockup Dessert by Anyha",
        "Halaman yang dicari tidak ada. Kembali ke pratinjau empat arah desain.",
        "pemilih.css", "#F7F1E4", PEMILIH_FONTS, "/404.html", "favicon.png",
    ) + """
<main id="utama" class="pilih">
  <div class="wrap">
    <p class="kicker">404</p>
    <h1>Halaman ini tidak ada.</h1>
    <p class="pilih__intro">Mungkin tautannya salah ketik. Pratinjau desain ada di halaman depan.</p>
    <p><a class="tombol" href="/">Kembali ke pratinjau</a></p>
  </div>
</main>
""" + tutup(False)


# ------------------------------------------------------------------ tulis
def tulis(path, isi):
    tujuan = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(tujuan) or DIST, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(isi)


def salin_aset():
    for nama in ("arah-1.css", "arah-2.css", "arah-3.css", "arah-4.css", "pemilih.css"):
        shutil.copy(os.path.join(ROOT, "assets", "css", nama), os.path.join(DIST, "assets", "css", nama))
    shutil.copy(os.path.join(ROOT, "assets", "js", "site.js"), os.path.join(DIST, "assets", "js", "site.js"))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(os.path.join(DIST, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "assets", "js"), exist_ok=True)

    g = siapkan_gambar()

    tulis("index.html", halaman_pemilih(g))
    tulis("404.html", halaman_404())

    tulis("arah-1/index.html", arah_1(g))
    tulis("arah-1/menu/index.html", halaman_1(
        "menu", "Menu " + USAHA, DESKRIPSI["menu"], "/arah-1/menu/", isi_menu_1(g)))
    tulis("arah-1/tentang/index.html", halaman_1(
        "tentang", "Tentang " + USAHA, DESKRIPSI["tentang"], "/arah-1/tentang/", isi_tentang_1(g)))
    tulis("arah-1/kontak/index.html", halaman_1(
        "kontak", "Cara pesan " + USAHA, DESKRIPSI["kontak"], "/arah-1/kontak/", isi_kontak_1()))

    tulis("arah-2/index.html", arah_2(g))
    tulis("arah-2/menu/index.html", halaman_2(
        "menu", "Menu " + USAHA, DESKRIPSI["menu"], "/arah-2/menu/", isi_menu_2(g)))
    tulis("arah-2/tentang/index.html", halaman_2(
        "tentang", "Cerita " + USAHA, DESKRIPSI["tentang"], "/arah-2/tentang/", isi_tentang_2(g)))
    tulis("arah-2/kontak/index.html", halaman_2(
        "kontak", "Order " + USAHA, DESKRIPSI["kontak"], "/arah-2/kontak/", isi_kontak_2()))

    tulis("arah-3/index.html", arah_3(g))
    tulis("arah-3/menu/index.html", halaman_3(
        "menu", "Menu " + USAHA, DESKRIPSI["menu"], "/arah-3/menu/", isi_menu_3(g)))
    tulis("arah-3/tentang/index.html", halaman_3(
        "tentang", "Tentang " + USAHA, DESKRIPSI["tentang"], "/arah-3/tentang/", isi_tentang_3(g)))
    tulis("arah-3/kontak/index.html", halaman_3(
        "kontak", "Pesan " + USAHA, DESKRIPSI["kontak"], "/arah-3/kontak/", isi_kontak_3()))

    tulis("arah-4/index.html", arah_4(g))
    tulis("arah-4/menu/index.html", halaman_4(
        "menu", "Menu " + USAHA, DESKRIPSI["menu"], "/arah-4/menu/", isi_menu_4(g)))
    tulis("arah-4/tentang/index.html", halaman_4(
        "tentang", "Tentang " + USAHA, DESKRIPSI["tentang"], "/arah-4/tentang/", isi_tentang_4(g)))
    tulis("arah-4/kontak/index.html", halaman_4(
        "kontak", "Pesan " + USAHA, DESKRIPSI["kontak"], "/arah-4/kontak/", isi_kontak_4()))

    salin_aset()

    rute = ["/"]
    for n in (1, 2, 3, 4):
        rute += ["/arah-%d/" % n, "/arah-%d/menu/" % n, "/arah-%d/tentang/" % n, "/arah-%d/kontak/" % n]

    if SITE.get("url"):
        dasar = SITE["url"].rstrip("/")
        halaman_sitemap = "".join(
            "  <url><loc>%s%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>\n"
            % (dasar, r, "1.0" if r == "/" else "0.7") for r in rute)
        tulis("sitemap.xml",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + halaman_sitemap + "</urlset>\n")
        tulis("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % dasar)
    else:
        tulis("robots.txt", "User-agent: *\nAllow: /\n")

    tulis("_headers", "/assets/img/*\n  Cache-Control: public, max-age=604800\n/assets/css/*\n  Cache-Control: public, max-age=0, must-revalidate\n/assets/js/*\n  Cache-Control: public, max-age=0, must-revalidate\n")

    ukuran = jumlah = halaman = 0
    for akar, _d, berkas in os.walk(DIST):
        for b in berkas:
            jumlah += 1
            ukuran += os.path.getsize(os.path.join(akar, b))
            if b.endswith(".html"):
                halaman += 1
    print("halaman: %d" % halaman)
    print("berkas: %d, total %.1f KB" % (jumlah, ukuran / 1024))


if __name__ == "__main__":
    main()
