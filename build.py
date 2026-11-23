"""Build tiga arah mockup Dessert by Anyha.

Sumber:
  data/site.json    identitas, tautan Instagram, catatan pratinjau
  data/menu.json    produk dan isinya (harga belum dikirim pemilik)
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

FONTS = {
    1: "family=Fraunces:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700",
    2: "family=Anton&family=Plus+Jakarta+Sans:wght@400;500;700",
    3: "family=Cormorant+Garamond:ital,wght@0,300;0,500;1,400&family=Karla:wght@400;500;700",
}
PEMILIH_FONTS = "family=Fraunces:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700"

DESKRIPSI = {
    "beranda": "Dessert cup mangga dan fruit punch buatan rumahan dari Dessert by Anyha. Lihat menunya, lalu pesan lewat Instagram.",
    "menu": "Menu Dessert by Anyha: dessert cup mangga dan fruit punch. Pesan lewat Instagram.",
    "tentang": "Cerita Dessert by Anyha, dessert rumahan yang diracik per pesanan.",
    "kontak": "Cara pesan Dessert by Anyha lewat Instagram dan area pengiriman yang menyusul.",
}

IKON_IG = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
    '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="12" cy="12" r="4.4" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="17.6" cy="6.6" r="1.2" fill="currentColor"/></svg>'
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


def pesan(kelas, teks, produk=None, ikon=False):
    isi = (IKON_IG + " ") if ikon else ""
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s%s</a>' % (
        kelas, escape(tautan_pesan(produk)), isi, teks)


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


def logo_putar(nama, sisi, latar=(253, 251, 244), mutu=86):
    """Logo kiriman pemilik tersimpan miring 90 derajat, jadi teks Fruit Punch
    terbaca kalau kepalanya dimiringkan. Diputar searah jarum jam dulu, lalu
    dipangkas ke isi labelnya supaya tidak menyisakan margin putih besar."""
    im = sumber(nama).rotate(-90, expand=True)

    # pangkas margin putih: cari kotak piksel yang bukan hampir putih
    kecil = im.convert("L").resize((im.width // 4, im.height // 4), Image.LANCZOS)
    kotak = kecil.point(lambda v: 255 if v < 235 else 0).getbbox()
    if kotak:
        k = 4
        tepi = 12
        im = im.crop((
            max(0, kotak[0] * k - tepi), max(0, kotak[1] * k - tepi),
            min(im.width, kotak[2] * k + tepi), min(im.height, kotak[3] * k + tepi),
        ))

    # kanvas persegi berwarna latar section, jadi logo tidak terlihat sebagai kartu
    kanvas = Image.new("RGB", (im.width + 80, im.height + 80), latar)
    kanvas.paste(im, (40, 40))
    return kanvas.resize((sisi, sisi), Image.LANCZOS)


def siapkan_gambar():
    if os.path.isdir(IMG):
        shutil.rmtree(IMG)
    os.makedirs(IMG, exist_ok=True)
    hasil = {}

    cup_sun = sumber_bersih("mango-cup-sunlit.jpeg", 0.09)
    cup_hand = sumber("mango-cup-hand.jpeg")
    cup_dim = sumber("mango-cup-dim.jpeg")
    punch = sumber("fruit-punch.jpeg")
    logo = sumber("logo-anyha.jpeg")

    hasil["a1_hero"] = webp(potong(cup_sun, 4 / 5, 0.5).resize((900, 1125), Image.LANCZOS), "a1-hero.webp")
    hasil["a1_cup"] = webp(potong(cup_hand, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-cup.webp")
    hasil["a1_punch"] = webp(potong(punch, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-punch.webp")
    hasil["a1_cup_dim"] = webp(potong(cup_dim, 4 / 5, 0.5).resize((800, 1000), Image.LANCZOS), "a1-cup-dim.webp")
    hasil["a1_logo"] = webp(logo_putar("logo-anyha.jpeg", 520, (255, 253, 248)), "a1-logo.webp")
    hasil["a2_logo"] = webp(logo_putar("logo-anyha.jpeg", 520, (34, 27, 22)), "a2-logo.webp")

    hasil["a2_panggung"] = webp(potong(cup_sun, 16 / 9, 0.5).resize((1600, 900), Image.LANCZOS), "a2-panggung.webp", 82)
    hasil["a2_cup"] = webp(potong(cup_hand, 1, 0.5).resize((360, 360), Image.LANCZOS), "a2-cup.webp")
    hasil["a2_punch"] = webp(potong(punch, 1, 0.5).resize((360, 360), Image.LANCZOS), "a2-punch.webp")
    hasil["a2_panggung_menu"] = webp(potong(cup_dim, 16 / 9, 0.5).resize((1600, 900), Image.LANCZOS), "a2-panggung-menu.webp", 82)

    hasil["a3_hero"] = webp(potong(cup_sun, 16 / 10, 0.5).resize((1440, 900), Image.LANCZOS), "a3-hero.webp")
    hasil["a3_cup"] = webp(potong(cup_hand, 1, 0.5).resize((640, 640), Image.LANCZOS), "a3-cup.webp")
    hasil["a3_punch"] = webp(potong(punch, 1, 0.5).resize((640, 640), Image.LANCZOS), "a3-punch.webp")
    hasil["a3_cup_dim"] = webp(potong(cup_dim, 3 / 4, 0.5).resize((720, 960), Image.LANCZOS), "a3-cup-dim.webp")
    hasil["a3_logo"] = webp(logo_putar("logo-anyha.jpeg", 480, (253, 252, 248)), "a3-logo.webp")

    og = potong(cup_sun, 1200 / 630, 0.45).resize((1200, 630), Image.LANCZOS)
    og.save(os.path.join(IMG, "og.jpg"), "JPEG", quality=84, optimize=True, progressive=True)

    hasil["og"] = {"berkas": "assets/img/og.jpg", "w": 1200, "h": 630}

    # favicon tiga arah: huruf A dengan warna latar berbeda
    for nama, warna, tinta in (
        ("favicon.png", (251, 244, 231), (42, 29, 21)),
        ("favicon-2.png", (20, 16, 14), (255, 179, 40)),
        ("favicon-3.png", (245, 242, 234), (70, 82, 58)),
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
    muat = 'load="eager" ' if prioritas else ""
    if lazy and not prioritas:
        muat = 'loading="lazy" decoding="async" '
    return '<img src="/%s" alt="%s" width="%d" height="%d" %s%s>' % (
        d["berkas"], escape(alt), d["w"], d["h"],
        muat, ('fetchpriority="high" decoding="async" ' if prioritas else ""))


# ------------------------------------------------------------------ kepala dan kaki
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
<meta property="og:site_name" content="Dessert by Anyha">
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
                  'aria-label="Pesan lewat Instagram Dessert by Anyha">%s</a>\n'
                  % (escape(tautan_pesan()), IKON_IG))
    return f"""
{tombol}<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def kaki(gaya):
    isi = f"""
<footer class="kaki">
  <div class="wrap kaki__{'grid' if gaya == 1 else 'isi'}">
    <div>
      <strong>Dessert by Anyha</strong>
      <p>Dessert rumahan dari mangga pilihan dan campuran buah segar. Pesanan lewat Instagram.</p>
    </div>
    <div>
      <ul>
        <li><a href="/arah-{gaya}/menu/">Menu</a></li>
        <li><a href="/arah-{gaya}/tentang/">Tentang</a></li>
        <li><a href="/arah-{gaya}/kontak/">Cara pesan</a></li>
        <li><a href="{escape(SITE['instagram'])}" target="_blank" rel="noopener">Instagram {escape(SITE['handle'])}</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap kaki__bawah">
    <span>&copy; 2026 Dessert by Anyha.</span>
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
    return f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-1/">
      <strong>Dessert by Anyha</strong>
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
    tag = "".join("<li>%s</li>" % escape(t) for t in p["isi"])
    kunci = "a1_cup" if p["slug"] == "mango-cup" else "a1_punch"
    return f"""
      <article class="kartu">
        <div class="kartu__foto">
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </div>
        <div class="kartu__isi">
          <p class="kartu__label">{escape(p['label'])}</p>
          <h3>{escape(p['nama'])}</h3>
          <p>{escape(p['deskripsi'])}</p>
          <ul class="tag">{tag}</ul>
          <div class="kartu__kaki">
            <span>Harga menyusul</span>
            {pesan("tautan-kecil", "Tanya harga", p["nama"])}
          </div>
        </div>
      </article>"""


def langkah_1():
    langkah = [
        ("Pilih menunya", "Lihat dua menu yang tersedia, lalu tentukan jumlahnya."),
        ("Chat Instagram", "Kirim pesan berisi menu, jumlah, dan tanggal ambil atau kirim."),
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
        "Dessert by Anyha, dessert cup mangga rumahan",
        DESKRIPSI["beranda"] + " Dua menu: Mango Dessert Cup dan Fruit Punch.",
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
        {pesan("tombol", "Pesan lewat Instagram", ikon=True)}
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
        <h2>Dua menu, satu rasa dasar: manis yang tidak berlebihan.</h2>
      </div>
      <p>Harga belum ditampilkan karena menunggu daftar resmi dari pemilik. Tanyakan lewat Instagram, balasannya cepat.</p>
    </div>
    <div class="menu-grid">{kartu_1(MENU[0], g)}{kartu_1(MENU[1], g)}</div>
  </div>
</section>

<section class="bagian bagian--garis" id="cara">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>02</span> Cara pesan</p>
        <h2>Tiga langkah, lewat chat Instagram.</h2>
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
      {pesan("tombol tombol--mangga", "Chat Instagram", ikon=True)}
    </div>
  </div>
</section>
</main>
""" + kaki(1) + tutup()


def halaman_1(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-1.css", "#FBF4E7", FONTS[1], path, "favicon.png") + \
        nav_1(aktif) + '<main id="utama">' + isi + "</main>" + kaki(1) + tutup()


def isi_menu_1(g):
    return kepala_dalam("01", "Menu", "Menu hari ini.", "Dua menu yang tersedia. Harga menyusul dari pemilik, tanyakan lewat Instagram untuk daftar terbaru.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="menu-grid">{kartu_1(MENU[0], g)}{kartu_1(MENU[1], g)}</div>
    <div class="d-catatan">
      <p><strong>Pesan lewat Instagram.</strong> Sebutkan menu, jumlah, dan tanggal.</p>
      {pesan("tombol", "Chat Instagram", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--garis">
  <div class="wrap">
    <div class="bagian__kepala">
      <div>
        <p class="label"><span>02</span> Cara pesan</p>
        <h2>Tiga langkah, lewat chat Instagram.</h2>
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
      <p>Karena itu, pesanan sebaiknya masuk sehari sebelum mau diambil. Untuk jumlah banyak, tanyakan lebih awal lewat Instagram.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga potong, sagu mutiara, susu, campuran buah segar.</span></li>
        <li><strong>Kemasan</strong><span>Cup plastik bening dan botol, siap makan langsung.</span></li>
        <li><strong>Pemesanan</strong><span>Lewat chat Instagram, tanpa minimum yang rumit.</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat Instagram", ikon=True)}</div>
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
        {gambar(g["a1_cup_dim"], "Dessert cup mangga di dalam ruangan, tampak atas mangga dan susu")}
      </figure>
    </div>
  </div>
</section>"""


def isi_kontak_1():
    return kepala_dalam("01", "Cara pesan", "Chat, konfirmasi, lalu ambil atau kirim.", "Semua pesanan diproses lewat Instagram. Belum ada nomor WhatsApp khusus website, jadi tombol di halaman ini menuju DM Instagram.") + f"""
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
        <p>Nomor khusus website menyusul dari pemilik.</p>
        <p class="d-kecil">Sementara ini semua pesanan lewat Instagram.</p>
        {pesan("tombol tombol--garis", "Chat Instagram")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Area pengiriman dan jam ambil menyusul dari pemilik.</p>
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
          <li><strong>Menu</strong><span>Mango Dessert Cup atau Fruit Punch</span></li>
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
    return f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-2/"><strong>Anyha</strong><span>Dessert</span></a>
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
    tag = "".join("<li>%s</li>" % escape(t) for t in p["isi"])
    kunci = "a2_cup" if p["slug"] == "mango-cup" else "a2_punch"
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
            <ul class="baris-menu__tag">{tag}</ul>
          </div>
          <div class="baris-menu__kanan">
            <span class="baris-menu__harga">Harga menyusul</span>
            <a class="tautan-kecil" href="{escape(tautan_pesan(p['nama']))}" target="_blank" rel="noopener">Pesan</a>
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
        "Dessert by Anyha, dessert cup mangga dan fruit punch",
        DESKRIPSI["beranda"] + " Pesan lewat Instagram.",
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
      <h2>Dua barang.</h2>
      <p>Harga menyusul dari pemilik. Chat untuk daftar harga terbaru, balasannya cepat.</p>
    </div>
    <ul class="baris-menu">{baris_menu_2(MENU[0], g, 1)}{baris_menu_2(MENU[1], g, 2)}</ul>
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
    <div class="aksi">{pesan("tombol", "Chat Instagram", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki(2) + tutup()


def halaman_2(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-2.css", "#14100E", FONTS[2], path, "favicon-2.png") + \
        nav_2(aktif) + '<main id="utama">' + isi + "</main>" + kaki(2) + tutup()


def isi_menu_2(g):
    return kepala_dalam("01", "Menu", "Dua barang, harga menyusul.", "Daftar ini yang tersedia sekarang. Harga belum dikirim pemilik, jadi chat untuk daftar terbaru.") + f"""
<section class="bagian">
  <div class="wrap">
    <ul class="baris-menu">{baris_menu_2(MENU[0], g, 1)}{baris_menu_2(MENU[1], g, 2)}</ul>
    <div class="d-catatan">
      <p>Pesan lewat Instagram, sebutkan menu dan jumlahnya.</p>
      {pesan("tombol", "Chat Instagram", ikon=True)}
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
        <li><strong>Pemesanan</strong><span>Chat Instagram, tanpa minimum yang rumit.</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat Instagram", ikon=True)}</div>
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
    return kepala_dalam("01", "Order", "Chat, konfirmasi, ambil.", "Semua pesanan lewat Instagram. Nomor WhatsApp khusus website belum ada, jadi tombol di sini menuju DM Instagram.") + f"""
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
        <p>Nomor khusus website menyusul.</p>
        <p class="d-kecil">Sementara semua pesanan lewat Instagram.</p>
        {pesan("tombol tombol--garis", "Chat Instagram")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Area pengiriman dan jam ambil menyusul dari pemilik.</p>
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
          <li><strong>Menu</strong><span>Mango Dessert Cup atau Fruit Punch</span></li>
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
    return f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/arah-3/"><strong>Dessert by Anyha</strong><span>Est. rumahan</span></a>
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
    tag = "".join("<li>%s</li>" % escape(t) for t in p["isi"])
    kunci = "a3_cup" if p["slug"] == "mango-cup" else "a3_punch"
    return f"""
      <li>
        <div class="daftar-menu__isi">
          <h3>{escape(p['nama'])}</h3>
          <span class="daftar-menu__harga">Harga menyusul</span>
        </div>
        <p>{escape(p['deskripsi'])}</p>
        <ul class="daftar-menu__tag">{tag}</ul>
        <figure class="daftar-menu__foto">
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </figure>
        <a class="tautan-kecil" href="{escape(tautan_pesan(p['nama']))}" target="_blank" rel="noopener">Tanya harga lewat Instagram</a>
      </li>"""


def langkah_3():
    langkah = [
        ("Pilih dan chat", "Tentukan menu dan jumlah, lalu kirim pesan lewat Instagram."),
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
        "Dessert by Anyha, dessert cup mangga",
        DESKRIPSI["beranda"] + " Dua menu: Mango Dessert Cup dan Fruit Punch.",
        "arah-3.css", "#F5F2EA", FONTS[3], "/arah-3/", "favicon-3.png",
    ) + nav_3("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap">
    <p class="kicker">Dessert rumahan</p>
    <h1>Manis yang <em>tenang.</em></h1>
    <p class="hero__p">Dessert cup mangga dan fruit punch, dirakit setelah pesanan masuk. Mangga potong, sagu mutiara, susu, dan campuran buah dengan gula yang lebih ringan.</p>
    <div class="aksi">
      {pesan("tombol", "Pesan lewat Instagram", ikon=True)}
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
      <p>Harga belum ditampilkan karena menunggu daftar resmi dari pemilik. Tanyakan lewat Instagram.</p>
    </div>
    <ul class="daftar-menu">{daftar_3(MENU[0], g)}{daftar_3(MENU[1], g)}</ul>
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
    <div class="aksi">{pesan("tombol", "Chat Instagram", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki(3) + tutup()


def halaman_3(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, "arah-3.css", "#F5F2EA", FONTS[3], path, "favicon-3.png") + \
        nav_3(aktif) + '<main id="utama">' + isi + "</main>" + kaki(3) + tutup()


def isi_menu_3(g):
    return kepala_dalam("01", "Menu", "Yang tersedia hari ini.", "Dua menu, harga menyusul dari pemilik. Tanyakan lewat Instagram untuk daftar terbaru.") + f"""
<section class="bagian">
  <div class="wrap">
    <ul class="daftar-menu">{daftar_3(MENU[0], g)}{daftar_3(MENU[1], g)}</ul>
    <div class="d-catatan">
      <p>Pesan lewat Instagram, sebutkan menu dan jumlahnya.</p>
      {pesan("tombol", "Chat Instagram", ikon=True)}
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
      <div class="aksi">{pesan("tombol", "Chat Instagram", ikon=True)}</div>
    </div>
    <figure class="d-foto">
      {gambar(g["a3_cup_dim"], "Dessert cup mangga di dalam ruangan, tampak atas mangga dan susu")}
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
    return kepala_dalam("01", "Pesan", "Chat, konfirmasi, ambil.", "Semua pesanan lewat Instagram. Nomor WhatsApp khusus website belum ada, jadi tombol di halaman ini menuju DM Instagram.") + f"""
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
        <p>Nomor khusus website menyusul.</p>
        <p class="d-kecil">Sementara lewat Instagram.</p>
        {pesan("tombol tombol--garis", "Chat Instagram")}
      </div>
      <div class="d-kartu">
        <h2>Ambil atau kirim</h2>
        <p>Area dan jam menyusul dari pemilik.</p>
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
        <li><strong>Menu</strong><span>Mango Dessert Cup atau Fruit Punch</span></li>
        <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
        <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
        <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
      </ul>
      <p class="d-kecil" style="margin-top:1.5rem">Metode pembayaran menyusul dari pemilik.</p>
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
        "Tiga arah desain untuk Dessert by Anyha",
        "Pratinjau tiga arah desain situs Dessert by Anyha: Mangga Mentega, Pasar Malam, dan Washi. Isi dan foto sama, arah visual berbeda.",
        "pemilih.css", "#F7F1E4", PEMILIH_FONTS, "/", "favicon.png",
    ) + f"""
<main id="utama" class="pilih">
  <div class="wrap">
    <p class="kicker">Pratinjau desain</p>
    <h1>Tiga arah untuk Dessert by Anyha.</h1>
    <p class="pilih__intro">Isi dan foto sama di ketiganya. Yang berbeda palet, tipografi, susunan bagian, dan cara menonjolkan pemesanan. Pilih satu, lalu arah itu yang dibangun penuh.</p>
    <div class="pilih__grid">{''.join(kartu)}</div>
    <div class="pilih__catatan">
      <div>
        <h2>Yang sama di ketiganya</h2>
        <ul>
          <li>Empat halaman: beranda, menu, tentang, cara pesan.</li>
          <li>Data menu dan foto berasal dari berkas yang dikirim pemilik.</li>
          <li>Tombol pesan menuju DM Instagram.</li>
          <li>Harga dan nomor WhatsApp menunggu konfirmasi pemilik.</li>
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
    <p>Dessert by Anyha / pratinjau desain</p>
    <p><a href="{escape(SITE['instagram'])}" target="_blank" rel="noopener">Instagram {escape(SITE['handle'])}</a></p>
  </div>
</footer>
""" + tutup(False)


def halaman_404():
    return kepala(
        "Halaman tidak ditemukan, Dessert by Anyha",
        "Halaman yang dicari tidak ada. Kembali ke pratinjau tiga arah desain.",
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
    for nama in ("arah-1.css", "arah-2.css", "arah-3.css", "pemilih.css"):
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
        "menu", "Menu Dessert by Anyha", DESKRIPSI["menu"] + " Harga menyusul.", "/arah-1/menu/", isi_menu_1(g)))
    tulis("arah-1/tentang/index.html", halaman_1(
        "tentang", "Tentang Dessert by Anyha", DESKRIPSI["tentang"], "/arah-1/tentang/", isi_tentang_1(g)))
    tulis("arah-1/kontak/index.html", halaman_1(
        "kontak", "Cara pesan Dessert by Anyha", DESKRIPSI["kontak"], "/arah-1/kontak/", isi_kontak_1()))

    tulis("arah-2/index.html", arah_2(g))
    tulis("arah-2/menu/index.html", halaman_2(
        "menu", "Menu Dessert by Anyha", DESKRIPSI["menu"] + " Harga menyusul.", "/arah-2/menu/", isi_menu_2(g)))
    tulis("arah-2/tentang/index.html", halaman_2(
        "tentang", "Cerita Dessert by Anyha", DESKRIPSI["tentang"], "/arah-2/tentang/", isi_tentang_2(g)))
    tulis("arah-2/kontak/index.html", halaman_2(
        "kontak", "Order Dessert by Anyha", DESKRIPSI["kontak"], "/arah-2/kontak/", isi_kontak_2()))

    tulis("arah-3/index.html", arah_3(g))
    tulis("arah-3/menu/index.html", halaman_3(
        "menu", "Menu Dessert by Anyha", DESKRIPSI["menu"] + " Harga menyusul.", "/arah-3/menu/", isi_menu_3(g)))
    tulis("arah-3/tentang/index.html", halaman_3(
        "tentang", "Tentang Dessert by Anyha", DESKRIPSI["tentang"], "/arah-3/tentang/", isi_tentang_3(g)))
    tulis("arah-3/kontak/index.html", halaman_3(
        "kontak", "Pesan Dessert by Anyha", DESKRIPSI["kontak"], "/arah-3/kontak/", isi_kontak_3()))

    salin_aset()

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
