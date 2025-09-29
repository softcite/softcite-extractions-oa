#This code rewrites the dataset with a consistent schema and encoding.

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Input and output paths
input_path = "/content/drive/MyDrive/full_dataset/purpose_assessments.parquet"
output_path = "/content/drive/MyDrive/full_dataset/purpose_assessments_fixed.parquet"

# Step 1: Load using pandas (PyArrow as engine ensures correct parsing)
df = pd.read_parquet(input_path, engine="pyarrow")

# Step 2: Fix schema issues (convert uint16 → int32 for cross-language compatibility)
for col in df.select_dtypes(include=["uint16"]).columns:
    df[col] = df[col].astype("int32")

# Optional: normalize column names (if Go wrote mixed cases or spaces)
df.columns = [c.strip() for c in df.columns]

# Step 3: Write back clean parquet with explicit schema
table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_table(
    table,
    output_path,
    compression="snappy",       # good balance size/speed
    use_deprecated_int96_timestamps=False,
    coerce_timestamps="ms"      # consistent timestamp handling
)

print(f"Rewritten Parquet saved to: {output_path}")
