"""
SoftCite dataset subsampling tool in Python.
Replicates the Go version functionality in Python
"""

import os
import random
from pathlib import Path
from typing import List, Set
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Constants
BATCH_SIZE = 1 << 20  # 1MB batch size
PAPERS_NAME = "papers"
MENTIONS_NAME = "mentions"
PURPOSE_ASSESSMENTS_NAME = "purpose_assessments"
PARQUET_EXT = ".parquet"
PAPER_ID_FIELD_NAME = "paper_id"
HAS_MENTIONS_FIELD_NAME = "has_mentions"

# Fixed input/output directories in code (Give path of your input and output folder here)
INPUT_DIR = r"/content/drive/"
OUTPUT_DIR = r"/content/drive/"

# Fixed seed
RANDOM_SEED = 42

# Fixed partitions (fractions that sum up to 1)
PARTITIONS = [0.01,0.05]  # Example: 1% sample, 5% sample

def calculate_thresholds(partitions: List[float]) -> List[float]:
    """Convert partition sizes to cumulative thresholds."""
    thresholds = []
    cumulative = 0.0
    for partition in partitions:
        cumulative += partition
        thresholds.append(cumulative)
    return thresholds

def get_partitions(
    papers_path: str, 
    seed: int, 
    thresholds: List[float]
) -> List[Set[int]]:
    """
    Get paper partitions by randomly sampling papers with mentions.
    
    Args:
        papers_path: Path to papers parquet file
        seed: Random seed
        thresholds: Cumulative partition thresholds
        
    Returns:
        List of sets containing paper IDs for each partition
    """
    random.seed(seed)
    partitions = [set() for _ in thresholds]
    
    parquet_file = pq.ParquetFile(papers_path)
    for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE,
                                           columns=[PAPER_ID_FIELD_NAME, HAS_MENTIONS_FIELD_NAME]):
        df = batch.to_pandas()
        papers_with_mentions = df[df[HAS_MENTIONS_FIELD_NAME] == True]
        for _, row in papers_with_mentions.iterrows():
            paper_id = row[PAPER_ID_FIELD_NAME]
            rand_value = random.random()
            for i, threshold in enumerate(thresholds):
                if rand_value < threshold:
                    partitions[i].add(paper_id)
                    break
    return partitions

def partition_parquet(
    input_path: str,
    output_path: str, 
    partitions: List[Set[int]]
) -> None:
    """
    Partition a parquet file based on paper ID partitions.
    
    Args:
        input_path: Input parquet file path
        output_path: Base output path (will add partition numbers)
        partitions: List of paper ID sets for each partition
    """
    if not os.path.exists(input_path):
        print(f"Warning: Input file {input_path} does not exist, skipping...")
        return
    
    parquet_file = pq.ParquetFile(input_path)
    schema = parquet_file.schema.to_arrow_schema()

    
    output_paths = []
    writers = []
    for i in range(len(partitions)):
        base_path = Path(output_path)
        partition_path = base_path.parent / f"{base_path.stem}_{i}{base_path.suffix}"
        output_paths.append(str(partition_path))
        writer = pq.ParquetWriter(
            str(partition_path),
            schema,
            compression='gzip',
            compression_level=9
        )
        writers.append(writer)
    
    try:
        for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
            df = batch.to_pandas()
            if PAPER_ID_FIELD_NAME not in df.columns:
                print(f"Warning: {PAPER_ID_FIELD_NAME} column not found in {input_path}")
                continue
            partition_dfs = [[] for _ in partitions]
            for _, row in df.iterrows():
                paper_id = row[PAPER_ID_FIELD_NAME]
                for partition_idx, partition in enumerate(partitions):
                    if paper_id in partition:
                        partition_dfs[partition_idx].append(row)
                        break
            for i, rows in enumerate(partition_dfs):
                if rows:
                    partition_df = pd.DataFrame(rows)
                    partition_table = pa.Table.from_pandas(partition_df, schema=schema)
                    writers[i].write_table(partition_table)
    finally:
        for writer in writers:
            writer.close()

def main():
    """Main function"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    thresholds = calculate_thresholds(PARTITIONS)
    seed = RANDOM_SEED
    print(f"Using seed: {seed}")
    
    papers_path = os.path.join(INPUT_DIR, PAPERS_NAME + PARQUET_EXT)
    paper_partitions = get_partitions(papers_path, seed, thresholds)
    
    for i, partition in enumerate(paper_partitions):
        print(f"Partition {i}: {len(partition)} papers")
    
    out_papers = os.path.join(OUTPUT_DIR, PAPERS_NAME + PARQUET_EXT)
    partition_parquet(papers_path, out_papers, paper_partitions)
    
    in_mentions = os.path.join(INPUT_DIR, MENTIONS_NAME + PARQUET_EXT)
    out_mentions = os.path.join(OUTPUT_DIR, MENTIONS_NAME + PARQUET_EXT)
    partition_parquet(in_mentions, out_mentions, paper_partitions)
    
    in_assessments = os.path.join(INPUT_DIR, PURPOSE_ASSESSMENTS_NAME + PARQUET_EXT)
    out_assessments = os.path.join(OUTPUT_DIR, PURPOSE_ASSESSMENTS_NAME + PARQUET_EXT)
    partition_parquet(in_assessments, out_assessments, paper_partitions)
    
    print("Subsampling completed successfully!")

if __name__ == "__main__":
    main()

