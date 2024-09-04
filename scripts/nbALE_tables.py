# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ![SkeideLab and MPI CBS logos](../misc/header_logos.png)
#
# # Notebook #07: Output Tables
#
# *Created April 2021 by Alexander Enge* ([enge@cbs.mpg.de](mailto:enge@cbs.mpg.de))
#
# This notebook contains a convenience function that we've used to create all of the tables for our manuscript. We only comment on these sparsely since no substantial work is happening here and because the solutions we've used are very idiosyncratic to the present meta-analysis. Also note that the tables still required a bit of post-processing, such as turning the anatomical peak labels from abbreviations into plain language.

# %%
!pip install atlasreader

# %%
from os import makedirs, path

import numpy as np
import pandas as pd
from atlasreader import get_statmap_info
from IPython.display import display
from nilearn import image

# %% [markdown]
# Table 1 in the manuscript provides descriptive information about the experiments included in the meta-analysis. This information was originally stored in the file `data/literature_search/included.csv`. It was then updated with some additional information in the previous notebooks and stored as a new file called `results/exps.json`. Here we load this into a DataFrame and compute some summary statistics which are reported in the paper (such as the overall sample size of children and their mean age).

# %%
# Read included experiments (Table 1)
"""
exps = pd.read_json("../results/exps.json")
exps["peaks"] = [np.array(peaks, dtype="float") for peaks in exps["peaks"]]
exps["n_peaks"] = [len(peaks) for peaks in exps["peaks"]]

# Compute summary statistics
_ = [
    print(
        col + ":",
        "sum",
        exps[col].sum(),
        "mean",
        exps[col].mean(),
        "median",
        exps[col].median(),
        "min",
        exps[col].min(),
        "max",
        exps[col].max(),
    )
    for col in ["n", "age_mean", "age_min", "age_max", "n_peaks"]
]

# Compute weighted mean age
exps["age_mean_weighted"] = [age * n for age, n in zip(exps["age_mean"], exps["n"])]
print("weighted mean age:", exps["age_mean_weighted"].sum() / exps["n"].sum())

# Compute sex and handedness ratios
print(exps["sex_female"].sum() / (exps["sex_female"].sum() + exps["sex_male"].sum()))
print(exps["hand_right"].sum() / (exps["hand_right"].sum() + exps["hand_left"].sum()))

# Count peaks with and without effect sizes
tstats = exps["tstats_corr"].explode()
print(len(tstats[tstats != "p"]))
print(len(tstats[tstats != "p"]) / len(tstats))
print(len(tstats[tstats == "p"]))

# Cut peaks in left vs. right hemisphere
peaks = exps["peaks_mni"].explode()
peaks_x = [focus[0] for focus in peaks]
peaks_left = [x for x in peaks_x if x < 0]
print(len(peaks_left))
print(len(peaks_left) / len(peaks_x))
"""
# %% [markdown]
# This next block is a helper function to create a cluster table from multiple *z* score maps. 
# It also has an option to add ALE values if a corresponding ALE value map happens to be available 
# (note that this is not the case for subtraction analyses and SDM maps). 
# The function also looks up anatomical labels for each cluster and 
# its peak based on the anatomic automatic labeling atlas (AAL2; Rolls et al., 2015, *NeuroImage*) 
# as implemented in the AtlasReader package (Notter et al., 2019, *J Open Source Softw*).

# %%
# Define function to print the clusters from multiple images as a table
def combined_cluster_table(
    img_files_z=[],
    img_files_ale=[],
    stub_keys=[],
    stub_colname="Analysis",
    atlas="aal",
    td_jar=None,
    output_file="cluster_table.tsv",
):

    # Create output director
    output_dir = path.dirname(output_file)
    makedirs(output_dir, exist_ok=True)

    # Create a list of DataFrames with peak and cluster stats for each image
    df_tuples = [
        get_statmap_info(img_file, cluster_extent=0, atlas="aal", voxel_thresh=0)
        for img_file in img_files_z
    ]
    dfs = [
        pd.DataFrame(
            {
                "Cluster #": df_tuple[0]["cluster_id"],
                "Size (mm3)": df_tuple[0]["volume_mm"],
                "Cluster labels": df_tuple[0][atlas],
                "Mean z": df_tuple[0]["cluster_mean"],
                "Peak z": df_tuple[1]["peak_value"],
                "Peak X": df_tuple[1]["peak_x"],
                "Peak Y": df_tuple[1]["peak_y"],
                "Peak Z": df_tuple[1]["peak_z"],
                "Peak label": df_tuple[1][atlas],
            }
        )
        for df_tuple in df_tuples
    ]

    # Add ALE values if available
    if img_files_ale:
        df_tuples_ale = [
            get_statmap_info(img_file, cluster_extent=0, atlas="aal", voxel_thresh=0)
            if img_file
            else (
                pd.DataFrame({"cluster_mean": [float("nan")]}),
                pd.DataFrame({"peak_value": [float("nan")]}),
            )
            for img_file in img_files_ale
        ]
        dfs_ale = [
            pd.DataFrame(
                {
                    "Mean ALE": df_tuple[0]["cluster_mean"],
                    "Peak ALE": df_tuple[1]["peak_value"],
                }
            )
            for df_tuple in df_tuples_ale
        ]
        for df, df_ale in zip(dfs, dfs_ale):
            df.insert(4, column="Mean ALE", value=df_ale["Mean ALE"])
            df.insert(6, column="Peak ALE", value=df_ale["Peak ALE"])

    # Concatenate into one big DataFrame
    df = pd.concat(dfs, keys=stub_keys)

    # Reformat numerical columns
    df["Size (mm3)"] = df["Size (mm3)"].apply(lambda x: "{:,.0f}".format(x))
    cols_int = ["Cluster #", "Peak X", "Peak Y", "Peak Z"]
    df[cols_int] = df[cols_int].applymap(int)
    cols_2f = ["Mean z", "Peak z"]
    df[cols_2f] = df[cols_2f].applymap(lambda x: "{:,.2f}".format(x))
    if img_files_ale:
        cols_3f = ["Mean ALE", "Peak ALE"]
        df[cols_3f] = df[cols_3f].applymap(lambda x: "{:,.3f}".format(x))
        df[cols_3f] = df[cols_3f].replace("nan", "")

    # Add the stub column
    df.index = df.index.set_names(stub_colname, level=0)
    df.reset_index(level=stub_colname, inplace=True)
    mask = df[stub_colname].duplicated()
    df.loc[mask.values, [stub_colname]] = ""

    # Save to CSV
    df.to_csv(output_file, sep="\t", index=False)

    return df


# %% [markdown]
# We apply this function to create the Cluster Tables 2–6. These present the results of all of our ALE, subtraction, and SDM analyses.

# %%
# Create Table 2 (ALE & SDM results) 主要看table2的代码
tab2 = combined_cluster_table(
    img_files_z=[
        "../results/ale/all_z_thresh.nii.gz",
        "../results/sdm/analysis_mod1/mod1_z_thresh.nii.gz",
        "../results/sdm/analysis_mod2/mod2_z_thresh.nii.gz",
    ],
    stub_keys=[
        "Activation likelihood estimation",
        "Seed-based d mapping",
        "With covariates",
    ],
    stub_colname="Analysis",
    img_files_ale=[
        "../results/ale/all_stat_thresh.nii.gz",
        None,
        None,
    ],
    atlas="aal",
    output_file="../results/tables/tab2_children.tsv",
)
display(tab2)


# %%
# Create Table 3 (task category ALEs)
tab3 = combined_cluster_table(
    img_files_z=[
        "../results/ale/knowledge_z_thresh.nii.gz",
        "../results/ale/relatedness_z_thresh.nii.gz",
        "../results/ale/objects_z_thresh.nii.gz",
    ],
    stub_keys=[
        "Knowledge",
        "Relatedness",
        "Objects",
    ],
    stub_colname="Analysis",
    img_files_ale=[
        "../results/ale/knowledge_stat_thresh.nii.gz",
        "../results/ale/relatedness_stat_thresh.nii.gz",
        "../results/ale/objects_stat_thresh.nii.gz",
    ],
    atlas="aal",
    output_file="../results/tables/tab3_tasks.tsv",
)
display(tab3)