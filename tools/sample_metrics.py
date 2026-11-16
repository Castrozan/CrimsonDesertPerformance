#!/usr/bin/env python3
import argparse
import csv
import re
import subprocess
import sys
import time
from dataclasses import dataclass, fields
from pathlib import Path

GAME_PROCESS_NAME = "CrimsonDesert.e"
DEFAULT_COOP_LOG = (
    Path.home() / ".local/share/Steam/steamapps/common/Crimson Desert/bin64/cdmp.log"
)
OVERLAY_FRAMES_PATTERN = re.compile(
    r"^\[(\d+):(\d+):(\d+\.\d+)\].*Overlay diag: frames (\d+)"
)


@dataclass
class Sample:
    unix_time: float
    game_pid: int
    frames_per_second: float | None
    game_resident_mebibytes: int | None
    game_video_mebibytes: int | None
    total_video_used_mebibytes: int | None
    gpu_utilization_percent: int | None
    gpu_clock_megahertz: int | None
    gpu_power_watts: float | None
    gpu_temperature_celsius: int | None
    memory_available_mebibytes: int
    swap_used_mebibytes: int


def find_game_pid() -> int:
    result = subprocess.run(
        ["pgrep", "-x", GAME_PROCESS_NAME], capture_output=True, text=True
    )
    pids = result.stdout.split()
    return int(pids[0]) if pids else 0


def read_meminfo_mebibytes() -> dict[str, int]:
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, rest = line.split(":", 1)
        values[key] = int(rest.split()[0]) // 1024
    return values


def read_resident_mebibytes(pid: int) -> int | None:
    if not pid:
        return None
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except OSError:
        return None
    match = re.search(r"^VmRSS:\s+(\d+) kB", status, re.MULTILINE)
    return int(match.group(1)) // 1024 if match else None


def query_nvidia(arguments: list[str]) -> list[list[str]]:
    result = subprocess.run(
        ["nvidia-smi", *arguments, "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
    )
    return [
        [cell.strip() for cell in line.split(",")]
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def parse_number(text: str, kind: type):
    try:
        return kind(float(text)) if kind is int else kind(text)
    except ValueError:
        return None


class OverlayFrameCounter:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.previous: tuple[float, int] | None = None

    def latest_reading(self) -> tuple[float, int] | None:
        try:
            with self.log_path.open("rb") as handle:
                handle.seek(0, 2)
                handle.seek(max(0, handle.tell() - 65536))
                tail = handle.read().decode(errors="ignore").splitlines()
        except OSError:
            return None
        for line in reversed(tail):
            match = OVERLAY_FRAMES_PATTERN.match(line)
            if match:
                hours, minutes, seconds, frames = match.groups()
                clock = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                return clock, int(frames)
        return None

    def frames_per_second(self) -> float | None:
        reading = self.latest_reading()
        if reading is None:
            return None
        previous, self.previous = self.previous, reading
        if previous is None or reading[0] <= previous[0] or reading[1] < previous[1]:
            return None
        return round((reading[1] - previous[1]) / (reading[0] - previous[0]), 2)


def take_sample(counter: OverlayFrameCounter) -> Sample:
    pid = find_game_pid()
    gpu = query_nvidia(
        ["--query-gpu=memory.used,utilization.gpu,clocks.gr,power.draw,temperature.gpu"]
    )
    gpu_row = gpu[0] if gpu else [""] * 5
    applications = query_nvidia(["--query-compute-apps=pid,used_memory"])
    game_video = next(
        (parse_number(row[1], int) for row in applications if row[0] == str(pid)),
        None,
    )
    memory = read_meminfo_mebibytes()
    return Sample(
        unix_time=round(time.time(), 3),
        game_pid=pid,
        frames_per_second=counter.frames_per_second(),
        game_resident_mebibytes=read_resident_mebibytes(pid),
        game_video_mebibytes=game_video,
        total_video_used_mebibytes=parse_number(gpu_row[0], int),
        gpu_utilization_percent=parse_number(gpu_row[1], int),
        gpu_clock_megahertz=parse_number(gpu_row[2], int),
        gpu_power_watts=parse_number(gpu_row[3], float),
        gpu_temperature_celsius=parse_number(gpu_row[4], int),
        memory_available_mebibytes=memory["MemAvailable"],
        swap_used_mebibytes=memory["SwapTotal"] - memory["SwapFree"],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--coop-log", type=Path, default=DEFAULT_COOP_LOG)
    arguments = parser.parse_args()

    counter = OverlayFrameCounter(arguments.coop_log)
    counter.frames_per_second()
    deadline = time.monotonic() + arguments.duration
    column_names = [field.name for field in fields(Sample)]
    with arguments.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=column_names)
        writer.writeheader()
        while time.monotonic() < deadline:
            time.sleep(arguments.interval)
            writer.writerow(take_sample(counter).__dict__)
            handle.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
