# Dessert by Anyha - tiga arah mockup

Pratinjau desain untuk calon klien `@dessertbyanyha` (dessert cup mangga dan fruit
punch). Tiga arah visual, isi dan foto sama, supaya pemilik bisa memilih satu.

Setiap arah 4 halaman: beranda, menu, tentang, cara pesan. Plus halaman pemilih di
`/` dan `404.html`. Total 14 halaman.

Belum situs final. Harga, nomor WhatsApp, area kirim, dan jam pesanan masih
menunggu pemilik (lihat "Yang menunggu klien").

## Tiga arah

| Arah | Nama | Tipografi | Ciri |
|---|---|---|---|
| `/arah-1/` | Mangga Mentega | Fraunces | krem hangat, kartu membulat, foto dengan bingkai mangga |
| `/arah-2/` | Pasar Malam | Anton | latar hampir hitam, judul raksasa, pita fakta, baris menu besar |
| `/arah-3/` | Washi | Cormorant Garamond | kertas washi, serif tipis, daftar gaya kedai, panel matcha |

Alasan tiap arah, palet, dan kontras terukur ada di `DESIGN.md`.

## Perintah

```bash
pip install -r requirements.txt
python build.py
python tools/audit.py          # harus berakhir: masalah: 0
python tools/serve.py 8125     # pratinjau http://127.0.0.1:8125
```

Pratinjau wajib lewat server, bukan `file://`, karena semua path aset absolut.
Hentikan server sebelum `python build.py`: Windows tidak mengizinkan `dist/`
dihapus saat sedang dipakai.

## Struktur

```
build.py              generator 14 halaman + potong gambar + favicon + OG
data/site.json        identitas, tautan Instagram, catatan pratinjau
data/menu.json        dua produk, isi, dan alt foto
assets/css/           arah-1.css, arah-2.css, arah-3.css, pemilih.css
assets/js/site.js     menu mobile dan lightbox foto
assets-src/           foto asli kiriman pemilik (tidak ikut build)
tools/audit.py        pemeriksaan hasil build
tools/serve.py        pratinjau lokal dengan 404 kustom
tools/cek.js          skrip pemeriksaan geometri di browser (dipakai agent-browser)
pratinjau/            tangkapan layar desktop dan HP
dist/                 hasil build, diabaikan git
```

## Cara mengubah isi

- Produk, isi, dan alt foto: `data/menu.json`, lalu build. Ketiga arah membaca
  berkas yang sama.
- Tautan Instagram dan pesan pembuka chat: `data/site.json` pada kunci `dm` dan
  `wa_pesan`. Selama `wa` kosong, semua tombol menuju `ig.me/m/dessertbyanyha`.
  Begitu nomor WhatsApp dikirim pemilik, isi `wa` dengan `https://wa.me/62...`
  dan semua tombol ikut pindah tanpa menyentuh `build.py`.
- Teks per arah ada di `build.py`: `nav_1` sampai `nav_3`, `isi_menu_*`,
  `isi_tentang_*`, `isi_kontak_*`, lalu `arah_1` sampai `arah_3`.
- Foto: ganti berkas di `assets-src/` dengan nama yang sama, lalu build. Nama
  berkas webp ikut berubah kalau sumbernya berubah, jadi pengunjung lama tidak
  melihat foto lama.

Catatan foto: berkas `mango-cup-sunlit.jpeg` membawa watermark generator AI di
sudut bawah. `build.py` memotong 9 persen bagian bawah sebelum dipotong ke rasio,
supaya watermark tidak ikut tampil. Kalau pemilik mengirim foto tanpa watermark,
hapus `sumber_bersih(...)` jadi `sumber(...)`.

## Hasil uji 23 November 2026

- Build bersih: 14 halaman, 39 berkas, sekitar 606 KB.
- `tools/audit.py`: 0 masalah.
- 70 kombinasi halaman dan lebar layar (14 halaman x 1440, 1024, 768, 390, 320):
  nol overflow horizontal, nol target sentuh di bawah 44 px, semua gambar termuat,
  satu `h1` per halaman, font termuat.
- Menu mobile: terbuka, `aria-expanded` berubah, tertutup lewat Escape.
- Lightbox: terbuka dengan gambar 900 px, tertutup lewat Escape.
- Semua tombol pesan: `https://ig.me/m/dessertbyanyha`, `target=_blank`, `rel=noopener`.
- Rute: semua 200 kecuali `/404` dan path ngawur yang memakai halaman 404 sendiri.
- Kontras: 24 pasangan diukur di `DESIGN.md`, semua lolos AA 4.5:1.

## Yang menunggu klien

1. Harga Mango Dessert Cup dan Fruit Punch.
2. Nomor WhatsApp khusus pesanan.
3. Area pengiriman atau pengambilan, dan jam pesanan.
4. Metode pembayaran dan ketentuan DP.
5. Menu lain di luar dua yang ada di foto (kalau ada).
6. Foto tanpa watermark untuk hero arah 1, 2, dan 3.
7. Arah mana yang dipilih.

## Deploy

Sudah live: https://dessertbyanyha.pages.dev

Repo: `alifvir/dessertbyanyha` (publik, branch `main`). Proyek Cloudflare Pages
`dessertbyanyha` dibuat lewat Connect to Git, jadi setiap push ke `main` langsung
membangun ulang. Setelan yang dipakai:

- Build command: `pip install -r requirements.txt && python build.py`
- Build output directory: `dist`
- Branch: `main`

`dist/` diabaikan git karena Pages membangunnya sendiri. `data/site.json` sudah
memuat `url`, jadi canonical, `og:url`, dan `sitemap.xml` ikut dibuat tiap build.
Kalau domain klien ditambahkan nanti, ganti `url` lalu build dan push.
