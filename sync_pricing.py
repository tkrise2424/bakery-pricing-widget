import requests
import csv
import json
from io import StringIO
from datetime import date

FILE_ID = "1Ij8A3RI_UYVBfFB3YbXH6uKdXrAg3voG32LzN2pkGz8"
SHEET_GID = "10544563"  # Publish Pricing tab
CSV_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv&gid={SHEET_GID}"

def to_float(val):
    """Safely convert a cell value to float, stripping any text formatting."""
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None

def to_int(val):
    v = to_float(val)
    return int(v) if v is not None else None

def parse_floor(val):
    """Parse floor value - returns int for numeric floors, 'Lot' for lot items."""
    if val is None or val == "":
        return None
    s = str(val).strip()
    if s.lower() == "lot":
        return "Lot"
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return s

print("Downloading CSV...")
resp = requests.get(CSV_URL)
resp.raise_for_status()

reader = csv.reader(resp.text.splitlines())
rows = list(reader)
print(f"Got {len(rows)} rows")

# Debug: print first 5 rows
for i, r in enumerate(rows[:5]):
    print(f"  Row {i}: {r}")

units_by_floor = {}
lot_items = []

for row in rows:
    if not row or len(row) < 2:
        continue

    col_a = str(row[0]).strip() if row[0] else ""
    col_b = str(row[1]).strip() if len(row) > 1 and row[1] else ""
    col_c = row[2] if len(row) > 2 else None
    col_d = row[3] if len(row) > 3 else None
    col_e = row[4] if len(row) > 4 else None

    # Skip header rows
    if col_b == "Status" and col_c == "Floor":
        continue

    # Skip empty / test rows
    if not col_a or col_a == "Test":
        continue

    # Skip addon rows (handled separately below)
    if col_a in ("Extra FOB", "Personal Desk", "Mailbox"):
        continue

    # Only process unit rows
    if not (col_a.startswith("Unit") or col_a.lower().startswith("parking") or col_a.lower().startswith("stand")):
        continue

    is_avail = col_b.lower() in ("avail", "available")
    floor_key = parse_floor(col_c)
    sq_ft = to_int(col_d)
    monthly = to_int(col_e)

    unit = {
        "unit": col_a.strip(),
        "status": "Available" if is_avail else "Not Available",
        "floor": floor_key if floor_key == "Lot" else floor_key,
        "sq_ft": sq_ft,
        "per_sq_ft": None,
        "monthly": monthly,
        "total_monthly": monthly
    }

    print(f"  Parsed: {unit['unit']} | {unit['status']} | floor={unit['floor']} | sq_ft={unit['sq_ft']} | ${unit['monthly']}")

    if floor_key == "Lot":
        lot_items.append(unit)
    elif floor_key is not None:
        floor_str = str(floor_key)
        if floor_str not in units_by_floor:
            units_by_floor[floor_str] = []
        units_by_floor[floor_str].append(unit)

# Parse addons from the bottom of the sheet
addons = []
capture = False
for row in rows:
    if not row:
        continue
    col_a = str(row[0]).strip() if row[0] else ""
    col_b = str(row[1]).strip() if len(row) > 1 and row[1] else ""

    if col_b == "Monthly":
        capture = True
        continue

    if capture and col_a in ("Extra FOB", "Personal Desk", "Mailbox"):
        monthly = to_int(row[4]) if len(row) > 4 else None
        addons.append({"name": col_a, "monthly": monthly})

# Fallback addons
if not addons:
    addons = [
        {"name": "Extra FOB", "monthly": 20},
        {"name": "Personal Desk", "monthly": 250},
        {"name": "Mailbox", "monthly": 25}
    ]

# Build floors dict
floors = {}
for fk in ["1", "2", "3", "4"]:
    floors[fk] = units_by_floor.get(fk, [])
if lot_items:
    floors["Lot"] = lot_items

pricing = {
    "last_updated": str(date.today()),
    "property": "901 S 15th St.",
    "floors": floors,
    "addons": addons
}

print(f"\nFloor counts: { {k: len(v) for k, v in floors.items()} }")
print(f"Addons: {addons}")

with open("pricing.json", "w") as f:
    json.dump(pricing, f, indent=2)

print(f"pricing.json updated — {date.today()}")
