# ![SkeideLab and MPI CBS logos](../misc/header_logos.png)
#
# # Notebook #08: Output Figures
#
# *Created April 2021 by Alexander Enge* ([enge@cbs.mpg.de](mailto:enge@cbs.mpg.de))
#
# This notebooks contains the code that we've used to create publication-ready figures from the statistical maps that we've created in the previous notebooks. We did not add any explanatory text because no substantial work is happening here and the solutions we've used are very idiosyncratic to the present meta-analysis. Also, most of what is happening should hopefully become clear from the code itself and the comments. For most figures, we rely heavily on Nilearn's `plot_glass_brain()` function and combine multiple of these glass brains using matplotlib's `gridspec` syntax. Note that there is no code for Figure 1 (showing the literature search and selection process in the form of a [PRISMA flowchart](https://doi.org/10.1136/bmj.n71)). This is because this figure was created manually using [LibreOffice Impress](https://www.libreoffice.org).

from os import makedirs

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from nilearn import image, plotting
from scipy import stats
from scipy.stats import pearsonr
# 绘制绘图的函数
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




# mpl.rcParams.update({"font.family": ["Liberation Sans"], "font.size": 12})

# Create output directory
output_dir = "output/ale"
makedirs(output_dir, exist_ok=True)

# Define scaling factor so we can set all the figure sizes in scaling gpt
scaling = 2 / 30  # Scaling factor for resizing figures
figsize = (90 * scaling, 145 * scaling)  # Figure size based on scaling

# Create the figure and gridspec layout
fig1 = plt.figure(figsize=figsize)
gs = fig1.add_gridspec(145, 90)

# Add subplot for plotting the brain images
ax1 = fig1.add_subplot(gs[70:95, :]) # Define the area for the subplot

# Set color normalization and parameters for plotting
alpha = 0.8  # Transparency setting for the plots
vmax_viridis = 2 / 0.75  # Max value for viridis colormap normalization
norm = mpl.colors.Normalize(vmin=0, vmax=vmax_viridis, clip=True)  # Color normalization

# Define vmin and vmax for the Z-score color range
vmin, vmax = 0, 8  # Z-score range for coloring

# Plot z-maps from ALE
img_unhealth = image.load_img("output/ale/patients/health_z_thresh.nii.gz")
p3 = plotting.plot_glass_brain(None, display_mode="lyrz", axes=ax1)
p3.add_overlay(img_unhealth, cmap="YlOrRd", vmin=vmin, vmax=vmax)

plt.show()

# Save the figure as PNG and PDF formats
fig2.savefig("output/figures/fig2.png", dpi=300)
fig2.savefig("output/figures/fig2.pdf")