# PANDUAN VideoEdit 🎬

Automasi edit video pendek (TikTok / Reels / Shorts):
**vertical → buang senyap → subtitle → logo → compress**

---

## 📁 Struktur folder

| Folder | Fungsi |
|---|---|
| `input/` | Letak video mentah di sini. **Fail di sini tidak akan diubah atau dipadam.** |
| `output/` | Video siap: `<nama>_siap.mp4` + fail subtitle `<nama>_siap.srt` |
| `assets/` | `logo.png`, folder `fonts/`, muzik, intro/outro |
| `scripts/` | Semua script + **`config.py`** (semua tetapan) |
| `temp/` | Fail sementara. Dipadam sendiri selepas setiap video siap |
| `models/` | Model Whisper (dimuat turun sekali sahaja, ~464MB) |

---

## ⚡ Arahan ringkas

Anda boleh **taip ayat biasa kepada Claude** (lajur tengah), atau **jalankan arahan sendiri** di Terminal dalam folder `VideoEdit` (lajur kanan).

> 💡 Di Windows, guna `python` dan bukan `python3`.

| Apa anda mahu | Taip kepada Claude | Arahan Terminal |
|---|---|---|
| Proses semua video | "proses semua video dalam input" | `python3 scripts/batch.py` |
| Proses satu video sahaja | "proses video raya.mp4 sahaja" | `python3 scripts/batch.py --fail raya.mp4` |
| Proses semula video yang sudah siap | "proses semula semua video" | `python3 scripts/batch.py --semula` |
| Tanpa buang senyap | "proses semua tapi jangan buang senyap" | `python3 scripts/batch.py --langkau silence` |
| Tanpa logo & subtitle | "proses tanpa logo dan subtitle" | `python3 scripts/batch.py --langkau logo,subtitle` |
| Subtitle English | "proses semua, subtitle English" | `python3 scripts/batch.py --bahasa en` |
| Tukar ke 9:16 sahaja | "jadikan video.mp4 vertical" | `python3 scripts/vertical.py input/video.mp4` |
| Buang senyap sahaja | "buang senyap dalam video.mp4" | `python3 scripts/silence.py input/video.mp4` |
| Subtitle sahaja | "letak subtitle kat video.mp4" | `python3 scripts/subtitle.py input/video.mp4` |
| Logo sahaja | "letak logo kat video.mp4" | `python3 scripts/logo.py input/video.mp4` |
| Compress sahaja | "compress video.mp4 untuk upload" | `python3 scripts/compress.py input/video.mp4` |
| Bantuan / pilihan | "apa pilihan untuk batch?" | `python3 scripts/batch.py --help` |

**Nota:**
- Script satu-langkah (vertical, silence, dll.) simpan hasil di `output/<nama>_<langkah>.mp4`.
- Nama langkah untuk `--langkau`: `vertical`, `silence`, `subtitle`, `logo`, `compress`.
- Video yang sudah ada `_siap.mp4` dalam `output/` akan **dilangkau**. Guna `--semula` untuk buat semula.
- Jika satu video gagal, batch teruskan ke video lain. Fail sementara video itu disimpan di `temp/<nama>/` untuk semakan.

---

## 🖼️ Cara tukar LOGO

1. Simpan logo anda sebagai **`assets/logo.png`**. PNG berlatar lutsinar paling cantik.
2. Siap. Batch akan guna logo itu secara automatik.

Laraskan dalam `scripts/config.py`:
```python
LOGO_FAIL = "logo.png"  # nama fail dalam assets/
LOGO_LEBAR = 160        # saiz logo (piksel). Besarkan → 220, kecilkan → 120
LOGO_LEGAP = 0.8        # 1.0 = penuh, 0.5 = separuh lutsinar
LOGO_MARGIN = 50        # jarak dari bucu kanan atas
```
Guna logo lain sekali sahaja (tanpa ubah config):
`python3 scripts/batch.py --logo assets/logo_raya.png`

> Jika `assets/logo.png` tiada, langkah logo dilangkau dengan amaran. Video tetap siap.

---

## 🔤 Cara tukar FONT subtitle

Dua font sudah disediakan dalam `assets/fonts/`: **Montserrat Bold** (lalai) dan **Poppins Bold**.

Tukar ke Poppins dalam `scripts/config.py`:
```python
FONT_FAIL = "Poppins-Bold.ttf"
FONT_NAMA = "Poppins"
```

Untuk guna font lain:
1. Salin fail `.ttf`/`.otf` ke `assets/fonts/`.
2. Tukar `FONT_FAIL` kepada nama fail itu.
3. Tukar `FONT_NAMA` kepada nama keluarga font (cth: `"Bebas Neue"`). Nama keluarga boleh dilihat bila buka fail font itu.

---

## 🔠 Cara tukar SAIZ & gaya subtitle

Dalam `scripts/config.py`:
```python
SAIZ_SUBTITLE = 80      # 60 = kecil, 80 = sederhana, 100 = besar
TEBAL_OUTLINE = 5       # ketebalan garis hitam
HURUF_BESAR = True      # False = huruf biasa
MAKS_PERKATAAN = 4      # perkataan setiap paparan (2–3 = gaya TikTok laju)
JARAK_BAWAH = 600       # naikkan jika subtitle terlindung oleh caption TikTok
WARNA_TEKS = "FFFFFF"   # putih. Kuning = "FFE000"
WARNA_OUTLINE = "000000"
BAHASA = "ms"           # "ms" Melayu (boleh campur English), "en", atau "auto"
MODEL_WHISPER = "small" # "medium" lebih tepat tapi lebih lambat
```

> Fail `.srt` dalam `output/` boleh dibuka dengan Notepad/TextEdit untuk semak ejaan.

---

## ⚙️ Tetapan lain (`scripts/config.py`)

| Tetapan | Lalai | Maksud |
|---|---|---|
| `LEBAR`, `TINGGI`, `FPS` | 1080, 1920, 30 | Saiz & kadar bingkai video siap |
| `KABUR_LATAR` | 40 | Kekuatan blur latar (video landscape). `0` = latar hitam |
| `AMBANG_SENYAP` | 0.04 | Naikkan (0.06) jika banyak bunyi latar; turunkan (0.02) jika suara perlahan terpotong |
| `MARGIN_SENYAP` | "0.25s" | Ruang dikekalkan sekitar percakapan. Besarkan jika potongan terasa terlalu rapat |
| `SAIZ_MAKS_MB` | 95 | Had saiz fail siap |
| `CRF` | 21 | Kualiti (lebih kecil = lebih cantik & besar) |

---

## 💻 Pasang di komputer sendiri (`Documents/VideoEdit`)

1. Salin folder `VideoEdit` ini ke `Documents/`.
2. Pasang **Python 3.10+** dan **ffmpeg**:
   - macOS: `brew install python ffmpeg`
   - Windows: `winget install Python.Python.3.12 Gyan.FFmpeg`
3. Dalam Terminal, di folder `Documents/VideoEdit`:
   ```
   pip install -r requirements.txt
   ```
   Arahan ini memasang `faster-whisper` dan `auto-editor`.
4. Model Whisper (~464MB) dimuat turun sendiri ke `models/` kali pertama subtitle dijana.
5. Letak video dalam `input/` dan jalankan `python3 scripts/batch.py`.

---

## 🛠️ Masalah biasa

| Masalah | Penyelesaian |
|---|---|
| `'ffmpeg' tidak dijumpai` | Pasang ffmpeg (lihat di atas), kemudian buka Terminal baru |
| `'auto-editor' tidak dijumpai` | `pip install auto-editor` |
| Subtitle salah ejaan | Guna `MODEL_WHISPER = "medium"`, atau pastikan `BAHASA` betul |
| Subtitle terlindung caption TikTok | Naikkan `JARAK_BAWAH` (cth: 750) |
| Potongan senyap terlalu agresif | Turunkan `AMBANG_SENYAP` atau besarkan `MARGIN_SENYAP` |
| Fail siap > 100MB | Turunkan `SAIZ_MAKS_MB`. Script akan ulang secara automatik jika terlebih |
| Proses lambat | Normal untuk CPU. Subtitle paling lama (~1x tempoh video dengan model `small`) |
