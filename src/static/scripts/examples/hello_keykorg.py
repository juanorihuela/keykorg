"""
Ejemplo mínimo de script Python para usar en secuencias de KeyKorg.

Uso en scene_X.yaml:
  - action: shell
    command: "python src/static/scripts/examples/hello_keykorg.py"
"""

import subprocess
from datetime import datetime

NOW = datetime.now().strftime("%H:%M")

message = f"KeyKorg activo — {NOW}"
print(message)

subprocess.run(
    ["notify-send", "KeyKorg", message, "--icon=dialog-information"],
    check=False,
)
