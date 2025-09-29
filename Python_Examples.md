Examples in Python

Setup & Load Libraries and load data

```Python
import pandas as pd
# Choose which dataset folder to use

# Comment this to switch datasets

#dataset_choice = "full_dataset"
#dataset_choice = "p01_one_percent_random_subset"
dataset_choice = "p05_five_percent_random_subset"


# Construct the base path dynamically
base_path = f"/content/drive/MyDrive/{dataset_choice}"

# Load Parquet files
papers = pd.read_parquet(f"{base_path}/papers.parquet")
mentions = pd.read_parquet(f"{base_path}/mentions.pdf.parquet")
purposes = pd.read_parquet(f"{base_path}/purpose_assessments.pdf.parquet")

# Quick peek
print("Using dataset:", dataset_choice)
print("Papers:", papers.shape)
print("Mentions:", mentions.shape)
print("Purposes:", purposes.shape)
```

1. How many papers mention OpenStreetMap?

This example filters by `software_normalied` as this is less noisy than `software_raw`.

```Python
openstreetmap_papers = (
    mentions[mentions["software_normalized"] == "OpenStreetMap"]
    .drop_duplicates(subset="paper_id")   # distinct paper_id
)

count = openstreetmap_papers["paper_id"].nunique()
print("Number of papers mentioning OpenStreetMap:", count)

#Number of papers mentioning OpenStreetMap: 376
```

2. How did the number of papers referencing STATA each year change from 2000-2020?

By joining the Mentions table with Papers, we can compute statistics requiring access to paper metadata. Analyses like these are why we include fields such as `paper_id` in Mentions, even though it denormalizes the tables.

```Python
stata_mentions = (
    mentions[mentions["software_normalized"] == "STATA"]
    [["paper_id"]].drop_duplicates()
)

stata_by_year = (
    stata_mentions.merge(papers, on="paper_id", how="inner")
    .query("2000 <= published_year <= 2020")
    .groupby("published_year")
    .size()
    .reset_index(name="n")
    .sort_values("published_year")
)

print(stata_by_year)

    published_year    n
0             2000   11
1             2001   14
2             2002   20
3             2003   29
4             2004   51
5             2005   32
6             2006   42
7             2007   49
8             2008   77
9             2009   87
10            2010  107
11            2011  122
12            2012  139
13            2013  172
14            2014  169
15            2015  208
16            2016  268
17            2017  291
18            2018  310
19            2019  382
20            2020  485

```

3. What are the most popular software packages used since 2020, by number of distinct papers?

Answering this question requires joining all three tables.
Especially with the full dataset, we generally recommend using `select` statements before and after joins to reduce memory overhead.
Here we use the PurposeAssessments table to evaluate whether software was "used" in a paper.
The "document" scope is appropriate here as we're interested in whether the software was used by the paper, not whether particular mentions of the software indicate this.

```Python

popular_software = (
    papers.query("published_year >= 2020")[["paper_id"]]
    .merge(mentions[["software_mention_id", "software_normalized", "paper_id"]],
           on="paper_id", how="inner")
    .merge(purposes[["software_mention_id", "scope", "purpose", "certainty_score"]],
           on="software_mention_id", how="inner")
    .query("scope == 'document' and purpose == 'used' and certainty_score > 0.5")
    [["paper_id", "software_normalized"]]
    .drop_duplicates()
    .groupby("software_normalized")
    .size()
    .reset_index(name="n")
    .sort_values("n", ascending=False)
)

print(popular_software.head(10))  # show top 10

      software_normalized      n
53354                SPSS  22596
25325      GraphPad Prism   8080
18712               Excel   6131
28455              ImageJ   5477
33089              MATLAB   5117
51852                 SAS   3480
53497     SPSS Statistics   3065
58191               Stata   2545
77218              script   2247
35936              Matlab   2225

```
