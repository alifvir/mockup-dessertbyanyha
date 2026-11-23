# DESIGN.md - Dessert by Anyha, tiga arah mockup

Mockup untuk calon klien `@dessertbyanyha`. Tiga arah visual yang sengaja dibuat
berbeda total, supaya pemilik bisa memilih, bukan tiga variasi dari satu tema.

Isi dan foto sama di ketiganya (dessert cup mangga dan Fruit Punch). Yang berubah:
palet, tipografi, susunan bagian, bentuk kartu, dan cara menonjolkan pemesanan.

antislop active: during (global preference).

## Kebutuhan klien

Dessert rumahan yang dijual lewat Instagram. Pengunjung datang dari bio atau
story, jadi yang harus langsung terjawab di layar pertama: ini jualan apa,
terlihat enak atau tidak, dan bagaimana cara memesan.

Karena itu ketiga arah memakai hero foto produk asli, bukan ilustrasi, dan
tombol utama selalu menuju DM Instagram. Harga belum dikirim pemilik, jadi
tidak ada angka yang dipatok.

## Yang belum ada (jangan dikarang)

- Harga per produk.
- Nomor WhatsApp.
- Alamat, jadwal buka, area pengiriman.
- Nama varian lain di luar dua foto yang dikirim.

Semua tempat itu ditulis apa adanya: "Tanya harga", "menyusul", tombol DM.

## Palet dan kontras (dihitung, semua lolos AA)

| Arah | Pasangan | Rasio |
|---|---|---|
| 1 | tinta #2A1D15 di krem #FBF4E7 | 14.94:1 |
| 1 | redup #6E5B4E di krem | 5.87:1 |
| 1 | coklat #8A4A12 di krem | 6.26:1 |
| 1 | tinta di mangga #F2B45A | 8.91:1 |
| 1 | putih di coklat | 6.84:1 |
| 2 | krem #FFF8EC di malam #14100E | 17.92:1 |
| 2 | redup #C0B4A4 di malam | 9.28:1 |
| 2 | mangga #FFB328 di malam | 10.57:1 |
| 2 | malam di mangga | 10.57:1 |
| 3 | tinta #262B22 di washi #F5F2EA | 12.94:1 |
| 3 | redup #606758 di washi | 5.25:1 |
| 3 | matcha #46523A di washi | 7.42:1 |
| 3 | terakota #8E4318 di washi | 6.33:1 |
| 3 | washi di matcha | 7.42:1 |

## Arah 1 - Mangga Mentega

Dial ENERGY 2 / RHYTHM 2 / MOTION 1.

Design read: toko kue kecil yang ramah, bukan kafe kekinian. Krem hangat seperti
kertas roti, judul serif lembut, foto produk besar dengan sudut membulat. Terasa
seperti ditulis tangan di kemasan, bukan template.

| Token | Nilai | Peran |
|---|---|---|
| kertas | #FBF4E7 | latar halaman |
| kartu | #FFFDF8 | panel menu |
| tinta | #2A1D15 | teks utama |
| redup | #6E5B4E | teks penjelas |
| coklat | #8A4A12 | tautan, label, tombol kedua |
| mangga | #F2B45A | pita, sorotan, latar tombol |
| garis | #E4D6C3 | garis rambut |

Fraunces untuk judul, Plus Jakarta Sans untuk teks. Susunan: hero belah dua
dengan foto di kanan dan bidang mangga di belakangnya, dua kartu menu, tiga
langkah pesan, ajakan terakhir berlatar coklat.

## Arah 2 - Pasar Malam

Dial ENERGY 4 / RHYTHM 3 / MOTION 2.

Design read: poster gerobak malam. Latar hampir hitam, judul kapital besar
rapat, mangga sebagai lampu. Paling berani dari ketiganya, cocok kalau pemilik
ingin tampil beda di feed Instagram.

| Token | Nilai | Peran |
|---|---|---|
| malam | #14100E | latar halaman |
| panel | #221B16 | kartu menu, blok isi |
| garis | #3A2E22 | pemisah |
| krem | #FFF8EC | teks utama |
| redup | #C0B4A4 | teks penjelas |
| mangga | #FFB328 | judul sorotan, harga, tombol |

Anton untuk judul, Plus Jakarta Sans untuk teks. Sudut hampir tegak. Susunan:
judul raksasa menimpa foto penuh lebar, pita fakta berjalan, daftar menu berupa
baris besar bergaris, blok cerita, ajakan mangga penuh lebar.

## Arah 3 - Washi

Dial ENERGY 1 / RHYTHM 2 / MOTION 1.

Design read: label kemasan Jepang. Kertas washi, serif tipis, hijau matcha dan
terakota, hampir tanpa kotak. Paling tenang, cocok kalau pemilik ingin terlihat
rapi dan mahal tanpa ramai.

| Token | Nilai | Peran |
|---|---|---|
| washi | #F5F2EA | latar halaman |
| kartu | #FDFCF8 | bidang foto dan panel tipis |
| tinta | #262B22 | teks utama |
| redup | #606758 | teks penjelas |
| matcha | #46523A | panel gelap, tombol utama |
| terakota | #8E4318 | label kecil, nomor, aksen |
| garis | #DED8C9 | garis rambut |

Cormorant Garamond untuk judul, Karla untuk teks. Susunan: hero tengah dengan
foto menyempit di bawahnya, daftar menu dengan titik pemisah seperti daftar
harga kedai, paragraf cerita satu kolom sempit, ajakan tenang berlatar matcha.

## Aturan isi yang dipegang ketiganya

- Satu `h1` per halaman, landmark jelas, tautan lewati isi.
- Tanpa em dash, tanpa emoji, tanpa ikon set hiasan.
- Tanpa harga, testimoni, jumlah pembeli, atau klaim karangan.
- Foto hanya berkas kiriman pemilik, dipotong berbeda per arah.
- Tombol pesan menuju DM Instagram, bukan nomor karangan.
- Tanpa gradien, glass, atau bayangan selain hover tombol.
