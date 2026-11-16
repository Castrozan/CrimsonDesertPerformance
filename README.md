# Crimson Desert Performance

Keeps Crimson Desert loading and running on a small machine (4 GB of VRAM, 16 GB of RAM, Linux with Proton). The game
overflows a 4 GB card into pinned system RAM; when the host runs short of RAM the NVIDIA driver fails to allocate
(`NVRM ... NV_ERR_NO_MEMORY` in `journalctl -k`) and the game dies during a world load.

The package has two parts. The Linux launch wrapper in `package/linux/` gives the game memory headroom: for the length
of the session it pauses user services you name, drops the page cache and compacts memory, then resumes the services
when the game exits. The experimental `cdperf.asi` caps the VRAM budget the game reads from
`IDXGIAdapter3::QueryVideoMemoryInfo` and sets environment variables before Direct3D starts.

## Install the launch wrapper (Linux)

1. Copy the scripts onto your PATH: `install -Dm755 package/linux/cdperf-* -t ~/.local/bin/`.
2. Make sure `sudo -n sh -c 'echo 3 > /proc/sys/vm/drop_caches'` works without a password. If it doesn't, the
   wrapper skips the cache drop and says so on stderr.
3. In Steam, go to Crimson Desert, Properties, General, Launch Options, and set `~/.local/bin/cdperf-run %command%`.
4. To pause services other than the default `hex.service`, list them, space separated, in
   `CDPERF_PAUSE_USER_UNITS`, for example `CDPERF_PAUSE_USER_UNITS="hex.service other.service" ~/.local/bin/cdperf-run %command%`.

To uninstall, clear the Launch Options field and delete `~/.local/bin/cdperf-run` and `~/.local/bin/cdperf-free-memory`.
Paused services start again when the game exits.

## The ASI (experimental)

`scripts/build-linux.sh` builds `build/linux/bin/cdperf.asi` with clang-cl and xwin through Nix. It needs Ultimate ASI
Loader installed as `bin64/winmm.dll`, and it runs next to the co-op mod `cdmp.asi`. To install, copy `cdperf.asi` and
`package/cdperf.ini` into `bin64`. To uninstall, delete `cdperf.asi`, `cdperf.ini` and `cdperf.log` from `bin64`.

```ini
[video_memory]
local_budget_cap_mb=2560

[environment]
VKD3D_CONFIG=no_upload_hvv
```

Setting `local_budget_cap_mb=0` turns the cap off. Each `[environment]` line is set inside the game process before
Direct3D starts, so Proton options such as `VKD3D_CONFIG` or `DXVK_CONFIG` work without Steam launch options. A
`dxvk.conf` `dxgi.maxDeviceMemory` alone does not cap the budget: DXVK only applies it to the adapter description, and
the budget comes straight from the Vulkan driver.

## Measuring

`tools/measured_run.sh <label>` takes the shared game lock (`~/.local/share/cdmp/game.lock`; it refuses while another
session holds it), closes the game, frees host memory, starts `tools/sample_metrics.py`, launches the game through
Steam and presses Play on a virtual pad until the co-op mod reports the character in the world. `tools/game_lock.sh
release` hands the game back. Every 2 s the sampler records the frame rate (from the co-op mod's overlay frame counter in
`cdmp.log`), game and total VRAM (`nvidia-smi`), game resident memory, available RAM and swap. The character stands
still; compare runs with `tools/summarize_runs.py`, which reports the first 160 s in the world. Results and raw samples live in `measurements/`.

## Settings that do nothing

Several `user_engine_option_save.xml` keys are widely shared online: `_textureStreamingPoolSizeMB`, `_renderAheadLimit`,
`_workerThreadCount`, `_dynamicResolutionMin`, `_dynamicResolutionMax` and `_enableAsyncCompute`. None of them
appears anywhere in `CrimsonDesert.exe` build 1.0.0.3663, so the engine cannot read them.

## Tests

`scripts/test-linux.sh` runs the property test for the budget rule natively, plus the sampler's unit tests.
