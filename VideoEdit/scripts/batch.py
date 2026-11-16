"""BATCH: proses SEMUA video dalam input/ sekali gus.
Urutan: vertical → silence → subtitle → logo → compress
Hasil: output/<nama>_siap.mp4 (+ <nama>_siap.srt). Fail asal dalam input/ TIDAK diubah.

Guna:  python3 scripts/batch.py                 # semua video dalam input/
       python3 scripts/batch.py --fail a.mp4    # satu video sahaja
       python3 scripts/batch.py --langkau silence,logo
       python3 scripts/batch.py --semula        # proses semula walaupun sudah siap
"""
import argparse
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compress
import logo
import silence
import subtitle
import vertical
from common import INPUT, OUTPUT, TEMP, VIDEO_EXT, info, log, semak_alat

LANGKAH = [("vertical", vertical), ("silence", silence), ("subtitle", subtitle),
           ("logo", logo), ("compress", compress)]


def proses_satu(src, langkau, bahasa, fail_logo):
    nama = src.stem
    kerja = TEMP / nama
    shutil.rmtree(kerja, ignore_errors=True)
    kerja.mkdir(parents=True)
    akhir = OUTPUT / f"{nama}_siap.mp4"
    semasa = src                                  # fail asal hanya DIBACA
    for n, (lk, modul) in enumerate(LANGKAH, 1):
        if lk in langkau:
            log(f"[{n}/5] {lk}: dilangkau")
            continue
        log(f"[{n}/5] {lk}...")
        seterusnya = kerja / f"{n}_{lk}.mp4"
        if lk == "subtitle":
            modul.proses(semasa, seterusnya, bahasa=bahasa,
                         srt_keluar=akhir.with_suffix(".srt"))
        elif lk == "logo":
            modul.proses(semasa, seterusnya, logo=fail_logo)
        else:
            modul.proses(semasa, seterusnya)
        semasa = seterusnya
    if semasa == src:
        shutil.copyfile(src, akhir)
    else:
        shutil.move(str(semasa), akhir)
    shutil.rmtree(kerja, ignore_errors=True)    # padam fail sementara
    return akhir


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--fail", nargs="*", help="nama fail tertentu dalam input/ (lalai: semua)")
    ap.add_argument("--langkau", default="", help="langkah dilangkau, cth: silence,logo")
    ap.add_argument("--bahasa", choices=["ms", "en", "auto"], default=None,
                    help="bahasa subtitle (lalai: ikut config.py)")
    ap.add_argument("--logo", help="fail logo lain (lalai: assets/logo.png)")
    ap.add_argument("--semula", action="store_true", help="proses semula video yang sudah siap")
    a = ap.parse_args()

    semak_alat("ffmpeg", "ffprobe", "auto-editor")
    langkau = {x.strip() for x in a.langkau.split(",") if x.strip()}
    salah = langkau - {n for n, _ in LANGKAH}
    if salah:
        sys.exit(f"Langkah tidak dikenali: {', '.join(salah)}")
    OUTPUT.mkdir(exist_ok=True)
    TEMP.mkdir(exist_ok=True)

    if a.fail:
        video = [INPUT / Path(f).name for f in a.fail]
    else:
        video = sorted(p for p in INPUT.iterdir()
                       if p.is_file() and p.suffix.lower() in VIDEO_EXT and not p.name.startswith("."))
    if not video:
        log("Tiada video dalam input/. Letak video mentah di sana dahulu.")
        return

    berjaya, gagal_, dilangkau = [], [], []
    for k, src in enumerate(video, 1):
        print(f"\n===== [{k}/{len(video)}] {src.name} =====", flush=True)
        if not src.exists():
            log(f"✖ Tidak dijumpai: {src}")
            gagal_.append(src.name)
            continue
        if (OUTPUT / f"{src.stem}_siap.mp4").exists() and not a.semula:
            log("Sudah siap sebelum ini — langkau (guna --semula untuk proses semula)")
            dilangkau.append(src.name)
            continue
        t0 = time.time()
        try:
            out = proses_satu(src, langkau, a.bahasa, a.logo)
            i = info(out)
            log(f"✔ Siap dalam {time.time() - t0:.0f}s → output/{out.name} "
                f"({i['lebar']}x{i['tinggi']}, {i['tempoh']:.1f}s, {out.stat().st_size / 1e6:.1f}MB)")
            berjaya.append(src.name)
        except SystemExit:
            log(f"✖ Gagal: {src.name} (fail sementara disimpan di temp/{src.stem}/ untuk semakan)")
            gagal_.append(src.name)

    print("\n===== RINGKASAN =====")
    print(f"✔ Berjaya : {len(berjaya)}")
    if dilangkau:
        print(f"↷ Dilangkau: {len(dilangkau)} (sudah siap)")
    if gagal_:
        print(f"✖ Gagal   : {len(gagal_)} → {', '.join(gagal_)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
