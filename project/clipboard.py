from __future__ import annotations

import shutil
import subprocess
import sys


def copy_to_clipboard(text: str) -> None:
    # Try common clipboard helpers; do nothing if none are present
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode(), check=False)
    elif shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=False)
    elif shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text.encode(), check=False)
    else:
        print(
            "Note: No clipboard utility found (expected wl-copy or xclip). Skipping --copy.",
            file=sys.stderr,
        )
