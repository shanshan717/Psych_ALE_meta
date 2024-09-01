!pip install nilearn
import nilearn

from nilearn import image, plotting
import matplotlib.pyplot as plt

# Load the activation map(unhealth)
unhealth = image.load_img("/Users/ss/Desktop/self_ref_psy_v2/unhealth_C05_5k_ALE.nii")

# Load the MNI152 template as an underlay image
MNI_underlay = image.load_img("/Users/ss/Desktop/mni152.nii.gz")

# Plot the statistical map over the MNI152 template
plotting.plot_stat_map(unhealth, MNI_underlay) # 没有加'threshold'参数
plt.show()
plt.savefig(unhealth.png")

# Load the activation map(health)
health = image.load_img("/Users/ss/Desktop/self_ref_psy_v2/health_C05_5k_ALE.nii")
MNI_underlay = image.load_img("/Users/ss/Desktop/mni152.nii.gz")

plotting.plot_stat_map(health, MNI_underlay) # 没有加'threshold'参数
plt.show()
plt.savefig(health.png")
            
# Load the activation map(health>unhealth)
health_unhealth = image.load_img("/Users/ss/Desktop/self_ref_psy_v2/health_C05_5k_ALE-unhealth_C05_5k_ALE_ALE.nii")
MNI_underlay = image.load_img("/Users/ss/Desktop/mni152.nii.gz")

plotting.plot_stat_map(health_unhealth, MNI_underlay, threshold = 0.9) 
plt.show()
plt.savefig(health_unhealth.png")         

# Load the activation map(health<unhealth)
unhealth_health = image.load_img("/Users/ss/Desktop/self_ref_psy_v2/unhealth_C05_5k_ALE-health_C05_5k_ALE_ALE.nii")
MNI_underlay = image.load_img("/Users/ss/Desktop/mni152.nii.gz")

plotting.plot_stat_map(health_unhealth, MNI_underlay, threshold = 0.9) 
plt.show()
plt.savefig(unhealth_health.png") 

# Load the activation map(conjunction)
conjunction = image.load_img("/Users/ss/Desktop/self_ref_psy_v2/health_C05_5k_ALE_conj_unhealth_C05_5k_ALE_ALE.nii")
MNI_underlay = image.load_img("/Users/ss/Desktop/mni152.nii.gz")

plotting.plot_stat_map(health_unhealth, MNI_underlay) # 没有加'threshold'参数
plt.show()
plt.savefig(conjunction.png") 
            
# 大脑表层
# plotting.plot_img_on_surf(av_effect, surf_mesh = "fsaverage5")
# plotting.plot_stat_map(av_effect, MNI_underlay, threshold = 0.9) 
# plt.show()

# 网页端显示
# plotting.view_img_on_surf(av_effect, surf_mesh = "fsaverage7")
# html_view.open_in_browser()
