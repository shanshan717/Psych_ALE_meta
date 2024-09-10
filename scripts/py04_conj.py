from os import makedirs, path
import os
from nibabel import save
from nilearn import image, plotting, reporting
from nilearn.plotting import plot_glass_brain
import numpy as np
import pandas as pd
from atlasreader import get_statmap_info
from IPython.display import display

# We create a new output directory and put our two pre-existing Sleuth files there: the child-specific Sleuth file that we created with the help of Notebook #01 and the adult-specific Sleuth file that was kindly provided to us by Dr Rebecca L. Jackson from MRC CBU at Cambridge (UK).

# 创建输出目录
output_dir = "output/conj"
def create_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

# 计算并保存联合分析结果
def compute_conjunction_map(img1_path, img2_path, output_path, map_type="z", formula="np.where(img1 * img2 > 0, np.minimum(img1, img2), 0)"):
    """
    计算联合分析图（conjunction map），根据两个组的图像计算每个体素的最小值
    """
    img1 = image.load_img('output/ale/HCs/health_z_thresh.nii.gz')
    img2 = image.load_img('output/ale/unhealth_z_thresh.nii.gz')

    img_conj = image.math_img(formula, img1=img1, img2=img2)
    output_file = os.path.join(output_path, f"conjunction_{map_type}.nii.gz")
    save(img_conj, output_file)
    
    print(f"联合分析图 {map_type} 已保存至 {output_file}")
    return img_conj

# 可视化联合分析结果并保存
def plot_conjunction_map(img_conj, map_type="z", vmax=8, output_dir=None):
    """
    可视化联合分析的玻璃脑图，并保存图像文件
    """
    # 设置输出文件路径
    output_file = os.path.join(output_dir, f"conjunction_{map_type}_map.png") if output_dir else None

    # 生成玻璃脑图，并保存图像到指定路径
    plotting.plot_glass_brain(
        img_conj, display_mode="lyrz", colorbar=True, vmax=vmax, 
        title=f"Conjunction {map_type} Map", output_file=output_file
    )
    
    if output_file:
        print(f"联合分析图已保存至: {output_file}")

# 生成簇统计表并保存为TSV文件
def generate_cluster_table(img_conj, map_type="z", stat_threshold=0, min_distance=1000, output_dir=None, atlas="harvard_oxford"):
    """
    生成联合图的簇统计表，并保存为TSV文件
    """
    table = reporting.get_clusters_table(img_conj, stat_threshold=stat_threshold, min_distance=min_distance)
    print(f"{map_type} Map的簇统计表：")
    display(table)
    
    if output_dir:
        # 保存为TSV文件
        tsv_file = os.path.join(output_dir, f"{map_type}_clusters_table.tsv")
        table.to_csv(tsv_file, sep="\t", index=False)
        print(f"簇统计表已保存至: {tsv_file}")

# 主函数，进行联合分析
def run_conjunction_analysis(group1_z_path, group2_z_path, group1_ale_path, group2_ale_path, output_dir):
    """
    运行联合分析，分别计算z值图和ALE图的联合图，并保存结果
    """
    # 创建输出目录
    create_output_dir(output_dir)

    # 计算 z 值联合图
    print("计算 z 值联合图...")
    img_conj_z = compute_conjunction_map(group1_z_path, group2_z_path, output_dir, map_type="z")

    # 计算 ALE 联合图
    print("计算 ALE 值联合图...")
    img_conj_ale = compute_conjunction_map(group1_ale_path, group2_ale_path, output_dir, map_type="ale")

    # 可视化联合 z 值图
    print("可视化 z 值联合图...")
    plot_conjunction_map(img_conj_z, map_type="z",  output_dir=output_dir)

    # 可视化联合 ALE 值图
    print("可视化 ALE 值联合图...")
    plot_conjunction_map(img_conj_ale, map_type="ale",  output_dir=output_dir)

    # 生成簇统计表（z 值）
    print("生成 z 值簇统计表...")
    generate_cluster_table(img_conj_z, map_type="z",  output_dir=output_dir)

    # 生成簇统计表（ALE）
    print("生成 ALE 值簇统计表...")
    generate_cluster_table(img_conj_ale, map_type="ale",  output_dir=output_dir)


# 运行示例
if __name__ == "__main__":
    # 示例数据路径，使用你自己的z值图和ALE值图路径
    group1_z_path = "output/ale/HCs/health_z_thresh.nii.gz"  # 替换为实际路径
    group2_z_path = "output/ale/unhealth_z_thresh.nii.gz"  # 替换为实际路径
    group1_ale_path = "output/ale/HCs/health_stat_thresh.nii.gz"  # 替换为实际路径
    group2_ale_path = "output/ale/unhealth_stat_thresh.nii.gz"  # 替换为实际路径

    output_dir = "output"  # 输出目录

    # 运行联合分析
    run_conjunction_analysis(group1_z_path, group2_z_path, group1_ale_path, group2_ale_path, output_dir)