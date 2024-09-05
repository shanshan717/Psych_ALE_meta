# Overview
This repository contains the analytic code used in the study titled *"Abnormal brain activations during self-referential processing across psychiatric disorders: A transdiagnostic neuroimaging meta-analysis."* 

# 项目文件结构

```bash
Psych_ALE_meta-1/
│
├── data/
│   ├── health.txt
│   ├── health<unhealth.txt
│   ├── health>unhealth.txt
│   ├── unhealth.txt
│
├── scripts/
│   ├── py01_patients.py
│   ├── py02_HCs.py
│   ├── py03_subtraction.py
│   ├── py04_conj.py
│   ├── py05_tables.py
│   └── py06_figures.py
│
├── README.md
│
└── output/
    ├── ale/
    ├── conj/
    ├── figures/
    └── tables/
```

# Usage

To run the analysis, navigate to the scripts/ folder and execute the Python scripts in the following order:

	1.	py01_patients.py: Analyzes patient group data.
	2.	py02_HCs.py: Analyzes healthy control group data.
	3.	py03_subtraction.py: Performs subtraction analysis.
	4.	py04_conj.py: Conducts conjunction analysis.
	5.	py05_tables.py: Generates tables from the results.
	6.	py06_figures.py: Generates figures for the study.