# Crimson Desert Performance

Gives Crimson Desert more headroom on a small machine (4 GB of VRAM, 16 GB of RAM, Linux with Proton). The game
overflows a 4 GB card into pinned system RAM. When the host runs short of RAM, the NVIDIA driver fails to allocate
(`NVRM ... NV_ERR_NO_MEMORY` in `journalctl -k`) and the game can die during a world load.

The package has two independent parts, both in `package/linux/`:

- `cdperf-run` is a Steam launch wrapper. Before the game starts it drops the page cache and compacts memory, so the
  driver can find the contiguous pinned pages it needs. It can also stop user and system services and Docker containers you name
  for the length of the session, and starts them again when the game exits.
- `cdperf-settings` turns frame generation off in the game's settings file, and restores the original. On a 4 GB card
  this frees about 200 MiB of VRAM, but you see roughly half as many frames: frame generation's extra frames are gone.
  Use it if loads run out of memory; skip it if smoothness matters more.

The measurements behind these choices, and the levers that did not work, are in
[measurements/RESULTS.md](measurements/RESULTS.md).

## Install

1. Copy the scripts onto your PATH: `install -Dm755 package/linux/cdperf-* -t ~/.local/bin/`.
2. Make sure `sudo -n sh -c 'echo 3 > /proc/sys/vm/drop_caches'` works without a password. If it doesn't, the
   wrapper skips the cache drop and says so on stderr.
3. In Steam, go to Crimson Desert, Properties, General, Launch Options, and set
   `/home/<you>/.local/bin/cdperf-run %command%` (use the absolute path).
4. To free more memory while you play, create `~/.config/cdperf/config` (a shell file the wrapper sources):

   ```sh
   CDPERF_PAUSE_USER_UNITS="syncthing.service"
   CDPERF_STOP_SYSTEM_UNITS="media-on-demand.timer"
   CDPERF_STOP_CONTAINERS_MATCHING="^(arr-|stremio-)"
   ```

   `CDPERF_PAUSE_USER_UNITS` and `CDPERF_STOP_SYSTEM_UNITS` list user and system units, space separated; system units
   need passwordless `sudo`. Stop any timer or service that would bring a stopped container back.
   `CDPERF_STOP_CONTAINERS_MATCHING` is an extended regular expression matched against running Docker container
   names. A unit named `hex` is never stopped, because voice wake depends on it.
5. Optionally, with the game closed, run `cdperf-settings apply` to turn frame generation off. The original file is
   kept next to it as `user_engine_option_save.xml.cdperf-backup`.

## Uninstall

1. With the game closed, run `cdperf-settings revert` to restore the original settings file.
2. Clear the Launch Options field in Steam.
3. Delete `~/.local/bin/cdperf-run`, `~/.local/bin/cdperf-free-memory`, `~/.local/bin/cdperf-settings` and
   `~/.config/cdperf/`.

Paused services and stopped containers start again when the game exits, so nothing else is left behind. The co-op
mod is untouched by either part.

## Measuring

`tools/measured_run.sh <label> [seconds]` takes the shared game lock (`~/.local/share/cdmp/game.lock`; it refuses
while another session holds it), closes the game, frees host memory, starts `tools/sample_metrics.py`, launches the
game through Steam and presses Play on a virtual pad until the co-op mod reports the character in the world.
`tools/game_lock.sh release` hands the game back. Every 2 s the sampler records the frame rate (from the co-op mod's
overlay frame counter in `cdmp.log`), game and total VRAM (`nvidia-smi`), game resident memory, available RAM and
swap. The character stands still; compare runs with `tools/summarize_runs.py --skip <s> --window <s>`. Raw samples
live in `measurements/`.

## Tests

`scripts/test-linux.sh` runs the unit tests and syntax-checks the shell scripts.
