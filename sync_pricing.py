import requests
import openpyxl
import json
import math
from io import BytesIO
from datetime import date

FILE_ID = "1WXsJiUkQ9zivbybU57MDngPBGQufrFrT"
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=xlsx"

def mround(value, multiple):
    if not multiple: return value
    return round(value / multiple) * multiple

def calc_unit(unit, status, floor, blocks, per_sq_ft, fobs=0, mailbox=0, desks=0):
    if not blocks: return None
    sq_ft = mround(blocks * 440, 10)
    yearly = sq_ft * per_sq_ft
    monthly = mround(yearly / 12, 25)
    fob_cost = (fobs or 0) * 15
    mailbox_cost = mailbox or 0
    desk_cost = (desks or 0) * 250
    total_monthly = monthly + fob_cost + mailbox_cost + desk_cost
    return {
        "unit": unit,
        "status": "Available" if status in ("Avail", "Available") else "Not Available",
        "floor": floor,
        "sq_ft": int(sq_ft),
        "per_sq_ft": per_sq_ft,
        "monthly": int(monthly),
        "fobs": fobs or 0,
        "mailbox": mailbox_cost,
        "desks": desks or 0,
        "total_monthly": int(total_monthly)
    }

print("Downloading spreadsheet...")
resp = requests.get(EXPORT_URL)
resp.raise_for_status()
wb = openpyxl.load_workbook(BytesIO(resp.content))
print("Sheets:", wb.sheetnames)

ws = wb["Availability"]
rows = list(ws.iter_rows(values_only=True))

# Parse Availability tab - row 4 is header (index 3), data starts row 5 (index 4)
def get_row(i): return rows[i] if i < len(rows) else [None]*19

floor1 = [
    calc_unit("Unit 100", "Avail", 1, get_row(4)[3],  get_row(4)[5],  fobs=get_row(4)[9],  mailbox=get_row(4)[11], desks=get_row(4)[12]),
    calc_unit("Unit 105", "NA",    1, get_row(5)[3],  get_row(5)[5],  fobs=get_row(5)[9],  mailbox=get_row(5)[11], desks=get_row(5)[12]),
    calc_unit("Unit 110", "Avail", 1, get_row(6)[3],  get_row(6)[5],  fobs=get_row(6)[9],  mailbox=get_row(6)[11], desks=get_row(6)[12]),
    calc_unit("Unit 115", "Avail", 1, get_row(7)[3],  get_row(7)[5],  fobs=get_row(7)[9],  mailbox=get_row(7)[11], desks=get_row(7)[12]),
    calc_unit("Unit 120", "Avail", 1, get_row(8)[3],  get_row(8)[5],  fobs=get_row(8)[9],  mailbox=get_row(8)[11], desks=get_row(8)[12]),
    calc_unit("Unit 125", "Avail", 1, get_row(9)[3],  get_row(9)[5],  fobs=get_row(9)[9],  mailbox=get_row(9)[11], desks=get_row(9)[12]),
    calc_unit("Unit 130", "Avail", 1, get_row(10)[3], get_row(10)[5], fobs=get_row(10)[9], mailbox=get_row(10)[11], desks=get_row(10)[12]),
    calc_unit("Unit 135", "Avail", 1, get_row(11)[3], get_row(11)[5], fobs=get_row(11)[9], mailbox=get_row(11)[11], desks=get_row(11)[12]),
    calc_unit("Unit 140", "Avail", 1, get_row(12)[3], get_row(12)[5], fobs=get_row(12)[9], mailbox=get_row(12)[11], desks=get_row(12)[12]),
    calc_unit("Unit 142", "Avail", 1, get_row(13)[3], get_row(13)[5], fobs=get_row(13)[9], mailbox=get_row(13)[11], desks=get_row(13)[12]),
    calc_unit("Unit 145", "Avail", 1, get_row(14)[3], get_row(14)[5], fobs=get_row(14)[9], mailbox=get_row(14)[11], desks=get_row(14)[12]),
    calc_unit("Unit 150", "Avail", 1, get_row(15)[3], get_row(15)[5], fobs=get_row(15)[9], mailbox=get_row(15)[11], desks=get_row(15)[12]),
    calc_unit("Unit 155", "Avail", 1, get_row(16)[3], get_row(16)[5], fobs=get_row(16)[9], mailbox=get_row(16)[11], desks=get_row(16)[12]),
    calc_unit("Unit 160", "Avail", 1, get_row(17)[3], get_row(17)[5], fobs=get_row(17)[9], mailbox=get_row(17)[11], desks=get_row(17)[12]),
    calc_unit("Unit 165", "Avail", 1, get_row(18)[3], get_row(18)[5], fobs=get_row(18)[9], mailbox=get_row(18)[11], desks=get_row(18)[12]),
]

floor2 = [
    calc_unit("Unit 205", "NA", 2, get_row(27)[3], get_row(27)[5]),
    calc_unit("Unit 210", "NA", 2, get_row(28)[3], get_row(28)[5]),
]

floor3 = [
    calc_unit("Unit 305",   "Avail", 3, get_row(36)[3], get_row(36)[5]),
    calc_unit("Unit 310",   "Avail", 3, get_row(37)[3], get_row(37)[5]),
    calc_unit("Unit 315",   "Avail", 3, get_row(38)[3], get_row(38)[5]),
    calc_unit("Unit 320",   "Avail", 3, get_row(39)[3], get_row(39)[5]),
    calc_unit("Unit 325",   "Avail", 3, get_row(40)[3], get_row(40)[5]),
    calc_unit("Unit 326",   "Avail", 3, get_row(41)[3], get_row(41)[5]),
    calc_unit("Unit 327",   "Avail", 3, get_row(42)[3], get_row(42)[5]),
    calc_unit("Unit 330 W", "NA",    3, get_row(43)[3], get_row(43)[5]),
    calc_unit("Unit 335",   "NA",    3, get_row(44)[3], get_row(44)[5]),
    calc_unit("Unit 340",   "NA",    3, get_row(45)[3], get_row(45)[5]),
    calc_unit("Unit 345",   "Avail", 3, get_row(46)[3], get_row(46)[5]),
    calc_unit("Unit 350 W", "Avail", 3, get_row(47)[3], get_row(47)[5]),
    calc_unit("Unit 355 W", "Avail", 3, get_row(48)[3], get_row(48)[5]),
    calc_unit("Unit 360 W", "Avail", 3, get_row(49)[3], get_row(49)[5]),
    calc_unit("Unit 365 W", "Avail", 3, get_row(50)[3], get_row(50)[5]),
    calc_unit("Unit 370",   "Avail", 3, get_row(51)[3], get_row(51)[5]),
    calc_unit("Unit 375 W", "Avail", 3, get_row(52)[3], get_row(52)[5]),
    calc_unit("Unit 380 W", "Avail", 3, get_row(53)[3], get_row(53)[5]),
]

floor4 = [
    {"unit": f"Unit {n}", "status": "Not Available", "floor": 4, "sq_ft": None, "per_sq_ft": None, "monthly": None, "total_monthly": None}
    for n in [405,410,415,420,425,430,435,440,445,450,455,460]
]

lot = [
    {"unit": "Parking Lot Storage", "status": "Available", "floor": "Lot", "sq_ft": 8000, "per_sq_ft": 1, "monthly": 667, "total_monthly": 667},
    {"unit": "Stand Alone Warehouse/Workshop", "status": "Available", "floor": "Lot", "sq_ft": 3000, "per_sq_ft": 7, "monthly": 1750, "total_monthly": 1750},
]

def clean(lst): return [u for u in lst if u is not None]

pricing = {
    "last_updated": str(date.today()),
    "property": "901 S 15th St.",
    "floors": {
        "1": clean(floor1),
        "2": clean(floor2),
        "3": clean(floor3),
        "4": floor4,
        "Lot": lot
    },
    "addons": [
        {"name": "Extra FOB", "monthly": 20},
        {"name": "Personal Desk", "monthly": 250},
        {"name": "Mailbox", "monthly": 25}
    ]
}

with open("pricing.json", "w") as f:
    json.dump(pricing, f, indent=2)

print(f"pricing.json updated — {date.today()}")
