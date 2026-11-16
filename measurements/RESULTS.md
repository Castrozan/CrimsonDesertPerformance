# Results on chise (2026-11-16)

Machine: Ryzen 5 5600H (boost disabled, cores at about 2.77 GHz), RTX 3050 Laptop 4 GB on PCIe 3.0 x8, 16 GB RAM,
20 GB swap. Game build 1.0.0.3663 (patch 2.05.00) under Proton Experimental 11.0-20261112 with vkd3d-proton 3.2.0.
Settings: Minimum preset, NVIDIA DLSS 4.0 at 33 %, AMD FSR Frame Generation on, Reflex on, vsync off. The co-op mod
`cdmp.asi` is loaded in every run. Host memory is freed before every launch.

Scene: the save's start position, standing still, first 160 s after the frame counter starts. Frame rate counts
presents seen by the co-op overlay, so generated frames are included.

| # | Run | fps mean | fps median | fps min | game VRAM peak (MiB) | total VRAM peak (MiB) | game RSS peak (MiB) | RAM available min (MiB) | Load (s) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | r1 baseline | 66.5 | 69.2 | 33.0 | 3369 | 3761 | 4648 | 1070 | 92 |
| 2 | r2 ASI cap 2560 MiB | 62.2 | 71.6 | 25.0 | 3349 | 3748 | 5032 | 1612 | 54 |

Load time runs from pressing Play on the title screen to the co-op mod's first in-world position line, so it is
accurate to about 10 s.

## What the runs show

- The game asks for its VRAM budget about 1,000 times a second (`2026-11-16-r2-cdperf.log`), but with the budget
  reported as 2560 MiB it still used 3243 MiB, and its VRAM peak did not move. A 2560 MiB cap has no measurable effect.
- Before the runs, the voice dictation service `hex` held 723 MiB of VRAM next to the game. Stopping it took total
  VRAM use from 3765 to 3028 MiB with the game running. That is the largest single gain measured, and it is why the
  launch wrapper pauses it.
- R1 logged three `NV_ERR_NO_MEMORY` driver lines at 19:10:11 during start-up, but the game survived and loaded.
