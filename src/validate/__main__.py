"""python -m src.validate timeline.json  — exits 1 and prints errors if invalid."""
import sys
from pathlib import Path

from src.common import read_json
from src.validate import total_duration, validate

if len(sys.argv) != 2:
    sys.exit(__doc__)
tl = read_json(Path(sys.argv[1]))
errors = validate(tl)
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(tl['clips'])} clips, {total_duration(tl):.3f}s")
