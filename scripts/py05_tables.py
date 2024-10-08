from os import makedirs, path
from atlasreader import get_statmap_info
from IPython.display import display
from nilearn import image, plotting, reporting
from scipy import stats
from scipy.stats import pearsonr
from glob import glob
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
import os, fnmatch

import re

# We apply this function to create the Cluster Tables 2–6. These present the results of all of our ALE, subtraction, and SDM analyses.

# Define function to print the clusters from multiple images as a table
# 定义绘制表格的函数
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

# Load the ALE results
# Create ALE results Table
tab2 = combined_cluster_table(
    img_files_z=[
        "output/ale/unhealth_z_thresh.nii.gz", # 这里的图像要根据ALE的结果来
    ],
    stub_keys=[
        "Activation likelihood estimation",
    ],
    stub_colname="Analysis",
    img_files_ale=[
        "output/ale/unhealth_stat_thresh.nii.gz", # 这里的图像是z转换后的结果
    ],
    atlas="harvard_oxford",
    output_file="output/ale/tabALE1.tsv",
)
display(tab2)

# Create ALE results Table
tab3 = combined_cluster_table(
    img_files_z=[
        "output/ale/health_z_thresh.nii.gz", # 这里的图像要根据ALE的结果来
    ],
    stub_keys=[
        "Activation likelihood estimation",
    ],
    stub_colname="Analysis",
    img_files_ale=[
        "output/ale/health_stat_thresh.nii.gz", # 这里的图像是z转换后的结果
    ],
    atlas="harvard_oxford",
    output_file="output/ale/tabALE2.tsv",
)
display(tab3)

# Create Table 3 (conjunction)
tab4 = combined_cluster_table(
    img_files_z=[
        "output/conj/health_conj_unhealth_z.nii.gz",
    ],
    stub_keys=["Conjunction"],
    stub_colname="Analysis",
    img_files_ale=[
        "output/conj/health_conj_unhealth_ale.nii.gz",
    ],
    atlas="harvard_oxford",
    output_file="output/ale/tab_conj.tsv",
)
display(tab4)

# -----------------------------------------------
# individual peaks coordinates-plot
# Read table of experiments from ALE analysis
exps = pd.read_json("/Results/ALE/all_exps.json")

# Convert to categories and sort
group = ["Babies","Babies + Cry","Cry","Friendship", "Non-babies","Romance"]
exps["group"] = exps["group"].astype("category")
exps["group"].cat.reorder_categories(group, inplace=True)

# Extract all individual peaks and their z score
peaks_coords = np.array(exps["peaks_mni"].explode().tolist())

# Get task types of individual peaks
peaks_tasks = exps.explode("peaks_mni")["group"].cat.codes

# Extract all individual peaks and their z score
peaks_coords = np.array(exps["peaks_mni"].explode().tolist())

# Get indices of peaks without an effect size
idxs_p = np.where(np.isnan(peaks_coords))[0]

# Plot individual peaks

peaks = plotting.plot_markers(
    node_values=peaks_tasks,
    node_coords=peaks_coords,
    node_size=5,
    node_cmap="Set1",
    node_vmin=0.5,
    #node_vmax=2,
    alpha=0.8,
    display_mode='ortho',
    colorbar=True)

# ALE results -plot
ale_thresh_all = '/Results/ALE/all_z_size_level_thresh.nii.gz'

glass_brains_all = plotting.plot_glass_brain(ale_thresh_all, 
                                             display_mode="lyrz", 
                                             cmap="cold_white_hot", 
                                             vmin=0, vmax=5,
                                             colorbar=True)

stat_map_all_cor = plotting.plot_stat_map(ale_thresh_all, 
                                    colorbar=False, 
                                    display_mode = 'ortho',
                                    cut_coords=[-6,10,-2],
                                    draw_cross = False,
                                    cmap = "cold_white_hot", vmax=5)
