import pandas as pd
import os

# Paths
excel_path = r"C:\Users\Kruthi K Shetty\OneDrive\Documents\UiPath\AutoClinic-Reminder\Data\patients_registry.xlsx"
csv_path   = r"C:\Users\Kruthi K Shetty\OneDrive\Documents\UiPath\AutoClinic-Reminder\Data\patients_registry.csv"

# Load Excel (ensure Patient ID stays numeric)
df = pd.read_excel(excel_path, dtype={'Patient ID': int})

# Save as CSV, overwriting any existing file
df.to_csv(csv_path, index=False)

# Read back the CSV to confirm contents
confirmed = pd.read_csv(csv_path, dtype={'Patient ID': int})
print("--- patients_registry.csv content ---")
print(confirmed.to_string(index=False))

# Verify all expected IDs are present
expected_ids = {98042, 98043, 98044, 98045}
actual_ids = set(confirmed['Patient ID'].tolist())
missing = expected_ids - actual_ids
if missing:
    print(f"Missing IDs: {missing}")
else:
    print("All 4 patient IDs are present.")
