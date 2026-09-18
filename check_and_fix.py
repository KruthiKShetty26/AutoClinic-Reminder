import os, pandas as pd, shutil, json
from datetime import datetime, timedelta

base_dir = r"C:\Users\Kruthi K Shetty\OneDrive\Documents\UiPath\AutoClinic-Reminder"
data_dir = os.path.join(base_dir, "Data")
lab_out_dir = os.path.join(base_dir, "Lab_Outputs")
arch_dir = os.path.join(base_dir, "Archived_Reports")

# Load appointments.csv
appts_path = os.path.join(data_dir, "appointments.csv")
appt_df = pd.read_csv(appts_path)

# Current time (local)
now = datetime.now()
# For reproducibility, also parse from system message if needed, but use now.

# Extract timestamps
def parse_ts(ts_str):
    return datetime.strptime(str(ts_str).strip(), "%m/%d/%Y %I:%M %p")

appt_df['Parsed_TS'] = appt_df['Appointment Timestamp'].apply(parse_ts)

# Compute differences in hours
appt_df['DiffHours'] = (appt_df['Parsed_TS'] - now).dt.total_seconds() / 3600

# Determine which rows are within 24-48h
appt_df['InWindow'] = appt_df['DiffHours'].apply(lambda x: 24 <= x <= 48)

# Identify Anjali row
anjali_idx = appt_df[appt_df['Patient Name'].str.contains('Anjali')].index[0]
anjali_diff = appt_df.at[anjali_idx, 'DiffHours']

# If Anjali not in window, set new timestamp 30h from now
new_timestamp_str = None
if not (24 <= anjali_diff <= 48):
    new_dt = now + timedelta(hours=30)
    # Use a format string that works on both Unix and Windows.
    try:
        new_timestamp_str = new_dt.strftime('%-m/%-d/%Y %I:%M %p')
    except ValueError:
        # Windows uses %# for no‑leading‑zero month/day.
        new_timestamp_str = new_dt.strftime('%#m/%#d/%Y %I:%M %p')
    appt_df.at[anjali_idx, 'Appointment Timestamp'] = new_timestamp_str
    # Also update Parsed_TS and DiffHours for consistency
    appt_df.at[anjali_idx, 'Parsed_TS'] = new_dt
    appt_df.at[anjali_idx, 'DiffHours'] = (new_dt - now).total_seconds() / 3600
    appt_df.at[anjali_idx, 'InWindow'] = 24 <= appt_df.at[anjali_idx, 'DiffHours'] <= 48

# Save back to CSV (overwrite)
appt_df.drop(columns=['Parsed_TS','DiffHours','InWindow'], inplace=True)
appt_df.to_csv(appts_path, index=False)

# ---------- PDF Checks ----------
missing_pdfs = []
for pid in [98044, 98045]:
    fname = f"PAT_{pid}_Report.pdf"
    src = os.path.join(lab_out_dir, fname)
    if not os.path.isfile(src):
        # maybe in Archived_Reports
        src_arch = os.path.join(arch_dir, fname)
        if os.path.isfile(src_arch):
            shutil.move(src_arch, lab_out_dir)
            print(f"Moved {fname} from Archived_Reports back to Lab_Outputs")
        else:
            missing_pdfs.append(fname)

# ---------- Registry Checks ----------
reg_path = os.path.join(data_dir, "patients_registry.xlsx")
reg_df = pd.read_excel(reg_path)
# Ensure Patient ID column is numeric (int)
reg_df['Patient ID'] = pd.to_numeric(reg_df['Patient ID'], errors='coerce').astype('Int64')
# Trim whitespace in string columns
for col in ['Patient Name','Patient Email','Doctor Email','Status']:
    reg_df[col] = reg_df[col].astype(str).str.strip()
# Save back
reg_df.to_excel(reg_path, index=False)

# Build report
report = {
    "now": now.strftime('%Y-%m-%d %H:%M:%S'),
    "appointments": [],
    "missing_pdfs": missing_pdfs,
    "registry": {
        "ids": reg_df['Patient ID'].tolist()
    }
}
for _, row in appt_df.iterrows():
    report['appointments'].append({
        "Patient Name": row['Patient Name'],
        "Appointment Timestamp": row['Appointment Timestamp'],
        "DiffHours": (parse_ts(row['Appointment Timestamp']) - now).total_seconds() / 3600,
        "InWindow": 24 <= (parse_ts(row['Appointment Timestamp']) - now).total_seconds() / 3600 <= 48
    })

print(json.dumps(report, indent=2))
