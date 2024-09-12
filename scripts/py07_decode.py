# Discrete functional decoding
import os

import nibabel as nib
import numpy as np
from nilearn.plotting import plot_roi

from nimare.dataset import Dataset
from nimare.decode import discrete
from nimare.utils import get_resource_path

# Run the decoder
decoder = discrete.BrainMapDecoder(correction=None)
decoder.fit(dset)
decoded_df = decoder.transform(ids=ids)
decoded_df.sort_values(by="probReverse", ascending=False).head()