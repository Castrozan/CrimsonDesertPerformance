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
| 7 | r7 older DLSS model (`NVIDIA DLSS` instead of `NVIDIA DLSS 4.0`) | running | 27.2 / 28.0 / 13.7 | 3343 | 3768 | 265 |

The 160 s window starting 240 s later (the forest after the transition) gives the same picture: r5 52.0 / 49.5 / 36.6,
r6 29.9 / 34.9 / 10.8, and r7 27.8 / 28.0 / 26.7.

Every prepped launch on 2026-11-16 reached the world: the seven runs, two restore checks, and one Steam launch through
`cdperf-run`. The kernel logs `NV_ERR_NO_MEMORY` lines at nearly every launch, prepped or not, so those lines alone do
not mark a crash.

## What the runs show

- **Budget cap (the ASI): no effect on VRAM, so it was removed.** The game reads its VRAM budget about 1,000 times a
  second, but with 2560 or 1536 MiB reported it still used about 3245 MiB, and its peak did not move. At 1536 MiB the
  frame rate also fell.
- **Frame generation off: about 200 MiB less VRAM, at the cost of smoothness.** Game VRAM peak fell by 224 MiB with hex
  stopped and by 192 MiB with hex running. Total VRAM fell by 112 to 158 MiB. Presented frames roughly halved and the
  minimum dropped, because frame generation's extra frames are gone. In the in-game stats panel, GPU frame time on the
  same view went from 51.04 ms to 21.91 ms.
- **Older DLSS model: slower, no VRAM saving.** Switching from DLSS 4.0 to the older model halved the presented frame
  rate in both windows and left VRAM unchanged, so DLSS 4.0 stays.
- **Run-to-run noise is large.** The two baselines (r1 and r5) differ by 20 fps mean. Only the VRAM differences
  repeat across pairs, so they are the only effect this data supports.
- **Host memory.** Background services decide how much RAM and VRAM the game gets. With the voice service `hex` held
  at 723 MiB of VRAM, total VRAM use was 3765 MiB; without it, 3028 MiB. hex must keep running on this machine, so
  the package never pauses it.
- **Swap.** At about 21:52, with the game in the world, 11.9 GB of swap was in use, and 2.8 GB of it was the game's own
  memory. Stopping the 13 media containers (arr and stremio) cut swap use to 9.65 GB and raised available RAM from
  2614 to 3125 MiB. That is why the wrapper can stop containers for the session.

## Settings that do nothing

Several `user_engine_option_save.xml` keys are widely shared online: `_textureStreamingPoolSizeMB`, `_renderAheadLimit`,
`_workerThreadCount`, `_dynamicResolutionMin`, `_dynamicResolutionMax` and `_enableAsyncCompute`. None of them
appears anywhere in `CrimsonDesert.exe` build 1.0.0.3663, so the engine cannot read them.
