from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
base = root / "src/main/java/com/baroxvs/client"
java_files = sorted(base.rglob("*.java"))
print("=== JAVA FILES WITH GLASS / CHOOSE REFERENCES ===")
for path in java_files:
    src = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"glass|choose", src, re.I) or re.search(r"glass|choose", path.name, re.I):
        print(f"FILE {path.relative_to(root)} ({len(src.splitlines())} lines)")
        for number, line in enumerate(src.splitlines(), 1):
            if re.search(r"glass|choose", line, re.I):
                print(f"  {number}: {line.strip()[:240]}")

print("\n=== MODULE CATALOG REGISTRATIONS AROUND GLASS / CHOOSE / WET ===")
catalog = base / "cosmetic/ModuleCatalog.java"
lines = catalog.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if re.search(r"glass|choose|wet_world|liquid_rain|reflection|held_item", line, re.I):
        lo, hi = max(0, i-3), min(len(lines), i+5)
        print(f"--- {catalog.name}:{i+1} ---")
        for j in range(lo, hi):
            print(f"{j+1}: {lines[j]}")

print("\n=== UI / RENDER METHODS THAT DRAW GLASS OR MODULE CHOICES ===")
for path in java_files:
    if not any(k in path.name.lower() for k in ("glass", "module", "skin", "cosmetic", "hud", "menu", "ui")):
        continue
    src = path.read_text(encoding="utf-8", errors="replace")
    rows = src.splitlines()
    wanted = [i for i, line in enumerate(rows) if re.search(
        r"glass|choose|selectedModule|module.*(card|row|tile)|draw.*(panel|module)|render.*glass",
        line, re.I)]
    if not wanted:
        continue
    print(f"--- {path.relative_to(root)} ({len(rows)} lines) ---")
    seen = set()
    for i in wanted:
        lo, hi = max(0, i-4), min(len(rows), i+7)
        if any(j in seen for j in range(lo, hi)):
            continue
        seen.update(range(lo, hi))
        for j in range(lo, hi):
            print(f"{j+1}: {rows[j]}")
        print("...")

print("\\n=== PRECISE UI DRAW RANGES ===")
ranges = {
    "gui/Ui.java": [(1, 260)],
    "gui/ModuleClickGuiScreen.java": [(215, 520), (520, 690)],
    "gui/ModuleSettingsScreen.java": [(420, 660)],
    "gui/BaroxMenuScreen.java": [(300, 405), (540, 610)],
    "cosmetic/ModuleCatalog.java": [(105, 180), (195, 235)],
}
for rel, spans in ranges.items():
    path = base / rel
    rows = path.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"\\n--- {rel} ---")
    for first, last in spans:
        print(f"### lines {first}-{last}")
        for i in range(first - 1, min(last, len(rows))):
            print(f"{i+1}: {rows[i]}")
