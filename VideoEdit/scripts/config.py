# =============================================================
#  TETAPAN VIDEOEDIT — ubah nilai di sini, simpan, dan jalankan semula.
#  (Baris bermula dengan # ialah komen, tidak dibaca oleh script.)
# =============================================================

# ---------- VERTICAL (9:16) ----------
LEBAR = 1080            # lebar video siap (piksel)
TINGGI = 1920           # tinggi video siap (piksel)
FPS = 30                # bingkai sesaat
KABUR_LATAR = 40        # kekuatan blur latar belakang (video landscape). 0 = latar hitam

# ---------- SILENCE (buang senyap) ----------
AMBANG_SENYAP = 0.04    # 0.01–0.10. Lebih tinggi = lebih banyak dibuang dianggap "senyap"
MARGIN_SENYAP = "0.25s" # ruang dikekalkan sebelum/selepas bercakap (elak potong terlalu rapat)

# ---------- SUBTITLE ----------
MODEL_WHISPER = "small" # tiny / base / small / medium / large-v3-turbo
BAHASA = "ms"           # "ms" = Melayu (paling baik untuk video campur BM+English)
                        # "en" = English sahaja; "auto" = kesan sendiri
FONT_FAIL = "Montserrat-Bold.ttf"   # fail dalam assets/fonts/ (cth: "Poppins-Bold.ttf")
FONT_NAMA = "Montserrat"            # nama keluarga font (cth: "Poppins")
SAIZ_SUBTITLE = 80      # saiz huruf (untuk video 1080x1920). 60 = kecil, 100 = besar
TEBAL_OUTLINE = 5       # ketebalan garis hitam
HURUF_BESAR = True      # True = SEMUA HURUF BESAR
MAKS_PERKATAAN = 4      # bilangan perkataan maksimum setiap paparan subtitle
JARAK_BAWAH = 600       # jarak subtitle dari bawah skrin (piksel). Elak kawasan UI TikTok
WARNA_TEKS = "FFFFFF"   # putih (format RRGGBB)
WARNA_OUTLINE = "000000"  # hitam

# ---------- LOGO ----------
LOGO_FAIL = "logo.png"  # fail dalam assets/ (PNG lutsinar paling cantik)
LOGO_LEBAR = 160        # lebar logo dalam piksel (video 1080 lebar)
LOGO_LEGAP = 0.8        # 1.0 = penuh, 0.5 = separuh lutsinar
LOGO_MARGIN = 50        # jarak dari bucu kanan atas (piksel)

# ---------- COMPRESS ----------
SAIZ_MAKS_MB = 95       # sasaran saiz maksimum (bawah had 100MB)
BITRATE_VIDEO_MAKS = 8000  # kbps — had kualiti tertinggi
BITRATE_AUDIO = 128     # kbps
CRF = 21                # kualiti H.264 (18 = sangat tinggi, 23 = biasa)
