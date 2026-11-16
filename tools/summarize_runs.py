#!/usr/bin/env python3
import argparse
import csv
import statistics
import sys
from pathlib import Path


def numbers(rows: list[dict], column: str) -> list[float]:
    return [float(row[column]) for row in rows if row[column] not in ("", "None")]


def summarize(path: Path, skip_seconds: float, window_seconds: float) -> dict:
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    game_rows = [row for row in rows if row["game_pid"] not in ("", "0")]
    world_rows = [
        row for row in game_rows if row["frames_per_second"] not in ("", "None")
    ]
    if world_rows:
        start = float(world_rows[0]["unix_time"])
        world_rows = [
            row
            for row in world_rows
            if skip_seconds <= float(row["unix_time"]) - start <= skip_seconds + window_seconds
        ]
    frame_rates = numbers(world_rows, "frames_per_second")
    return {
        "run": path.stem,
        "fps_samples": len(frame_rates),
        "fps_mean": round(statistics.fmean(frame_rates), 1) if frame_rates else None,
        "fps_median": round(statistics.median(frame_rates), 1) if frame_rates else None,
        "fps_min": min(frame_rates, default=None),
        "game_video_peak_mib": max(
            numbers(game_rows, "game_video_mebibytes"), default=None
        ),
        "total_video_peak_mib": max(
            numbers(game_rows, "total_video_used_mebibytes"), default=None
        ),
        "game_resident_peak_mib": max(
            numbers(game_rows, "game_resident_mebibytes"), default=None
        ),
        "memory_available_min_mib": min(
            numbers(game_rows, "memory_available_mebibytes"), default=None
        ),
        "gpu_power_mean_watts": round(
            statistics.fmean(numbers(world_rows, "gpu_power_watts")), 1
        )
        if world_rows
        else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--skip", type=float, default=0.0)
    parser.add_argument("--window", type=float, default=180.0)
    arguments = parser.parse_args()
    summaries = [summarize(path, arguments.skip, arguments.window) for path in arguments.runs]
    columns = list(summaries[0])
    print("| " + " | ".join(columns) + " |")
    print("|" + "---|" * len(columns))
    for summary in summaries:
        print("| " + " | ".join(str(summary[column]) for column in columns) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
