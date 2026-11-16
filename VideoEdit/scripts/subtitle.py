"""SUBTITLE: jana subtitle automatik (Bahasa Melayu / English) dan burn-in ke video.
Gaya: huruf besar, putih, outline hitam, tengah-bawah (elak UI TikTok).
Fail .srt juga disimpan di sebelah video keluar.

Guna:  python3 scripts/subtitle.py input/video.mp4 [output/hasil.mp4] [--bahasa ms|en|auto]
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import config as C
from common import (FONTS, MODELS, TEMP, X264_TEMP, ffmpeg, gagal, info, laluan_keluar, log,
                    semak_alat)


# ---------- Transkripsi ----------
def muat_model():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        gagal("faster-whisper belum dipasang:  pip install faster-whisper")
    lokal = MODELS / f"whisper-{C.MODEL_WHISPER}"
    if not (lokal / "model.bin").exists():
        log(f"Muat turun model Whisper '{C.MODEL_WHISPER}' (sekali sahaja)...")
        from faster_whisper import download_model
        download_model(C.MODEL_WHISPER, output_dir=str(lokal))
        shutil.rmtree(lokal / ".cache", ignore_errors=True)
    return WhisperModel(str(lokal), device="auto", compute_type="int8")


def baca_audio(path):
    """Nyahkod audio ke 16kHz mono float32 guna ffmpeg (tak bergantung pada PyAV)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path),
                        "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        gagal(f"Gagal baca audio: {r.stderr.decode(errors='ignore')[-500:]}")
    return np.frombuffer(r.stdout, dtype=np.float32)


def transkrip(model, path, bahasa):
    audio = baca_audio(path)
    opsyen = dict(word_timestamps=True, vad_filter=True, beam_size=5,
                  vad_parameters=dict(min_silence_duration_ms=400))
    segs, inf = model.transcribe(audio, language=bahasa, **opsyen)
    if bahasa is None:
        # Hadkan kepada Melayu atau English sahaja. (Indonesia dikira sebagai Melayu,
        # kerana Whisper selalu tersilap kesan BM sebagai 'id'.)
        p = dict(inf.all_language_probs or [])
        p_ms = p.get("ms", 0) + p.get("id", 0)
        p_en = p.get("en", 0)
        pilih = "ms" if p_ms >= p_en else "en"
        log(f"Kesan auto: Melayu {p_ms:.0%} / English {p_en:.0%} → guna '{pilih}'")
        if inf.language != pilih:
            segs, inf = model.transcribe(audio, language=pilih, **opsyen)
    log(f"Bahasa subtitle: {inf.language}")
    kata = []
    for s in segs:
        for w in (s.words or []):
            t = w.word.strip()
            if not t:
                continue
            if kata and not w.word.startswith(" ") and not kata[-1][2].endswith((".", ",", "!", "?")):
                # sambungan perkataan sebelumnya (token tanpa jarak), cth "VIDE" + "O"
                s0, _, t0 = kata[-1]
                kata[-1] = (s0, w.end, t0 + t)
            else:
                # had 1.5s setiap perkataan — elak subtitle muncul terlalu awal/lama
                kata.append((max(w.start, w.end - 1.5), w.end, t))
    return kata


def pecah_baris(kata):
    """Kumpul perkataan jadi paparan pendek (gaya TikTok)."""
    bahagian, cur = [], []
    for i, (s, e, t) in enumerate(kata):
        if cur and (len(cur) >= C.MAKS_PERKATAAN or s - cur[-1][1] > 0.6):
            bahagian.append(cur)
            cur = []
        cur.append((s, e, t))
        if re.search(r"[.!?]$", t) or (t.endswith(",") and len(cur) >= 2):
            bahagian.append(cur)
            cur = []
    if cur:
        bahagian.append(cur)
    hasil = []
    for k, b in enumerate(bahagian):
        mula, tamat = b[0][0], b[-1][1]
        if k + 1 < len(bahagian):
            seterusnya = bahagian[k + 1][0][0]
            if seterusnya - tamat < 0.4:
                tamat = seterusnya          # elak subtitle berkelip
        teks = " ".join(t for _, _, t in b)
        teks = re.sub(r"[.,]+$", "", teks)  # buang noktah/koma hujung
        if C.HURUF_BESAR:
            teks = teks.upper()
        hasil.append((mula, max(tamat, mula + 0.3), teks))
    return hasil


# ---------- Fail subtitle ----------
def masa_srt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def masa_ass(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02}:{cs // 100 % 60:02}.{cs % 100:02}"


def warna_ass(rrggbb):
    r, g, b = rrggbb[0:2], rrggbb[2:4], rrggbb[4:6]
    return f"&H00{b}{g}{r}".upper()


def tulis_srt(baris, path):
    with open(path, "w", encoding="utf-8") as f:
        for n, (s, e, t) in enumerate(baris, 1):
            f.write(f"{n}\n{masa_srt(s)} --> {masa_srt(e)}\n{t}\n\n")


def tulis_ass(baris, path, W, H):
    skala = W / 1080
    saiz = round(C.SAIZ_SUBTITLE * skala)
    outline = round(C.TEBAL_OUTLINE * skala)
    margin_v = round(C.JARAK_BAWAH * H / 1920)
    margin_lr = round(110 * skala)   # elak butang tepi kanan TikTok
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTok,{C.FONT_NAMA},{saiz},{warna_ass(C.WARNA_TEKS)},&H000000FF,{warna_ass(C.WARNA_OUTLINE)},&H80000000,-1,0,0,0,100,100,0,0,1,{outline},2,2,{margin_lr},{margin_lr},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for s, e, t in baris:
            t = t.replace("{", "(").replace("}", ")")
            f.write(f"Dialogue: 0,{masa_ass(s)},{masa_ass(e)},TikTok,,0,0,0,,{t}\n")


# ---------- Proses ----------
_model = None


def proses(inp, out, bahasa=C.BAHASA, srt_keluar=None):
    global _model
    bahasa = bahasa or C.BAHASA
    if bahasa in (None, "auto"):
        bahasa = None
    inp, out = Path(inp).resolve(), Path(out).resolve()
    if not (FONTS / C.FONT_FAIL).exists():
        gagal(f"Font tidak dijumpai: assets/fonts/{C.FONT_FAIL}")
    i = info(inp)
    if not i["ada_audio"]:
        log("Tiada audio — langkau subtitle (salin sahaja)")
        shutil.copyfile(inp, out)
        return out

    if _model is None:
        log(f"Muat model Whisper '{C.MODEL_WHISPER}'...")
        _model = muat_model()
    log("Transkripsi audio (mungkin ambil masa)...")
    baris = pecah_baris(transkrip(_model, inp, bahasa))
    log(f"{len(baris)} baris subtitle dijana")

    kerja = TEMP / f"sub_{inp.stem}"
    kerja.mkdir(parents=True, exist_ok=True)
    tulis_ass(baris, kerja / "sub.ass", i["lebar"], i["tinggi"])
    srt = Path(srt_keluar) if srt_keluar else out.with_suffix(".srt")

    if not baris:
        log("Tiada percakapan dikesan — video disalin tanpa subtitle")
        shutil.copyfile(inp, out)
        srt = None
    else:
        tulis_srt(baris, srt)
        # guna laluan relatif supaya tiada masalah aksara khas dalam filter ffmpeg
        fontsdir = os.path.relpath(FONTS, kerja).replace("\\", "/")
        vf = f"subtitles=sub.ass:fontsdir='{fontsdir}'"
        ffmpeg(["-i", inp, "-vf", vf, *X264_TEMP, "-c:a", "copy",
                "-movflags", "+faststart", out], cwd=kerja)
    shutil.rmtree(kerja, ignore_errors=True)
    if srt:
        log(f"Fail SRT: {srt}")
    return out


if __name__ == "__main__":
    import argparse
    semak_alat("ffmpeg", "ffprobe")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--bahasa", choices=["ms", "en", "auto"], default=None,
                    help="bahasa subtitle (lalai: ikut config.py)")
    a = ap.parse_args()
    out = laluan_keluar(a.input, "subtitle", a.output)
    proses(a.input, out, a.bahasa)
    log(f"Siap: {out}")
