# Discrete functional decoding
import os

import nibabel as nib
import numpy as np
from nilearn.plotting import plot_roi

from nimare.dataset import Dataset
from nimare.decode import discrete
from nimare.utils import get_resource_path

from nimare.io import convert_sleuth_to_dataset
from nimare.decode import discrete

# 假设 sleuth_file.txt 是你准备好的 Sleuth 格式数据文件
sleuth_file = "/Users/ss/Documents/Psych_ALE_meta/data/unhealth.txt"

# 将 Sleuth 格式的数据转换为 NiMARE Dataset 对象
dset = convert_sleuth_to_dataset(sleuth_file)

# 检查数据集信息
print(dset.ids)  # 查看包含的实验ID

# Run the decoder
decoder = discrete.NeurosynthDecoder(correction=None)
decoder.fit(dset)
decoded_df = decoder.transform(ids=ids)
decoded_df.sort_values(by="probReverse", ascending=False).head()