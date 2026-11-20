# Syed Zohaib Shah, Roll Number: PSEB-2026-010729, Date: 2026-11-20

# Name: Syed Zohaib Shah
# Roll Number: PSEB-2026-010729
# Date: 20-11-2026
# Project: Online Retail Data Inspection

import pandas as pd

# Step 1: Define the dataset path
file_path = "data/raw/Online Retail.xlsx"

# Step 2: Read the Excel dataset
df = pd.read_excel(file_path)

# Step 3: Display the first five records
print("\nFIRST FIVE ROWS")
print(df.head())

# Step 4: Display the dataset shape
print("\nDATASET SHAPE")
print(df.shape)

# Step 5: Display column names
print("\nCOLUMN NAMES")
print(df.columns.tolist())

# Step 6: Display data types
print("\nDATA TYPES")
print(df.dtypes)

# Step 7: Display missing values
print("\nMISSING VALUES")
print(df.isnull().sum())

# Step 8: Display duplicate records
print("\nDUPLICATE RECORDS")
print(df.duplicated().sum())

# Step 9: Display general information
print("\nDATASET INFORMATION")
df.info()

