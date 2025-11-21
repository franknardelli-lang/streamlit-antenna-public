"""
CSV Antenna Sweep Data Processor

This script processes antenna measurement CSV files containing two sweep datasets 
representing electric field strength (in dBµV/m) versus angle. It is designed to clean,
align, combine, and output processed data for further analysis.

Key Functionality:
- Prompts the user to select a folder containing CSV files.
- Reads each CSV file assuming at least two columns: angle and field strength.
- Detects the "sweep break" where the angle data resets (angle decreases).
- Splits data into two sweeps based on this break.
- Cleans repeated rows at the start of the second sweep (up to 5 duplicates).
- Averages duplicate angle entries in the second sweep to align data.
- Interpolates the second sweep's field values onto the first sweep's angle points.
- Converts field strengths from dBµV/m to linear V/m scale.
- Combines the two sweeps using a Pythagorean sum of the field strengths.
- Converts the combined field strength back to dBµV/m.
- Saves the processed data to new CSV files with '_processed.csv' suffix.

Usage:
- Run the script.
- Select the folder containing raw CSV files.
- The script processes all CSV files in the folder and writes processed versions.

Dependencies:
- Python standard libraries: os, tkinter
- Third-party libraries: numpy, pandas, scipy

This tool is useful for antenna engineers and researchers needing to merge and clean
multiple sweep measurements before further analysis or visualization.

Author: [Your Name]
Date: [Date]
"""


import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from tkinter import Tk
from tkinter.filedialog import askdirectory

def process_all_csvs():
    # Hide main tkinter window
    Tk().withdraw()
    folder_path = askdirectory(title='Select folder containing CSV files')
    if not folder_path:
        print('No folder selected. Exiting.')
        return

    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
    print(f'Found {len(csv_files)} CSV files in {folder_path}')
    if not csv_files:
        return

    for filename in csv_files:
        in_path = os.path.join(folder_path, filename)
        print(f'Processing "{filename}"...')
        try:
            # 1) Read CSV, assuming header in first row
            df = pd.read_csv(in_path)
            if df.shape[1] < 2:
                print('  Skipping: fewer than 2 columns')
                continue

            angles = df.iloc[:,0].values
            f1_dBuV_m = df.iloc[:,1].values

            # 2) Find sweep break where angle decreases
            d = np.diff(angles)
            brk_indices = np.where(d < 0)[0]
            if len(brk_indices) == 0:
                print('  No clear sweep break found. Skipping.')
                continue
            brk = brk_indices[0]

            ang1 = angles[:brk+1]
            f1 = f1_dBuV_m[:brk+1]
            ang2 = angles[brk+1:]
            f2_dBuV_m = f1_dBuV_m[brk+1:]

            # 3) Clean repeated leading rows in sweep 2 (up to 5)
            keep = np.ones(len(ang2), dtype=bool)
            for k in range(1, min(5, len(ang2))):
                if ang2[k] == ang2[k-1] and f2_dBuV_m[k] == f2_dBuV_m[k-1]:
                    keep[k] = False
            ang2 = ang2[keep]
            f2_dBuV_m = f2_dBuV_m[keep]

            # 4) Align sweeps by averaging duplicates in sweep 2
            df2 = pd.DataFrame({'angle': ang2, 'field': f2_dBuV_m})
            df2_mean = df2.groupby('angle').mean().reset_index()

            # Interpolate sweep 2 onto sweep 1 angles
            interp_func = interp1d(df2_mean['angle'], df2_mean['field'],
                                   kind='linear', fill_value='extrapolate')
            f2_on_1 = interp_func(ang1)

            # 5) Convert dBµV/m to V/m
            f1_V_per_m = 10 ** ((f1 - 120) / 20)
            f2_V_per_m = 10 ** ((f2_on_1 - 120) / 20)

            # 6) Pythagorean sum
            total_V_per_m = np.sqrt(f1_V_per_m**2 + f2_V_per_m**2)

            # 7) Convert back to dBµV/m
            total_dBuV_m = 20 * np.log10(total_V_per_m) + 120

            # 8) Write output CSV
            out_df = pd.DataFrame({
                'Angle': ang1,
                'Field1': f1,
                'Field2': f2_on_1,
                'TotalField': total_dBuV_m
            })
            out_name = os.path.join(folder_path, filename.replace('.csv', '_processed.csv'))
            out_df.to_csv(out_name, index=False)
            print(f'  Wrote {out_name}')

        except Exception as e:
            print(f'Error processing {filename}: {e}')

if __name__ == "__main__":
    process_all_csvs()