# Results on chise (2026-11-16)

Machine: Ryzen 5 5600H (boost disabled, cores at about 2.77 GHz), RTX 3050 Laptop 4 GB on PCIe 3.0 x8, 16 GB RAM,
20 GB swap. Game build 1.0.0.3663 (patch 2.05.00) under Proton Experimental 11.0-20261112 with vkd3d-proton 3.2.0.
Settings: Minimum preset, NVIDIA DLSS 4.0 at 33 %, Reflex on, vsync off, AMD FSR Frame Generation on unless the run
says otherwise. The co-op mod `cdmp.asi` is loaded in every run, and host memory is freed (page cache dropped, memory
compacted) before every launch.

Each run cold-starts the game, loads the same save and stands still. The table covers the first 160 s after the frame
counter starts, which is the save's opening transition scene. The frame rate counts presents seen by the co-op
overlay, so with frame generation on, generated frames are included and the rate is roughly double the rendered rate.

| # | Run | hex | fps mean / median / min | game VRAM peak (MiB) | total VRAM peak (MiB) | Launch to world (s) |
|---|---|---|---|---|---|---|
| 1 | r1 baseline | stopped | 66.5 / 69.2 / 33.0 | 3369 | 3761 | about 240 |
| 2 | r2 ASI budget cap 2560 MiB | stopped | 62.2 / 71.6 / 25.0 | 3349 | 3748 | about 190 |
| 3 | r3 ASI budget cap 1536 MiB | stopped | 39.9 / 42.9 / 17.4 | 3347 | 3769 | about 184 |
| 4 | r4 frame generation off | stopped | 30.9 / 40.1 / 8.3 | 3145 | 3649 | 179 |
| 5 | r5 baseline repeat | running | 46.7 / 49.3 / 19.7 | 3327 | 3764 | 226 |
| 6 | r6 frame generation off | running | 28.7 / 32.4 / 7.8 | 3135 | 3606 | 191 |

The 160 s window starting 240 s later (the forest after the transition) gives the same picture: r5 52.0 / 49.5 / 36.6
and r6 29.9 / 34.9 / 10.8.

Every run loaded the save. The kernel logged `NV_ERR_NO_MEMORY` during game start-up in r1 (19:10:11), r5 (20:12:25)
and r6 (20:24:44), and the game survived each time.

## What the runs show

- **Budget cap (the ASI): no effect on VRAM, so it was removed.** The game reads its VRAM budget about 1,000 times a
  second, but with 2560 or 1536 MiB reported it still used about 3245 MiB, and its peak did not move. At 1536 MiB the
  frame rate also fell.
- **Frame generation off: about 200 MiB less VRAM, at the cost of smoothness.** Game VRAM peak fell by 224 MiB with hex
  stopped and by 192 MiB with hex running. Total VRAM fell by 112 to 158 MiB. Presented frames roughly halved and the
  minimum dropped, because frame generation's extra frames are gone. In the in-game stats panel, GPU frame time on the
  same view went from 51.04 ms to 21.91 ms.
- **Run-to-run noise is large.** The two baselines (r1 and r5) differ by 20 fps mean. Only the VRAM differences
  repeat across pairs, so they are the only effect this data supports.
- **Host memory.** Background services decide how much RAM and VRAM the game gets. With the voice service `hex` held
  at 723 MiB of VRAM, total VRAM use was 3765 MiB; without it, 3028 MiB. hex must keep running on this machine, so
  the package never pauses it.

## Settings that do nothing

Several `user_engine_option_save.xml` keys are widely shared online: `_textureStreamingPoolSizeMB`, `_renderAheadLimit`,
`_workerThreadCount`, `_dynamicResolutionMin`, `_dynamicResolutionMax` and `_enableAsyncCompute`. None of them
appears anywhere in `CrimsonDesert.exe` build 1.0.0.3663, so the engine cannot read them.
