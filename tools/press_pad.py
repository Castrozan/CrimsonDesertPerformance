import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "CrimsonDesertMultiplayer/tools/agent_mcp"))

from agent_mcp.virtual_pad import VirtualPad

pad = VirtualPad()
for control in sys.argv[1:]:
    pad.set_control(control, True)
    time.sleep(0.15)
    pad.set_control(control, False)
    time.sleep(0.8)
pad.close()
