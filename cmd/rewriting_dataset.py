#This is the code which reads the old parquet files into memory again and rewrites them with improved schema and same (gzip) compression technique

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
from pathlib import Path

# === CONFIG ===
input_path = Path("/scratch/10000/.../papers.parquet")
output_path = input_path.with_name(input_path.stem + "_gzip_fixed.parquet")

# === LOAD FULL DATA INTO MEMORY ===
print("Loading full dataset into memory...")
df = pd.read_parquet(input_path, engine="pyarrow")
print(f"Loaded shape: {df.shape}")

# === CLEAN COLUMN NAMES ===
df.columns = [c.strip() for c in df.columns]

# === HANDLE NaNs AND FIX DTYPES ===
for col in df.columns:
    dtype_str = str(df[col].dtype)
    
    # Replace NaN in integer-like columns (common issue from Parquet-Go)
    if "uint" in dtype_str or "int" in dtype_str:
        # If numeric but NaNs exist, replace with 0 (safe default)
        if df[col].isna().any():
            print(f"⚠️  NaNs detected in integer column '{col}', replacing with 0.")
            df[col] = df[col].fillna(0)
        
        # Convert unsigned to signed int64
        df[col] = df[col].astype("int64")

    elif np.issubdtype(df[col].dtype, np.floating):
        # Keep as float64 (don’t downcast or convert to int)
        df[col] = df[col].astype("float64")

# === CONVERT TO PARQUET TABLE AND WRITE BACK ===
table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_table(
    table,
    output_path,
    compression="gzip",
    use_deprecated_int96_timestamps=False,
    coerce_timestamps="ms",
    write_statistics=True,   
    version="2.6" 
)

print(f"✅ Rewritten Parquet saved to: {output_path}")
print(f"Compression: gzip | Shape: {df.shape}")
