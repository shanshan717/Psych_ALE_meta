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
# !pip install atlasreader

# %%
from os import makedirs, path

import numpy as np
import pandas as pd
from atlasreader import get_statmap_info
from IPython.display import display
from nilearn import image

# %% [markdown]
# We apply this function to create the Cluster Tables 2–6. These present the results of all of our ALE, subtraction, and SDM analyses.

# %%
# Define function to print the clusters from multiple images as a table
def combined_cluster_table(
    img_files_z=[],
    img_files_ale=[],
    stub_keys=[],
    stub_colname="Analysis",
    atlas="harvard_oxford",
    td_jar=None,
    output_file="cluster_table.tsv",
):

    # Create output director
    output_dir = path.dirname(output_file)
    makedirs(output_dir, exist_ok=True)

    # Create a list of DataFrames with peak and cluster stats for each image
    df_tuples = [
        get_statmap_info(img_file, cluster_extent=0, atlas="harvard_oxford", voxel_thresh=0)
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
            get_statmap_info(img_file, cluster_extent=0, atlas="harvard_oxford", voxel_thresh=0)
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

# %%
# Create ALE results Table
tab2 = combined_cluster_table(
    img_files_z=[
        "/Users/ss/Desktop/psych_meta/output/ale/unhealth_z_thresh.nii.gz", # 这里的图像要根据ALE的结果来
    ],
    stub_keys=[
        "Activation likelihood estimation",
    ],
    stub_colname="Analysis",
    img_files_ale=[
        "/Users/ss/Desktop/psych_meta/output/ale/unhealth_stat_thresh.nii.gz", # 这里的图像是z转换后的结果
    ],
    atlas="harvard_oxford",
    output_file="/Users/ss/Desktop/psych_meta/output/ale/tabALE.tsv",
)

# Create Table 6 (comparison with adults)
tab6 = combined_cluster_table(
    img_files_z=[
        "../results/adults/children_conj_adults_z.nii.gz",
    ],
    stub_keys=["Conjunction"],
    stub_colname="Analysis",
    img_files_ale=[
        "../results/adults/children_conj_adults_ale.nii.gz",
    ],
    atlas="harvard_oxford",
    output_file="output",
)
display(tab6)