# Is Gogatsubyo Real?

A 16-Year Analysis of Monthly Suicide Patterns Challenges Japan's "May Sickness" Narrative

## Overview

This repository contains the data, analysis code, and manuscript for our study examining whether gogatsubyo (五月病, "May sickness") — a widely recognized Japanese cultural concept — is supported by population-level suicide statistics.

## Key Findings

- May suicides are significantly elevated (IRR=1.282, P<0.001) but **not distinguishable from March** (P=0.75)
- The 20–29 age group — the primary target of the gogatsubyo narrative — shows the **weakest** May signal among significant age groups
- School-related suicides show **no significant May increase**
- Work-related suicides show the highest May elevation (IRR=1.334)
- Results are robust across COVID-19 exclusion, era comparison, and HAC standard errors

## Data Sources

- **Suicide statistics**: Ministry of Health, Labour and Welfare "Basic Data on Suicide in Communities" (2009–2024)
- **Population data**: Statistics Bureau of Japan (2009–2024)

## Repository Structure

```
data/           - Processed data files
scripts/        - Analysis and visualization code
output/         - Figures, tables, and manuscript PDF
manuscript.md   - Full manuscript text
```

## Requirements

- Python 3.12+
- numpy, statsmodels, matplotlib, openpyxl, xlrd, weasyprint, markdown

## Series

This study is part of the "Japanese Folk Beliefs and Public Health Data" series:
1. [Yakudoshi (厄年)](https://github.com/rehabilitation-collaboration/yakudoshi-v2)
2. [Rokuyo × Birth (六曜)](https://github.com/rehabilitation-collaboration/rokuyo-birth)
3. [Higan Temperature (彼岸)](https://github.com/rehabilitation-collaboration/higan-temperature)
4. **Gogatsubyo (五月病)** ← this repository

## License

CC BY 4.0

## Author

Mizuki Shirai, MHS — Specified Nonprofit Corporation Rehabilitation Collaboration
