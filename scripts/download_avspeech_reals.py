"""
Download a curated subset of AVSpeech real clips from YouTube and store them
as local training samples.

Each row in avspeech_train.csv has:
    youtube_id,start,end,x_center,y_center

We only need the YouTube segment timings—coordinates are ignored for now.

Usage example:
    python -m scripts.download_avspeech_reals \
        --csv data/avspeech_train.csv \
        --output_dir data/raw/real/avspeech \
        --max_clips 250

Requires:
    pip install yt-dlp
    FFmpeg available on PATH
"""

from __future__ import annotations

import argparse
import csv
import random
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import yt_dlp  # type: ignore


YT_URL = "https://www.youtube.com/watch?v={vid}"


@dataclass
class ClipRow:
    youtube_id: str
    start: float
    end: float
    x: float
    y: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def parse_csv(csv_path: Path) -> List[ClipRow]:
    rows: List[ClipRow] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line in reader:
            if not line or line[0].startswith("#"):
                continue
            try:
                yt_id = line[0].strip()
                start = float(line[1])
                end = float(line[2])
                x = float(line[3])
                y = float(line[4])
            except (IndexError, ValueError):
                continue
            rows.append(ClipRow(yt_id, start, end, x, y))
    return rows


def iter_candidates(rows: List[ClipRow], min_duration: float) -> Iterator[ClipRow]:
    random.shuffle(rows)
    for row in rows:
        if row.duration < min_duration:
            continue
        yield row


def trim_with_ffmpeg(src: Path, dst: Path, start: float, duration: float) -> bool:
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(src),
        "-t",
        f"{duration:.3f}",
        "-c",
        "copy",
        str(dst),
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        print(f"[ffmpeg] failed: {proc.stderr.decode(errors='ignore')[:400]}")
        return False
    return True


def download_clip(row: ClipRow, tmp_dir: Path) -> Path | None:
    url = YT_URL.format(vid=row.youtube_id)
    tmp_out = tmp_dir / f"{row.youtube_id}.%(ext)s"
    opts = {
        "outtmpl": str(tmp_out),
        "quiet": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "retries": 2,
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.download([url])
            if res != 0:
                return None
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[yt-dlp] error for {row.youtube_id}: {exc}")
        return None

    mp4_files = list(tmp_dir.glob(f"{row.youtube_id}*.mp4"))
    if not mp4_files:
        return None
    return mp4_files[0]


def main() -> None:
    ap = argparse.ArgumentParser(description="Download real clips from AVSpeech.")
    ap.add_argument("--csv", type=Path, required=True, help="Path to avspeech_train.csv")
    ap.add_argument("--output_dir", type=Path, required=True, help="Directory for trimmed clips")
    ap.add_argument("--max_clips", type=int, default=200, help="Number of clips to download")
    ap.add_argument("--min_duration", type=float, default=2.5, help="Skip segments shorter than this many seconds")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    args = ap.parse_args()

    random.seed(args.seed)
    rows = parse_csv(args.csv)
    if not rows:
        raise SystemExit("No valid rows found in CSV")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    downloaded = 0

    with tempfile.TemporaryDirectory(prefix="avspeech_dl_") as tmp_root:
        tmp_path = Path(tmp_root)
        for row in iter_candidates(rows, args.min_duration):
            if downloaded >= args.max_clips:
                break

            clip_name = f"{row.youtube_id}_{int(row.start)}_{int(row.end)}.mp4"
            dst = args.output_dir / clip_name
            if dst.exists():
                print(f"[skip] exists: {dst.name}")
                continue

            print(f"[{downloaded+1}/{args.max_clips}] Downloading {row.youtube_id} ({row.start:.1f}s→{row.end:.1f}s)")
            raw_path = download_clip(row, tmp_path)
            if raw_path is None:
                print(f"  ! Unable to download {row.youtube_id}, skipping")
                continue

            if not trim_with_ffmpeg(raw_path, dst, row.start, row.duration):
                print(f"  ! Trim failed for {row.youtube_id}, skipping")
                raw_path.unlink(missing_ok=True)
                continue

            raw_path.unlink(missing_ok=True)
            downloaded += 1
            manifest.append(
                {
                    "file": clip_name,
                    "youtube_id": row.youtube_id,
                    "start": row.start,
                    "end": row.end,
                    "duration": row.duration,
                }
            )

    if manifest:
        manifest_path = args.output_dir / "manifest.json"
        import json

        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Saved manifest to {manifest_path}")
    else:
        print("No clips downloaded.")


if __name__ == "__main__":
    main()

