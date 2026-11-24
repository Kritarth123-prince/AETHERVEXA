"""One-time migration from the app's earlier name (TraceLens).

Copies settings (including encrypted API keys, which stay readable because they
are bound to the Windows user, not the app), the local analysis history and
any downloaded tools. Nothing is deleted from the old location.
"""

from __future__ import annotations

import os
import shutil

OLD_ID = "TraceLens"
NEW_ID = "AETHERVEXA"


def migrate_previous_install() -> list[str]:
    copied: list[str] = []
    roaming, local = os.environ.get("APPDATA"), os.environ.get("LOCALAPPDATA")
    try:
        if roaming:
            old_ini = os.path.join(roaming, OLD_ID, f"{OLD_ID}.ini")
            new_ini = os.path.join(roaming, NEW_ID, f"{NEW_ID}.ini")
            if os.path.isfile(old_ini) and not os.path.exists(new_ini):
                os.makedirs(os.path.dirname(new_ini), exist_ok=True)
                shutil.copy2(old_ini, new_ini)
                copied.append(new_ini)
        if local:
            for name in ("history.json", "tools"):
                old = os.path.join(local, OLD_ID, name)
                new = os.path.join(local, NEW_ID, name)
                if os.path.exists(old) and not os.path.exists(new):
                    os.makedirs(os.path.dirname(new), exist_ok=True)
                    (shutil.copytree if os.path.isdir(old) else shutil.copy2)(old, new)
                    copied.append(new)
    except OSError:
        pass  # migration is a convenience; the app works without it
    return copied
