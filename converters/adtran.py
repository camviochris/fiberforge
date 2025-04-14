import pandas as pd
import json
import re
from datetime import date

def load_profiles():
    with open("settings/adtran_profiles.json") as f:
        return json.load(f)

def find_column(columns, patterns):
    for pat in patterns:
        for col in columns:
            if re.search(pat, col, re.IGNORECASE):
                return col
    return None

def convert(df):
    profiles = load_profiles()
    default_status = 'UNASSIGNED'
    device_rows = []

    serial_col = find_column(df.columns, [r'^serial number$', r'^serial$', r'^sn$'])
    mac_col = find_column(df.columns, [r'^mac$', r'^mac address(es)?$'])
    fsan_col = find_column(df.columns, [r'^fsan$'])

    model = df.iloc[0].get('Model') or list(profiles.keys())[0]
    profile_info = profiles.get(model)
    if not profile_info:
        raise ValueError(f"Unsupported model: {model}")

    for _, row in df.iterrows():
        serial = str(row.get(serial_col, '')).strip() or 'no value'
        mac = str(row.get(mac_col, '')).strip() or 'no value'
        fsan = str(row.get(fsan_col, '')).strip() or 'no value'
        template = profile_info["template"]
        device_numbers = template.replace("<<MAC>>", mac).replace("<<SN>>", serial).replace("<<FSAN>>", fsan)
        device_rows.append({
            "device_profile": profile_info["device_profile"],
            "device_name": model,
            "device_numbers": device_numbers,
            "location": "WAREHOUSE",
            "status": default_status
        })

    today = date.today().strftime("%Y%m%d")
    file_name = f"converted_{today}_{model}.csv"
    return pd.DataFrame(device_rows), file_name
