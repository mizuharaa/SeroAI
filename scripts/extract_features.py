import os
import sys
import csv
import argparse
import pathlib
from typing import Dict, Iterable, Tuple

# Make project importable when running from scripts/
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import analyze_media  # type: ignore


VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}


def is_video_file(path: str) -> bool:
    name = os.path.basename(path).lower()
    ext = os.path.splitext(name)[1]
    if ext not in VIDEO_EXTS:
        return False
    # Skip obvious temp or incomplete files
    bad_tokens = ("tmp", ".temp", ".partial", ".crdownload", "~", ".ds_store")
    if any(t in name for t in bad_tokens):
        return False
    try:
        if os.path.getsize(path) < 20_000:  # < 20KB likely not a valid video
            return False
    except Exception:
        return False
    return True


def iter_labeled_files(root_real: str, root_fake: str) -> Iterable[Tuple[str, int]]:
    for dirpath, _, files in os.walk(root_real):
        for f in files:
            fp = os.path.join(dirpath, f)
            if is_video_file(fp):
                yield fp, 0
    for dirpath, _, files in os.walk(root_fake):
        for f in files:
            fp = os.path.join(dirpath, f)
            if is_video_file(fp):
                yield fp, 1


def build_features_row(video_path: str, label: int) -> Dict:
    r = analyze_media(video_path)
    # Flatten to stable columns
    quality = r.get("quality", {}) or {}
    # Forensics, face_dynamics, and artifact_analysis are at top level (not in debug)
    forensic = r.get("forensics", {}) or {}
    dyn = r.get("face_dynamics", {}) or {}
    arts = r.get("artifact_analysis", {}) or {}
    # Temporal is also at top level
    temporal = r.get("temporal", {}) or {}
    flow = (temporal or {}).get("flow", {}) or {}
    rppg = (temporal or {}).get("rppg", {}) or {}

    row = {
        "id": os.path.basename(video_path),
        "path": os.path.relpath(video_path, start=str(ROOT)),
        "label": label,
        # quality
        "quality.blur": quality.get("blur"),
        "quality.brisque": quality.get("brisque"),
        "quality.bitrate": quality.get("bitrate"),
        "quality.shake": quality.get("shake"),
        # watermark (boolean already in debug shortcut)
        "wm.detected": (r.get("debug", {}) or {}).get("watermark_detected"),
        # forensics
        "forensics.prnu": forensic.get("prnu_score"),
        "forensics.flicker": forensic.get("flicker_score"),
        "forensics.codec": forensic.get("codec_score"),
        # face dynamics
        "face.mouth_exag": dyn.get("mouth_exaggeration_score"),
        "face.mouth_static": dyn.get("mouth_static_score"),
        "face.eye_blink": dyn.get("eye_blink_anomaly"),
        "face.sym_drift": dyn.get("face_symmetry_drift"),
        # artifacts
        "art.edge": arts.get("edge_artifact_score"),
        "art.texture": arts.get("texture_inconsistency"),
        "art.color": arts.get("color_anomaly_score"),
        "art.freq": arts.get("freq_artifact_score"),
        # temporal
        "temp.flow_oddity": flow.get("oddity_score"),
        "temp.rppg": rppg.get("rppg_score"),
    }
    return row


def main():
    ap = argparse.ArgumentParser(description="Extract features for supervised training")
    ap.add_argument("--real", default="data/raw/real", help="Folder with real videos")
    ap.add_argument("--fake", default="data/raw/fake", help="Folder with fake videos")
    ap.add_argument("--out", default="data/training/features.csv", help="Output CSV path")
    ap.add_argument("--resume", action="store_true", help="Skip IDs already present in the output CSV")
    ap.add_argument("--no-resume", dest="resume", action="store_false", help="Do not skip existing IDs")
    ap.set_defaults(resume=True)
    ap.add_argument("--flush_every", type=int, default=1, help="Flush to disk every N rows (default 1 = per-row)")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit on files for a quick run")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Determine header / existing IDs if resuming
    header = None
    existing_ids = set()
    file_exists = os.path.exists(args.out) and os.path.getsize(args.out) > 0
    if file_exists:
        try:
            with open(args.out, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                if args.resume and reader.fieldnames and "id" in reader.fieldnames:
                    for row in reader:
                        if "id" in row and row["id"]:
                            existing_ids.add(row["id"])
        except Exception as e:
            print(f"[WARN] Could not read existing CSV ({e}); will not skip existing IDs.")

    # Open for append; write header if file doesn't exist
    written = 0
    processed = 0
    with open(args.out, "a", newline="", encoding="utf-8") as f:
        # Prime writer
        if header is None:
            # Create a temporary row to get columns order
            # (We will delay actual writing until first real row)
            header = None
        w = None

        for path, lbl in iter_labeled_files(args.real, args.fake):
            if args.limit and processed >= args.limit:
                break
            try:
                row = build_features_row(path, lbl)
                processed += 1
                rid = row.get("id")
                if args.resume and rid in existing_ids:
                    print(f"[SKIP] {rid} already in {os.path.basename(args.out)}")
                    continue

                # Initialize header/writer on first row if needed
                if w is None:
                    cols = list(row.keys())
                    # If file didn't exist or had no header, write it now
                    if not file_exists or not existing_ids:
                        writer = csv.DictWriter(f, fieldnames=cols)
                        writer.writeheader()
                        w = writer
                    else:
                        # file exists with header; ensure order
                        writer = csv.DictWriter(f, fieldnames=cols)
                        # don't write header again
                        w = writer

                w.writerow(row)
                written += 1
                if args.flush_every and (written % args.flush_every == 0):
                    f.flush()
                print(f"[{written}] {os.path.basename(path)}  label={lbl}")
            except KeyboardInterrupt:
                print("\n[INTERRUPTED] Exiting by user request.")
                break
            except Exception as e:
                print(f"[WARN] Skipping {path}: {e}")
                continue

    if written == 0:
        print("No new rows written (all IDs may have been already present or no videos found).")
    else:
        print(f"\nAppended {written} new rows → {args.out}")


if __name__ == "__main__":
    main()


