# Title: Subtraction Analysis
from os import makedirs, path
import os
import numpy as np
from IPython.display import display
from nibabel import save
from nilearn import glm, image, plotting, reporting
from nimare import io, meta

# Before doing the actual subtraction analyses, let's define a helper function for statistical thresholding. Since no FWE correction method has been defined for subtraction analyses (yet), we use an uncorrected voxel-level threshold (usually $p<.001$) combined with a cluster-level extent threshold (in mm<sup>3</sup>). Note that we assume the voxel size to be 2×2×2 mm<sup>3</sup> (the default in NiMARE).

# Define helper function for dual threshold based on voxel-p and cluster size (in mm3)
def dual_thresholding(
    img_z, voxel_thresh, cluster_size_mm3, two_sided=True, fname_out=None
):

    # If img_z is a file path, we first need to load the actual image
    img_z = image.load_img(img=img_z)

    # Check if the image is empty
    if np.all(img_z.get_fdata() == 0):
        print("THE IMAGE IS EMPTY! RETURNING THE ORIGINAL IMAGE.")
        return img_z

    # Convert desired cluster size to the corresponding number of voxels
    k = cluster_size_mm3 // 8

    # Actual thresholding
    img_z_thresh, thresh_z = glm.threshold_stats_img(
        stat_img=img_z,
        alpha=voxel_thresh,
        height_control="fpr",
        cluster_threshold=k,
        two_sided=two_sided,
    )

    # Print the thresholds that we've used
    print(
        "THRESHOLDING IMAGE AT Z > "
        + str(thresh_z)
        + " (P = "
        + str(voxel_thresh)
        + ") AND K > "
        + str(k)
        + " ("
        + str(cluster_size_mm3)
        + " mm3)"
    )

    # If requested, save the thresholded map
    if fname_out:
        save(img_z_thresh, filename=fname_out)

    return img_z_thresh

# Now we can go on to perform the actual subtraction analyses. We again define a helper function for this so we can apply this to multiple Sleuth files with a single call (and also reuse it in later notebooks). We simply read two Sleuth files into NiMARE and let its `meta.cbma.ALESubtraction()` function do the rest (as briefly described above). It outputs an unthresholded *z* score map which we then threshold using our helper function.

# Define function for performing a single ALE subtraction analysis
def run_subtraction(
    text_file1,
    text_file2,
    voxel_thresh,
    cluster_size_mm3,
    random_seed,
    n_iters,
    output_dir,
):

    # Let's show the user what we are doing
    print(
        'SUBTRACTION ANALYSIS FOR "'
        + text_file1
        + '" VS. "'
        + text_file2
        + '" WITH '
        + str(n_iters)
        + " PERMUTATIONS"
    )

    # Set a random seed to make the results reproducible
    if random_seed:
        np.random.seed(random_seed)

    # Read Sleuth files
    dset1 = io.convert_sleuth_to_dataset(text_file=text_file1)
    dset2 = io.convert_sleuth_to_dataset(text_file=text_file2)

    # Actually perform subtraction analysis
    sub = meta.cbma.ALESubtraction(n_iters=n_iters, low_memory=False)
    sres = sub.fit(dset1, dset2)

    # Save the unthresholded z map
    img_z = sres.get_map("z_desc-group1MinusGroup2")
    makedirs(output_dir, exist_ok=True)
    name1 = path.basename(text_file1).replace(".txt", "")
    name2 = path.basename(text_file2).replace(".txt", "")
    prefix = output_dir + "/" + name1 + "_minus_" + name2
    save(img_z, filename=prefix + "_z.nii.gz")

    # Create and save the thresholded z map
    dual_thresholding(
        img_z=img_z,
        voxel_thresh=voxel_thresh,
        cluster_size_mm3=cluster_size_mm3,
        two_sided=True,
        fname_out=prefix + "_z_thresh.nii.gz",
    )

# We create a dictionary of Sleuth file names which we want to subtract from one another and supply each of these contrasts to the function that we have just defined. Note that large numbers of Monte Carlo iterations (≥ 10,000) seem to be necessary to get stable results. However, this requires very large amounts of memory. You may therefore want to decrease `n_iters` when trying out this code on a small local machine or on a cloud server.

if __name__ == "__main__":

    # Create dictionary for subtraction analysis: health vs unhealth
    subtrs = dict(
        {
            "../data/health.txt":
            "../data/unhealth.txt"
        }
    )

    # Use the function to perform the actual subtraction analysis
    for key, value in subtrs.items():
        run_subtraction(
            text_file1=key,            # Path to health.txt
            text_file2=value,          # Path to unhealth.txt
            voxel_thresh=0.001,        # Set voxel threshold
            cluster_size_mm3=200,      # Set cluster size threshold
            random_seed=1234,          # Set random seed for reproducibility
            n_iters=5000,             # 这里作者用的是20000，我这里改成了1000
            output_dir="../output/ale"  # Specify your output directory
        )