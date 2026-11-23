# DEPLOY.md - repo GitHub dan Cloudflare Pages

> Baca saat: user bilang "deploy github dan pages.dev", "push ke github",
> "deploy ulang", atau "situsnya belum update".

Dokumen ini memuat semua yang sudah terbukti jalan untuk proyek ini. Kalau ada
yang bertentangan dengan kenyataan di mesin, yang menang adalah hasil perintah,
bukan dokumen ini. Perbarui dokumen ini setiap kali ada yang berubah.

## 1. Keadaan sekarang (23 November 2026)

| Hal | Nilai |
|---|---|
| Folder kerja | `D:\Alif\Project\UMKM\dessertbyanyha\web` |
| Repo GitHub | https://github.com/alifvir/dessertbyanyha (publik, branch `main`) |
| Proyek Pages | `dessertbyanyha` |
| URL live | https://dessertbyanyha.pages.dev |
| Jenis proyek Pages | Connect to Git (BUKAN Direct Upload) |
| Akun Cloudflare | `alifvir78@gmail.com`, account id `6974ed1876aaf81ed6adbc30ae874fde` |
| Akun GitHub | `alifvir` |

Setelan build proyek Pages:

| Kolom | Isi |
|---|---|
| Framework preset | None |
| Build command | `pip install -r requirements.txt && python build.py` |
| Build output directory | `dist` |
| Root directory | kosong |
| Production branch | `main` |

## 2. Alur normal: revisi lalu deploy

Ini yang dipakai 95 persen waktu. Tidak perlu membuka dashboard Cloudflare.

```powershell
cd D:\Alif\Project\UMKM\dessertbyanyha\web

python build.py
python tools\audit.py          # wajib berakhir: masalah: 0

git add -A
git commit -F <berkas-pesan>
git push
```

`git push` ke `main` = rilis. Pages membangun ulang otomatis, biasanya selesai
di bawah satu menit.

Pesan commit ditulis ke berkas lalu dipakai dengan `-F`, karena heredoc gaya
bash tidak jalan di PowerShell. Berkas pesan harus tanpa BOM:

```powershell
$f = "C:\Users\ASUS\AppData\Local\Temp\pesan-commit.txt"
[IO.File]::WriteAllText($f, $pesan, (New-Object Text.UTF8Encoding($false)))
git commit -F $f
```

Kalau `Set-Content -Encoding UTF8` dipakai di PowerShell 5.1, BOM ikut masuk dan
judul commit tampil sebagai `﻿Isi url`. BOM tidak merusak situs, tapi terlihat
sebagai sampah di riwayat. Pakai `UTF8Encoding($false)` seperti di atas.

## 3. Kalau harus membuat repo dan proyek dari nol

Hanya perlu kalau repo atau proyeknya dihapus. Kredensial tersimpan di mesin ini,
jadi tidak ada langkah klik manual.

### 3a. Kredensial yang tersedia (terverifikasi)

- **GitHub**: kredensial HTTPS tersimpan di Git Credential Manager, akun
  `alifvir`. Cek tanpa menampilkan token:

  ```powershell
  $env:GCM_INTERACTIVE="never"; $env:GIT_TERMINAL_PROMPT="0"
  "protocol=https`nhost=github.com`n`n" | git credential fill
  ```

  Keluaran berisi `username=alifvir` dan baris `password=`. Jangan pernah
  menyalin baris password ke laporan, chat, atau berkas.

- **Cloudflare**: token OAuth wrangler di
  `%APPDATA%\xdg.config\.wrangler\config\default.toml` (kunci `oauth_token`).
  Scope-nya sudah termasuk `pages:write` dan `account:read`.

  Catatan: token ini TIDAK bisa diverifikasi lewat
  `/client/v4/user/tokens/verify` (selalu 401 karena itu endpoint untuk API
  token, bukan OAuth). Jangan simpulkan token rusak dari 401 di sana. Uji
  dengan perintah yang benar-benar dipakai, misalnya daftar proyek Pages.

### 3b. Membuat repo GitHub

```powershell
cd D:\Alif\Project\UMKM\dessertbyanyha\web
gh repo create alifvir/dessertbyanyha --public --description "Mockup tiga arah situs Dessert by Anyha"
```

`gh` butuh `GH_TOKEN`. Ambil dari kredensial tersimpan, jangan dari ingatan:

```powershell
$cred  = "protocol=https`nhost=github.com`n`n" | git credential fill
$token = ($cred -split "`n" | Where-Object { $_ -like "password=*" }) -replace "^password=", ""
$env:GH_TOKEN = $token
```

Lalu sambungkan dan push:

```powershell
git remote remove origin 2>$null
git remote add origin https://github.com/alifvir/dessertbyanyha.git
git branch -M main
$env:GIT_TERMINAL_PROMPT="0"
git push -u origin main
```

Bukti push berhasil: `git ls-remote origin -h refs/heads/main` harus sama persis
dengan `git rev-parse HEAD`. Jangan percaya kalimat "sudah dipush" tanpa ini.

### 3c. Membuat proyek Pages yang terhubung ke Git

**Jangan** memakai `wrangler pages deploy` atau dashboard "Upload assets".
Keduanya menghasilkan proyek Direct Upload yang selamanya tidak bisa dihubungkan
ke repo. Kalau itu terjadi, satu-satunya perbaikan adalah membuat proyek baru.

Cara yang terbukti: Pages API dengan `source.type = github`. Butuh `repo_id`
dari GitHub, bukan hanya nama repo:

```powershell
# repo id
$env:GH_TOKEN = $token
gh api repos/alifvir/dessertbyanyha --jq '.id'
```

Lalu POST ke API (isi `repo_id` hasil di atas, dan nama proyek = subdomain):

```powershell
$c   = Get-Content "$env:APPDATA\xdg.config\.wrangler\config\default.toml" -Raw
$tok = ([regex]::Match($c,'oauth_token\s*=\s*"([^"]+)"')).Groups[1].Value
$acc = "6974ed1876aaf81ed6adbc30ae874fde"
$h   = @{ Authorization = "Bearer $tok"; "Content-Type" = "application/json" }

$body = @{
  name = "dessertbyanyha"
  production_branch = "main"
  source = @{
    type = "github"
    config = @{
      owner = "alifvir"; repo_name = "dessertbyanyha"; repo_id = "1468395671"
      production_branch = "main"
      pr_comments_enabled = $false
      deployments_enabled = $true
      production_deployments_enabled = $true
      preview_deployment_setting = "all"
      preview_branch_includes = @("*"); preview_branch_excludes = @()
      path_includes = @("*"); path_excludes = @()
    }
  }
  build_config = @{
    build_command = "pip install -r requirements.txt && python build.py"
    destination_dir = "dist"; root_dir = ""
  }
  deployment_configs = @{
    production = @{ compatibility_date = "2026-11-23"; build_image_major_version = 3; usage_model = "standard"; fail_open = $true; always_use_latest_compatibility_date = $false; compatibility_flags = @(); env_vars = $null }
    preview    = @{ compatibility_date = "2026-11-23"; build_image_major_version = 3; usage_model = "standard"; fail_open = $true; always_use_latest_compatibility_date = $false; compatibility_flags = @(); env_vars = $null }
  }
} | ConvertTo-Json -Depth 8

Invoke-RestMethod -Method Post `
  -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects" `
  -Headers $h -Body $body -ContentType "application/json"
```

Cek nama subdomain dulu sebelum memilih nama proyek, karena `pages.dev` unik
lintas akun Cloudflare:

```powershell
try { [System.Net.Dns]::GetHostAddresses("dessertbyanyha.pages.dev") | Out-Null; "SUDAH DIPAKAI" } catch { "kosong" }
```

Kalau nama sudah dipakai, Cloudflare menambahkan akhiran acak, dan URL tidak
bisa dijanjikan. Proyek Pages juga **tidak bisa di-rename**.

### 3d. Build pertama

Proyek baru kadang belum punya deployment. Picu satu:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects/dessertbyanyha/deployments" `
  -Headers $h -Body "{}"
```

## 4. Memantau dan membuktikan deploy

Jangan berhenti di "push sukses". Buktikan Pages selesai membangun commit yang
benar, lalu buktikan isinya naik.

### 4a. Status build

```powershell
$d = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects/dessertbyanyha/deployments" -Headers $h
$d.result[0] | Select-Object `
  @{n="commit";e={$_.deployment_trigger.metadata.commit_hash.Substring(0,7)}},
  @{n="stage"; e={$_.latest_stage.name}},
  @{n="status";e={$_.latest_stage.status}}
```

Yang ditunggu: `stage=deploy`, `status=success`, dan hash commit sama dengan
`git rev-parse --short HEAD`. Hash yang berbeda berarti build masih versi lama.

### 4b. Isi live

Status 200 tidak membuktikan apa pun, karena versi lama juga 200. Uji frasa yang
hanya ada di revisi baru:

```powershell
$u = "https://dessertbyanyha.pages.dev"
foreach ($p in @("/","/arah-1/","/arah-2/","/arah-3/","/arah-1/menu/","/arah-3/tentang/","/sitemap.xml","/robots.txt","/404","/path-ngawur-xyz")) {
  "$(curl.exe -s -o NUL -w '%{http_code}' --max-time 25 "$u$p") $p"
}
```

Harapan: semua 200 kecuali dua path terakhir. `/404` dan path ngawur membalas
404 tetapi tetap memakai halaman 404 milik situs.

Untuk perubahan berupa nama atau teks, cek isinya langsung:

```powershell
$c = (Invoke-WebRequest "$u/arah-2/" -UseBasicParsing).Content
($c -match [regex]::Escape("Mockup Dessert by Anyha"))   # harus True
($c -match 'rel="canonical"')                             # harus True
```

Untuk perubahan berupa penghapusan, cari frasa yang HILANG. Status 200 dan
sitemap tetap sama seperti versi lama, jadi keduanya tidak membuktikan apa pun.

### 4c. Jebakan verifikasi

- `Invoke-WebRequest` bawaan PowerShell bisa lambat atau menggantung pada halaman
  besar. Pakai `curl.exe` untuk status, dan `Invoke-WebRequest` hanya untuk
  membaca isi satu halaman.
- Default User-Agent `urllib` diblokir Cloudflare dengan 403 yang terlihat
  seperti situs mati. Itu bot protection, bukan deploy gagal.
- 308 pada `/404.html` atau path tanpa garis miring akhir adalah redirect
  trailing-slash Cloudflare, normal.

## 5. Berkas yang dipakai build di host

Build host hanya butuh ini, dan semuanya harus ter-commit:

```
build.py
requirements.txt
data/site.json
data/menu.json
assets/css/*.css
assets/js/site.js
assets-src/*.jpeg
tools/audit.py         (tidak dipakai host, tapi ikut untuk pemeriksaan lokal)
```

Yang TIDAK ikut dan memang diabaikan `.gitignore`:

```
dist/                  host membangunnya sendiri
pratinjau/             tangkapan layar kerja, 6.9 MB
.wrangler/             cache CLI
__pycache__/
```

`assets-src/` wajib ter-commit. Tanpa foto sumber, `build.py` gagal di host pada
langkah Pillow.

### Uji build dari clone bersih

Lakukan sebelum push kalau ada berkas baru, karena build lokal bisa lulus
sementara host gagal akibat berkas yang lupa di-commit:

```powershell
$tmp = "$env:TEMP\uji-desserbyanyha"
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
git clone -q "D:\Alif\Project\UMKM\dessertbyanyha\web" $tmp
cd $tmp
python build.py
python tools\audit.py        # harus masalah: 0
```

Clone bersih TIDAK membuktikan dependency host lengkap, karena modul yang sudah
terpasang lokal ikut dipakai. Cocokkan import pihak ketiga di `build.py` dengan
`requirements.txt`. Saat ini hanya `Pillow`.

## 6. Domain sendiri (kalau nanti diminta)

Proyek Pages sudah Git-connected, jadi menambah domain tidak mengubah setelan
build.

1. Cloudflare Dashboard: Workers & Pages > `dessertbyanyha` > Custom domains >
   Set up a custom domain.
2. Isi `url` di `data/site.json` dengan domain baru, lalu `python build.py`.
3. Push. Canonical, `og:url`, dan `sitemap.xml` ikut berubah otomatis.
4. Tunggu sertifikat aktif, lalu ulangi pemeriksaan bagian 4b dengan domain baru.

## 7. Melamar klien memilih arah

Setelah klien memilih satu arah, langkahnya:

1. Hapus dua folder `arah-*` lain dari `build.py` dan dari `dist/`, atau arahkan
   `/` langsung ke arah terpilih.
2. Isi `wa` di `data/site.json` dengan `https://wa.me/62...` begitu nomor ada.
   Semua tombol ikut pindah tanpa menyentuh `build.py`.
3. Ganti `catatan_pratinjau` dan buang `pita_mockup()` dari build, karena
   situsnya bukan mockup lagi.
4. Ganti `nama` di `data/site.json` dari "Mockup Dessert by Anyha" kembali ke
   "Dessert by Anyha".
5. Build, audit, push.

## 8. Ringkasan perintah yang paling sering dipakai

```powershell
cd D:\Alif\Project\UMKM\dessertbyanyha\web
python build.py
python tools\audit.py
python tools\serve.py 8125 0.0.0.0     # pratinjau lokal, HP di WiFi sama boleh buka
git add -A
git commit -F <berkas-pesan-tanpa-BOM>
git push
```

Status cepat tanpa mengubah apa pun:

```powershell
git status -sb
git log --oneline -3
```

## 9. Riwayat deploy

| Commit | Isi | Status Pages |
|---|---|---|
| `fb08d28` | Mockup awal, 14 halaman | success |
| `f761f49` | Isi url + sitemap | success |
| `58735d2` | Perbaiki `loading="eager"` | success |
| `b6972a0` | Dokumentasi repo dan URL | success |
