# Python CLI VLESS & Trojan Generator

Dashboard CLI berbasis Python untuk berinteraksi dengan Cloudflare Worker VLESS/Trojan Anda. Tool ini memudahkan Anda untuk mengecek server yang tersedia dan membuat konfigurasi akun secara otomatis.

## Fitur

- 🌍 **Cek Region**: Melihat daftar negara dan jumlah IP proxy yang tersedia secara real-time.
- 🏢 **Filter ISP**: Memilih ISP atau Organisasi tertentu dari region yang dipilih.
- ⚡ **Generator Otomatis**: Membuat link akun Trojan, VLESS, dan Shadowsocks dengan mudah.
- ⚙️ **Config Manager**: Menyimpan URL Worker Anda sehingga tidak perlu mengetik ulang.
- 🎨 **Tampilan Menarik**: Menggunakan library `rich` untuk tampilan terminal yang modern.

## Persyaratan

- Python 3.x
- Cloudflare Worker yang sudah terdeploy dengan script VLESS (Backend).

## 📱 Panduan Instalasi (Termux - Android)

Berikut adalah langkah-langkah lengkap untuk menjalankan script ini di Termux:

### 1. Update & Install Python
Buka aplikasi Termux, lalu jalankan perintah berikut satu per satu:

```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

### 2. Clone Repository
Download script ini ke Termux Anda (ganti URL_REPO dengan link github Anda nanti):

```bash
git clone https://github.com/junialdiansyah/free-cf.git
cd free-cf
```

> **Catatan:** Jika Anda belum upload ke GitHub, Anda bisa menyalin folder script ini secara manual ke penyimpanan internal lalu akses dari Termux.

### 3. Install Dependencies
Install library yang dibutuhkan:

```bash
pip install -r free-cf/requirements.txt
```

## 🚀 Cara Menjalankan

Setelah semua terinstall, jalankan script dengan perintah:

```bash
python free-cf/main.py
```

### Konfigurasi Awal
1. Saat pertama kali dijalankan, script akan meminta **Worker URL**.
2. Masukkan URL Worker Anda (contoh: `https://vless.nama-mu.workers.dev`).
3. URL akan disimpan otomatis di `config.json`.

## 🖥️ Instalasi di Windows

1. Pastikan sudah install **Python**.
2. Double click file `run_cli.bat`.
3. Script akan otomatis menginstall requirements dan membuka dashboard.

## Menu Dashboard

1. **Check Available Regions**: Melihat proxy aktif per negara.
2. **Generate Configuration**:
   - Masukkan Bug Host/SNI (Opsional).
   - Pilih Protocol (Trojan/VLESS/SS).
   - Pilih Port (443/80).
   - Pilih Limit jumlah akun.
   - **Pilih Region** (Negara).
   - **Pilih ISP** (Jika memilih spesifik negara).
3. **Check My IP**: Cek info IP koneksi Anda saat ini.
4. **Update Worker URL**: Mengganti target worker.

---
Dibuat dengan ❤️ menggunakan Python & Cloudflare Workers.
