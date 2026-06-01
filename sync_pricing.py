import requests
import openpyxl
import json
from io import BytesIO
from datetime import date

FILE_ID = "1Ij8A3RI_UYVBfFB3YbXH6uKdXrAg3voG32LzN2pkGz8"
SHEET_GID = "10544563"  # Publish Pricing tab
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=xlsx&gid={SHEET_GID}"

def to_float(val):
    """Safely convert a cell value to float, stripping any text formatting."""
    if val is None:
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
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() == "lot":
        return "Lot"
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return s

print("Downloading spreadsheet...")
resp = requests.get(EXPORT_URL)
resp.raise_for_status()
wb = openpyxl.load_workbook(BytesIO(resp.content))
ws = wb.active
print("Sheet:", ws.title)

rows = list(ws.iter_rows(values_only=True))

# Parse units from Publish Pricing tab
# Data rows: Col A=unit name, Col B=status, Col C=floor, Col D=sq ft, Col E=monthly
# Sections are separated by repeated header rows ['', 'Status', 'Floor', 'Sq ft', 'Monthly']

units_by_floor = {}
lot_items = []

for row in rows:
    if row is None or len(row) == 0:
        continue

    col_a = str(row[0]).strip() if row[0] is not None else ""
    col_b = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
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
    if not (col_a.startswith("Unit") or col_a in ("Parking Lot Storage", "Stand Alone warehouse/workshop")):
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

    if floor_key == "Lot":
        lot_items.append(unit)
    else:
        floor_str = str(floor_key)
        if floor_str not in units_by_floor:
            units_by_floor[floor_str] = []
        units_by_floor[floor_str].append(unit)

# Parse addons from the bottom of the sheet
addons = []
capture_addons = False
for row in rows:
    if row is None or len(row) == 0:
        continue
    col_a = str(row[0]).strip() if row[0] is not None else ""
    col_b = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""

    if col_b == "Monthly":
        capture_addons = True
        continue

    if capture_addons and col_a in ("Extra FOB", "Personal Desk", "Mailbox"):
        monthly = to_int(row[4]) if len(row) > 4 else None
        addons.append({"name": col_a, "monthly": monthly})

# Fallback addons if not parsed
if not addons:
    addons = [
        {"name": "Extra FOB", "monthly": 20},
        {"name": "Personal Desk", "monthly": 250},
        {"name": "Mailbox", "monthly": 25}
    ]

# Build floors dict
floors = {}
for fk in ["1", "2", "3", "4"]:
    if fk in units_by_floor:
        floors[fk] = units_by_floor[fk]
    else:
        floors[fk] = []

if lot_items:
    floors["Lot"] = lot_items

pricing = {
    "last_updated": str(date.today()),
    "property": "901 S 15th St.",
    "floors": floors,
    "addons": addons
}

with open("pricing.json", "w") as f:
    json.dump(pricing, f, indent=2)

print(f"pricing.json updated — {date.today()}")
