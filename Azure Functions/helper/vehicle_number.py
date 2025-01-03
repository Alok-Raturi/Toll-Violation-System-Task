import random
import string
from typing import Dict, List, Optional

STATE_CODES: Dict[str, Dict[str, List[str]]] = {
    "AN": {"name": "Andaman and Nicobar", "districts": ["01", "02"]},
    "AP": {"name": "Andhra Pradesh", "districts": [str(i).zfill(2) for i in range(1, 41)]},
    "AR": {"name": "Arunachal Pradesh", "districts": [str(i).zfill(2) for i in range(1, 26)]},
    "AS": {"name": "Assam", "districts": [str(i).zfill(2) for i in range(1, 34)]},
    "BR": {"name": "Bihar", "districts": [str(i).zfill(2) for i in range(1, 39)]},
    "CG": {"name": "Chhattisgarh", "districts": [str(i).zfill(2) for i in range(1, 29)]},
    "CH": {"name": "Chandigarh", "districts": ["01", "02", "03", "04"]},
    "DD": {"name": "Daman and Diu", "districts": ["01", "02", "03"]},
    "DL": {"name": "Delhi", "districts": [str(i).zfill(2) for i in range(1, 15)]},
    "DN": {"name": "Dadra and Nagar Haveli", "districts": ["01", "02"]},
    "GA": {"name": "Goa", "districts": ["01", "02", "03", "04"]},
    "GJ": {"name": "Gujarat", "districts": [str(i).zfill(2) for i in range(1, 39)]},
    "HP": {"name": "Himachal Pradesh", "districts": [str(i).zfill(2) for i in range(1, 13)]},
    "HR": {"name": "Haryana", "districts": [str(i).zfill(2) for i in range(1, 24)]},
    "JH": {"name": "Jharkhand", "districts": [str(i).zfill(2) for i in range(1, 25)]},
    "JK": {"name": "Jammu and Kashmir", "districts": [str(i).zfill(2) for i in range(1, 21)]},
    "KA": {"name": "Karnataka", "districts": [str(i).zfill(2) for i in range(1, 32)]},
    "KL": {"name": "Kerala", "districts": [str(i).zfill(2) for i in range(1, 15)]},
    "LA": {"name": "Ladakh", "districts": ["01", "02"]},
    "LD": {"name": "Lakshadweep", "districts": ["01", "02"]},
    "MH": {"name": "Maharashtra", "districts": [str(i).zfill(2) for i in range(1, 51)]},
    "ML": {"name": "Meghalaya", "districts": [str(i).zfill(2) for i in range(1, 13)]},
    "MN": {"name": "Manipur", "districts": [str(i).zfill(2) for i in range(1, 17)]},
    "MP": {"name": "Madhya Pradesh", "districts": [str(i).zfill(2) for i in range(1, 52)]},
    "MZ": {"name": "Mizoram", "districts": [str(i).zfill(2) for i in range(1, 12)]},
    "NL": {"name": "Nagaland", "districts": [str(i).zfill(2) for i in range(1, 13)]},
    "OD": {"name": "Odisha", "districts": [str(i).zfill(2) for i in range(1, 31)]},
    "PB": {"name": "Punjab", "districts": [str(i).zfill(2) for i in range(1, 23)]},
    "PY": {"name": "Puducherry", "districts": ["01", "02", "03", "04"]},
    "RJ": {"name": "Rajasthan", "districts": [str(i).zfill(2) for i in range(1, 34)]},
    "SK": {"name": "Sikkim", "districts": ["01", "02", "03", "04"]},
    "TN": {"name": "Tamil Nadu", "districts": [str(i).zfill(2) for i in range(1, 39)]},
    "TR": {"name": "Tripura", "districts": [str(i).zfill(2) for i in range(1, 9)]},
    "TS": {"name": "Telangana", "districts": [str(i).zfill(2) for i in range(1, 34)]},
    "UK": {"name": "Uttarakhand", "districts": [str(i).zfill(2) for i in range(1, 14)]},
    "UP": {"name": "Uttar Pradesh", "districts": [str(i).zfill(2) for i in range(1, 76)]},
    "WB": {"name": "West Bengal", "districts": [str(i).zfill(2) for i in range(1, 24)]}
}

def generate_vehicle_number() -> str:

    state_code = random.choice(list(STATE_CODES.keys()))

    if state_code is not None:
        state_code = state_code.upper()
        if state_code not in STATE_CODES:
            raise ValueError(f"Invalid state code: {state_code}")
    else:
        state_code = random.choice(list(STATE_CODES.keys()))

    district_code = random.choice(STATE_CODES[state_code]["districts"])
    
    valid_letters = [c for c in string.ascii_uppercase if c not in ['O', 'I']]
    series = ''.join(random.choices(valid_letters, k=2))
    number = str(random.randint(1, 9999)).zfill(4)
    
    return f"{state_code} {district_code} {series} {number}"