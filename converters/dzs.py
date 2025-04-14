import pandas as pd
import json
import re
from datetime import date

def load_profiles():
    with open("settings/dzs_profiles.json") as f:
        return json.load(f)

def detect_device_name(description):
    desc = description.strip()
    if desc.startswith("SDG 854-V6"):
        return "SDG854-V6"
    elif desc.startswith("SDG 841-T6"):
        return "SDG841-T6"
    elif desc.startswith("SDG8612"):
        return "SDG8612"
    elif desc.startswith("SDX630"):
        return "SDX630"
    elif desc.startswith("SDX622V"):
        return "SDX622V"
    elif desc.startswith("DZS-611"):
        return "DZS-611"
    elif desc.startswith("DZS-622"):
        return "DZS-622"
    elif desc.startswith("DZS-632"):
        return "DZS-632"
    else:
        return desc

def convert(df):
    profiles = load_profiles()
    default_status = 'UNASSIGNED'
    default_location = 'WAREHOUSE'
    device_rows = []

    serial_col = next((col for col in df.columns if re.search(r'serial', col, re.IGNORECASE)), None)
    mac_col = next((col for col in df.columns if re.search(r'mac', col, re.IGNORECASE)), None)
    desc_col = next((col for col in df.columns if re.search(r'description', col, re.IGNORECASE)), None)

    if not serial_col or not mac_col or not desc_col:
        raise ValueError("Missing required columns: Serial, MAC, or Description.")

    for _, row in df.iterrows():
        serial = str(row.get(serial_col, '')).strip() or 'no value'
        mac = str(row.get(mac_col, '')).strip() or 'no value'
        desc = str(row.get(desc_col, '')).strip() or 'no value'
        device_name = detect_device_name(desc)
        profile = profiles.get(device_name)

        if not profile:
            continue

        template = profile["template"]
        device_numbers = template.replace("<<MAC>>", mac).replace("<<SN>>", serial).replace("<<FSAN>>", "no value")
        device_rows.append({
            "device_profile": profile["device_profile"],
            "device_name": device_name,
            "device_numbers": device_numbers,
            "location": default_location,
            "status": default_status
        })

    today = date.today().strftime("%Y%m%d")
    file_name = f"converted_{today}_dzs.csv"
    return pd.DataFrame(device_rows), file_name
