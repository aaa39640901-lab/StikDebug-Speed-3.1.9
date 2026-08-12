from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
for p in (ROOT / "StikDebug").rglob("*.swift"):
    text = p.read_text(encoding="utf-8")
    fixed = text.replace("Code編輯orView", "CodeEditorView")
    if fixed != text:
        p.write_text(fixed, encoding="utf-8")
        print(f"Fixed module import in {p}")
