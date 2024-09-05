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

# 加载必要的包
from os import makedirs, path
import os
import numpy as np
import pandas as pd
from IPython.display import display
from nibabel import save
from nilearn import image, plotting, reporting
from nimare import correct, io, meta, utils #主要用nimare完成元分析
from scipy.stats import norm


# We are now ready to perform the actual ALE analyses with NiMARE. 
# We write a custom function which takes a single Sleuth text file as its input and (a) calculates the ALE map, 
# (b) corrects for multiple comparisons using a Monte Carlo-based FWE correction, 
# and (c) stores the cluster level-thresholded maps into the output directory. 
# We then apply this function to all the Sleuth files we have created in the previous step. 

# Define function for performing a single ALE analysis with FWE correction
def run_ale(text_file, voxel_thresh, cluster_thresh, random_seed, n_iters, output_dir):

    # Let's show the user what we are doing
    print("ALE ANALYSIS FOR '" + text_file + "' WITH " + str(n_iters) + " PERMUTATIONS")

    # Set a random seed to make the results reproducible
    if random_seed:
        np.random.seed(random_seed)

    # Perform the ALE
    # target默认的是'ale_2mm'和'mni152_2mm'两种，这里我们选择'mni152_2mm'
    dset = io.convert_sleuth_to_dataset(text_file="data/health.txt", target="mni152_2mm") 
    ale = meta.cbma.ALE()
    res = ale.fit(dset)

    # FWE correction for multiple comparisons
    corr = correct.FWECorrector(
        method="montecarlo", voxel_thresh=voxel_thresh, n_iters=n_iters
    )
    cres = corr.transform(result=res)

    # Save unthresholded maps to the ouput directory
    prefix = path.basename(text_file).replace(".txt", "")
    res.save_maps(output_dir=output_dir, prefix=prefix)
    cres.save_maps(output_dir=output_dir, prefix=prefix)

    # Create cluster-level thresholded z and ALE maps
    img_clust = cres.get_map("z_desc-mass_level-cluster_corr-FWE_method-montecarlo")
    img_z = cres.get_map("z")
    img_ale = cres.get_map("stat")
    cluster_thresh_z = norm.ppf(1 - cluster_thresh / 2)
    img_clust_thresh = image.threshold_img(img=img_clust, threshold=cluster_thresh_z)
    img_mask = image.math_img("np.where(img > 0, 1, 0)", img=img_clust_thresh)
    img_z_thresh = image.math_img("img1 * img2", img1=img_mask, img2=img_z)
    img_ale_thresh = image.math_img("img1 * img2", img1=img_mask, img2=img_ale)

    # Save thresholded maps to the output directory
    save(img=img_z_thresh, filename=output_dir + "/" + prefix + "_z_thresh.nii.gz")
    save(img=img_ale_thresh, filename=output_dir + "/" + prefix + "_stat_thresh.nii.gz")
    # Return `cres` object for external use
    return cres

# 运行ALE分析
if __name__ == "__main__":
    # 输入疾病患者的Sleuth文件
    sleuth_file = "data/health.txt"

    # 应用我们定义的 run_ale 函数
    cres = run_ale(
        text_file=sleuth_file,
        voxel_thresh=0.001,
        cluster_thresh=0.05,
        random_seed=1234,
        n_iters=5000,  
        output_dir="data",
    )


# Finally, let's look at some exemplary results by plotting the (cluster-level FWE-corrected) *z* score map from the main analysis (including all semantic experiments). We also print a table of the corresponding cluster statistics.

# %%
if __name__ == "__main__":

    # Glass brain example
    img = image.load_img("data/health_z.nii.gz")
    p = plotting.plot_glass_brain(img, display_mode="lyrz", colorbar=True)

    # Cluster table example
    t = reporting.get_clusters_table(img, stat_threshold=0, min_distance=1000)
    display(t)

    print(cres.maps.keys())
