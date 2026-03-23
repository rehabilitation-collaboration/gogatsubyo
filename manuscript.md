# Is Gogatsubyo Real? A 16-Year Analysis of Monthly Suicide Patterns Challenges Japan's "May Sickness" Narrative

**Running title:** Gogatsubyo and monthly suicide patterns in Japan

**Mizuki Shirai, MHS**

Specified Nonprofit Corporation Rehabilitation Collaboration, Suita, Osaka, Japan

**Corresponding author:** Mizuki Shirai, reha-collab@manabu-lab.com

**ORCID:** 0009-0005-3615-0670

## Abstract

**Background:** Gogatsubyo (五月病, "May sickness") is a widely recognized cultural concept in Japan describing psychological maladjustment among new students and employees in May following the April academic/fiscal year transition. Surveys suggest 35–56% of working adults report experiencing gogatsubyo-like symptoms, yet no peer-reviewed study has empirically tested whether May represents a distinct peak in mental health burden.

**Methods:** We conducted a retrospective ecological study using national suicide statistics from the Japanese Ministry of Health, Labour and Welfare (2009–2024, N=377,688 suicides across 192 monthly observations). Negative binomial regression estimated incidence rate ratios (IRR) for each month relative to December, adjusting for year trend with population offset. Subgroup analyses stratified by age group (8 categories) and cause of death (6 categories). Sensitivity analyses included COVID-19 period exclusion, era comparison (three 5–6-year blocks), and cause-specific analysis within the 20–29 age group. Benjamini-Hochberg correction was applied for multiple comparisons. Newey-West heteroscedasticity- and autocorrelation-consistent (HAC) standard errors were computed to assess robustness to temporal autocorrelation.

**Results:** May had the second-highest monthly suicide rate (20.5 per 100,000 person-years), with a significant IRR of 1.282 (95% CI 1.192–1.379; P<0.001) relative to December. However, May was not significantly different from March (IRR=0.998; P=0.75), indicating that the May elevation is part of a broader spring peak rather than a month-specific phenomenon. The 20–29 age group—the primary demographic target of the gogatsubyo narrative—had the lowest May IRR among all significant age groups (IRR=1.237). Work-related suicides showed the highest May elevation (IRR=1.334; P<0.001), while school-related suicides were non-significant (IRR=1.155; P=0.117). Among 20–29-year-olds specifically, work-related suicides were elevated by 51.3% in May (IRR=1.513; P<0.001), but school-related suicides remained non-significant (IRR=1.133; P=0.270). All findings were robust across COVID-19 exclusion, era comparison, and HAC standard errors.

**Conclusions:** May suicides are significantly elevated but represent part of a broader spring peak shared with March, not a phenomenon unique to May. The gogatsubyo narrative—that new students and young workers are specifically vulnerable in May—is not supported by suicide data: the target demographic shows the weakest May signal, and school-related suicides show no significant May increase. These findings, based on the most extreme manifestation of psychological distress, are consistent with the gogatsubyo narrative being sustained in part by confirmation bias. Whether milder forms of May-specific maladjustment exist beyond what population-level suicide statistics can capture remains an open question requiring individual-level data.

**Keywords:** gogatsubyo, May sickness, seasonal suicide patterns, Japan, cultural beliefs, negative binomial regression, confirmation bias

---

## Introduction

Gogatsubyo (五月病, literally "May sickness") is a Japanese cultural concept describing a syndrome of psychological maladjustment—lethargy, loss of motivation, anxiety, and depressive symptoms—believed to affect new students and employees approximately one month after the April academic and fiscal year transition [1]. The concept is deeply embedded in Japanese public consciousness: multiple non-academic surveys suggest that 35–56% of working adults report having experienced gogatsubyo-like symptoms [2, 3], and the term is widely used in Japanese media, corporate wellness programs, and popular discourse each spring. Despite this high cultural salience, gogatsubyo has no formal diagnostic criteria and does not appear in any classification system (ICD-11 or DSM-5-TR). Kato and Kanba (2017) described a related concept, "modern-type depression" (shin-gata utsu-byo), as an adjustment disorder characterized by situation-dependent depressive symptoms that improve upon removal from the stressful environment [1]—a phenomenological description that overlaps substantially with the gogatsubyo narrative.

Despite widespread social recognition, no peer-reviewed study has empirically tested whether May represents a distinct peak in mental health burden in Japan. This is a notable research gap given the extensive literature on seasonal patterns of suicide and psychiatric morbidity.

The seasonality of suicide is well established internationally. Yu et al. (2020), in a multi-country study of 1,106,820 suicides across 354 communities in 12 countries, demonstrated a spring peak and winter trough in most Northern Hemisphere nations, with Japan, South Korea, and Taiwan exhibiting a bimodal spring-autumn pattern [4]. Within Japan, Matsubayashi et al. (2016) analyzed 108,968 youth suicides (ages 6–26) over 40 years and found that suicides in school-age children peaked sharply at the beginning of academic terms (April and September), though this pattern was absent in 18–26-year-olds [5]. Okumura et al. (2019), using National Database of Health Insurance Claims (NDB) data on 605,982 psychiatric admissions, found that new psychiatric admissions peaked in July—not May—further undermining the gogatsubyo hypothesis at the population level [6].

If gogatsubyo were a real phenomenon with population-level impact, we would expect three specific patterns: (1) a May-specific peak distinguishable from the general spring elevation, (2) disproportionate effects in the target demographic (young adults aged 20–29), and (3) elevated rates specifically in school- and work-related causes of distress. This study tests all three predictions using 16 years of national suicide statistics from Japan.

---

## Methods

### Study Design

We conducted a retrospective ecological study using population-level monthly suicide data from Japan to test whether May shows a distinct elevation in suicide rates beyond the known spring seasonal pattern.

### Data Sources

#### Suicide data

Monthly suicide counts stratified by age group, sex, and cause of death were obtained from the Ministry of Health, Labour and Welfare (MHLW) "Basic Data on Suicide in Communities" (地域における自殺の基礎資料), which compiles police-reported suicide statistics [7]. Data covered January 2009 to December 2024 (16 years, 192 monthly observations). The dataset contains counts by eight age groups (<20, 20–29, 30–39, 40–49, 50–59, 60–69, 70–79, and 80+), two sex categories (male, female), and six cause-of-death categories (health problems, family problems, economic/livelihood problems, work-related problems, relationship problems, and school-related problems). Cause of death was assigned by police investigation; from 2022 onward, up to four causes could be assigned per case.

Two format changes in the source data required separate parsers: the 2009–2021 format ("old") contained age × cause tables without sex stratification, while the 2022–2024 format ("new") added sex stratification. The "relationship problems" category was renamed from "male-female relationship problems" (男女問題) to "interpersonal relationship problems" (交際問題) in 2022; these were unified in our dataset.

Note that these statistics use the "place of discovery" (発見地) definition of residence, which differs from the "place of residence" (住所地) used in the Vital Statistics of Japan (人口動態統計). Cross-validation against e-Stat vital statistics data for 2015–2024 confirmed that total monthly counts differed by less than 5%, consistent with the known definitional discrepancy.

#### Population data

Annual population estimates by age group were obtained from the Statistics Bureau of Japan (総務省統計局) for 2009–2024. These were used as denominators for rate calculations and as offset terms in regression models.

### Statistical Analysis

#### Primary analysis

Negative binomial regression was used to model monthly suicide counts:

> log(E[suicides_m]) = β₀ + Σ β_month × Month(m) + β_year × Year(m) + offset(log(population / 12))

where Month(m) was represented by 11 dummy variables (reference: December), Year(m) was a linear trend (centered at 2009) included to absorb the secular downtrend in suicide rates, and population/12 served as the exposure offset to convert monthly counts to annualized rates. Negative binomial regression was chosen over Poisson regression because the variance of monthly suicide counts substantially exceeded the mean (variance-to-mean ratio = 5.4), indicating overdispersion; a likelihood ratio test comparing the Poisson and negative binomial models confirmed this (P<0.001). All tests were two-sided with a significance level of α = 0.05. December was selected as the reference month because it consistently had the lowest suicide rate. A linear specification for year trend was chosen for parsimony; the era comparison sensitivity analysis (below) assessed whether non-linear secular trends affected the seasonal estimates by fitting separate models for three time blocks with distinct suicide rate trajectories. No monthly observations were missing across the 192-month study period; the dataset was complete.

Incidence rate ratios (IRR = exp(β)) with 95% confidence intervals were calculated for each month relative to December. Benjamini-Hochberg (BH) correction was applied to the 11 pairwise comparisons to control the false discovery rate at α = 0.05.

#### May versus March comparison

To test whether May is distinguishable from the broader spring peak, a separate model restricted to spring months (March–May) was fitted with month dummies (reference: March) and year trend. A non-significant May coefficient would indicate that May is part of the spring peak rather than a distinct phenomenon.

#### Subgroup analyses

Planned subgroup analyses repeated the primary model separately for each age group (<20, 20–29, 30–39, 40–49, 50–59, 60–69, 70–79, 80+; 8 comparisons per analysis) and each cause-of-death category (work, school, health, family, economic, relationship; 6 comparisons per analysis). Sex-stratified analyses were not performed because the pre-2022 data format did not cross-tabulate sex with cause of death, precluding consistent sex-stratified cause-specific analyses across the full study period. BH correction was applied within each analysis family.

#### Sensitivity analyses

Four planned sensitivity analyses assessed robustness:

1. **COVID-19 exclusion:** Excluding 2020–2023, when pandemic-related social changes may have altered seasonal suicide patterns (N=144 observations).
2. **Era comparison:** Separate models for three time blocks—2009–2014 (post-global-financial-crisis), 2015–2019 (pre-COVID), and 2020–2024 (COVID and post-COVID)—to assess temporal stability.
3. **Young adult cause-specific analysis:** Among 20–29-year-olds, separate models for each cause of death to test whether the gogatsubyo-relevant causes (work, school) show May-specific elevations.
4. **HAC standard errors:** Newey-West heteroscedasticity- and autocorrelation-consistent standard errors (maximum 12 lags) were computed using Poisson GLM to assess whether temporal autocorrelation affected inference. Conclusions were compared between standard and HAC-based estimates.

### Ethical Considerations

This study used exclusively publicly available, fully aggregated population-level data from the Japanese Ministry of Health, Labour and Welfare. No individual-level data were accessed. Under the Japanese Ethical Guidelines for Medical and Biological Research Involving Human Subjects (2021 revision), research using publicly available aggregate statistics does not require ethics committee review (Article 3, Paragraph 1, Item 1). As no human subjects were involved, no institutional review board approval or waiver was sought. This study was conducted in accordance with the principles of the Declaration of Helsinki where applicable to research using aggregate data.

### Software

All analyses were performed using Python 3.14.3 with NumPy, statsmodels 0.14.4, and matplotlib. Analysis code will be available at https://github.com/rehabilitation-collaboration/gogatsubyo.

---

## Results

### Study Population

The dataset comprised 377,688 suicides over 192 monthly observations (January 2009 to December 2024), with a mean of 1,967.1 suicides per month (SD 379.3). Annual totals declined from 32,845 in 2009 to 21,837 in 2024, reflecting a well-documented secular downtrend in Japanese suicide rates.

### Monthly Suicide Patterns

Monthly suicide rates showed a clear seasonal pattern with a spring peak and winter trough (Table 1, Figure 1). March had the highest mean rate (20.6 per 100,000 person-years), followed by May (20.5), April (19.4), and July (19.2). December had the lowest rate (16.0). The May mean was 28.0% higher than December and only 0.2% lower than March.

### Primary Analysis: Monthly IRR

Negative binomial regression confirmed that 10 of 11 months had significantly elevated suicide rates relative to December after BH correction (Table 2). The top three months were March (IRR=1.290, 95% CI 1.200–1.388; P<0.001), May (IRR=1.282, 95% CI 1.192–1.379; P<0.001), and April (IRR=1.213, 95% CI 1.127–1.304; P<0.001). February was the only non-significant month (IRR=1.067; P=0.082). HAC standard errors produced nearly identical estimates (HAC IRR for May: 1.280), confirming robustness to temporal autocorrelation.

### May Versus March

In the spring-restricted model (March–May only, reference: March), May showed an IRR of 0.998 (P=0.75) relative to March, indicating no significant difference between the two months. April was significantly lower than March (IRR=0.939; P<0.001). This result demonstrates that the May elevation is part of a broader spring peak rather than a May-specific phenomenon.

### Age-Stratified Analysis

Total suicides by age group over the study period were: <20 (n=10,042), 20–29 (n=40,840), 30–39 (n=49,458), 40–49 (n=62,543), 50–59 (n=66,102), 60–69 (n=59,706), 70–79 (n=50,599), and 80+ (n=37,291); 1,107 cases (0.3%) with unspecified age were excluded from age-stratified analyses. May IRRs were significant across all age groups except 80+ (Table 3, Figure 2). Notably, the 20–29 age group—the primary demographic target of the gogatsubyo narrative—had the lowest May IRR among all significant age groups (IRR=1.237, 95% CI 1.128–1.357; P<0.001). The highest May IRRs were observed in the 70–79 (IRR=1.400; P<0.001) and <20 (IRR=1.374; P<0.001) age groups. The 80+ group was non-significant (IRR=1.245, 95% CI 0.683–2.271; P=0.474) due to wide confidence intervals reflecting small cell sizes.

### Cause-Specific Analysis

Total cause-attributed suicides were: health (n=185,408), economic (n=67,942), family (n=57,557), work (n=34,889), relationship (n=13,372), and school (n=6,149). Note that individual suicides may be attributed to multiple causes (up to four from 2022 onward), so these counts are not mutually exclusive. Work-related suicides showed the highest May elevation (IRR=1.334, 95% CI 1.174–1.516; P<0.001), followed by economic (IRR=1.308; P=0.004) and health-related causes (IRR=1.274; P<0.001) (Table 3). School-related suicides were not significantly elevated in May (IRR=1.155, 95% CI 0.964–1.383; P=0.117), nor were relationship-related suicides (IRR=1.143; P=0.043, non-significant after BH correction).

### Sensitivity Analyses

All sensitivity analyses confirmed the robustness of the primary findings (Table 4).

**COVID-19 exclusion:** Excluding 2020–2023 yielded a May IRR of 1.294 (95% CI 1.199–1.397; P<0.001), virtually identical to the full-period estimate.

**Era comparison:** May IRRs were remarkably stable across all three eras: 1.282 (2009–2014), 1.288 (2015–2019), and 1.274 (2020–2024) (Figure 3). This temporal consistency argues against cohort effects or period-specific confounding.

**Young adult cause-specific analysis (20–29 age group):** Work-related suicides showed a pronounced May elevation (IRR=1.513, 95% CI 1.314–1.743; P<0.001), representing a 51.3% increase relative to December. In contrast, school-related suicides remained non-significant (IRR=1.133, 95% CI 0.908–1.413; P=0.270). Health-related (IRR=1.178; P=0.035) and economic (IRR=1.209; P=0.034) causes showed borderline significance.

**May ranking stability:** May was ranked #1 among all months in 2009–2014 and #2 (after March) in 2015–2024, consistently within the top two positions across the entire study period.

---

## Discussion

### Principal Findings

This study provides the first empirical test of gogatsubyo—the Japanese cultural belief that new students and employees experience disproportionate psychological maladjustment in May. Using 16 years of national suicide statistics (377,688 deaths), we found that May suicides are indeed significantly elevated (IRR=1.282 relative to December), but this elevation does not support the gogatsubyo narrative for three reasons.

First, May is not distinguishable from March (IRR=0.998; P=0.75). The May elevation is part of a well-documented spring suicide peak observed across the Northern Hemisphere [4], not a phenomenon unique to the post-April transition period. Second, the 20–29 age group—the core demographic of the gogatsubyo narrative—shows the weakest May signal among all significant age groups (IRR=1.237), directly contradicting the prediction that young adults are disproportionately affected. Third, school-related suicides show no significant May increase (IRR=1.155; P=0.117), and this null finding persists even when restricted to 20–29-year-olds (IRR=1.133; P=0.270).

### The Spring Peak: An International Phenomenon

The spring peak in suicide is one of the most replicated findings in psychiatric epidemiology. First documented by Durkheim (1897) and confirmed across dozens of countries over more than a century [8], the spring peak is typically attributed to a combination of biological factors (photoperiod-driven serotonergic changes) and social factors (increased social activity creating contrast with depressive states) [4, 9]. Yu et al. (2020) specifically identified Japan as exhibiting a bimodal spring-autumn pattern, consistent with our finding that March and May are the two peak months [4].

The gogatsubyo narrative offers a culture-specific causal explanation—April transition stress—for what is, in fact, an international seasonal pattern that predates Japan's modern academic calendar. This is a textbook case of a culturally available explanation being retrofitted to an empirical regularity, a process consistent with confirmation bias [10].

### Work-Related Suicides: The One Genuine Signal

The one finding partially consistent with the gogatsubyo concept is the elevated work-related suicide rate in May (IRR=1.334 overall; IRR=1.513 among 20–29-year-olds). This suggests that occupational stress may indeed intensify in May, possibly as the initial orientation period ends and new employees face full workload demands. However, this work-related elevation is not specific to young adults: the overall work-related May IRR (1.334) is only modestly lower than the 20–29 age-specific value (1.513), suggesting a general occupational stress pattern rather than a youth-specific adjustment crisis. Moreover, the absence of a school-related signal undermines the narrative's emphasis on academic maladjustment.

### Comparison with Prior Literature

Our findings are consistent with Okumura et al. (2019), who found that psychiatric admissions peaked in July rather than May [6], and with Matsubayashi et al. (2016), who found school-related suicide peaks at term starts (April, September) rather than one month after transition [5]. The Matsubayashi finding is particularly informative: if academic transition stress were the driver, we would expect the peak at the point of maximum environmental change (April) rather than one month later (May). Although <20-year-old suicides are elevated during spring, the May IRR for this age group (1.374) applies to all causes combined, not specifically to school-related suicides—a pattern more consistent with general spring seasonality than with an adjustment-lag mechanism.

### Gogatsubyo and Confirmation Bias

We propose that the population-level patterns attributed to gogatsubyo may be best understood as a confirmation bias phenomenon, in which the combination of (1) a real spring suicide peak, (2) a culturally salient April transition, and (3) selective media attention creates the perception of a May-specific crisis among young adults. The cognitive mechanism is straightforward: people who feel unwell in May have a readily available cultural explanation ("it must be gogatsubyo"), which reinforces the belief regardless of whether May is actually worse than other spring months. The high self-report rates (35–56%) in non-academic surveys [2, 3] may reflect this attribution bias rather than a genuine May-specific elevation in maladjustment.

This interpretation parallels findings from other cultural beliefs about health. The "Monday effect" on cardiovascular events persists as a replicated finding, yet its mechanism remains debated—with explanations ranging from work stress to weekend behavioral changes—illustrating how a culturally intuitive explanation can oversimplify a complex seasonal pattern [11]. Similarly, the belief in a full-moon effect on psychiatric admissions persists despite a lack of consistent supporting evidence in modern studies [12].

### Strengths and Limitations

This study has several strengths. First, it uses a complete national dataset spanning 16 years and 377,688 suicides, providing high statistical power. Second, the negative binomial regression framework appropriately handles overdispersed count data with population offset. Third, the multi-layered analytical strategy—overall, age-stratified, cause-stratified, and temporally stratified—provides a comprehensive test of the gogatsubyo hypothesis. Fourth, the consistency of results across COVID exclusion, era comparison, and HAC standard errors demonstrates robustness.

Several limitations should be noted. First, this is an ecological study using suicide as the outcome, which is the most extreme manifestation of psychological distress. Gogatsubyo, as popularly conceived, encompasses milder symptoms (fatigue, loss of motivation, anxiety) that may not be captured by suicide statistics. Individual-level data on psychiatric consultations, sick leave, or employee assistance program utilization would provide a more sensitive test, but such data are not publicly available at the monthly level in Japan. Second, the data are monthly aggregates; daily data would enable testing of specific hypotheses about Golden Week (late April–early May national holidays) and the post-holiday return to work/school. Third, the cause-of-death categories are assigned by police investigation rather than clinical assessment and may not accurately reflect the underlying psychosocial stressors; work-related and school-related causes may be particularly subject to underreporting. Fourth, the 80+ age group showed non-significant results with extremely wide confidence intervals (IRR=1.245, 95% CI 0.683–2.271), likely reflecting small cell sizes and overdispersion in this group. Fifth, we could not examine regional variation, as the data are national aggregates. Urban-rural differences in gogatsubyo recognition and in suicide seasonality may exist but could not be tested. Sixth, the cause-of-death coding system changed in 2022 from a single-cause to a multi-cause format (up to four causes per case), which may have inflated cause-specific counts in the later period; however, our era comparison showed stable May IRRs across all three time blocks, suggesting this change did not materially affect the seasonal pattern. Seventh, we did not adjust for environmental confounders such as temperature or photoperiod, which are hypothesized to contribute to the spring suicide peak through serotonergic mechanisms; our study design was not intended to explain the spring peak but rather to test whether May is distinguishable from it.

### Public Health Implications

Our findings suggest that the gogatsubyo narrative, while culturally meaningful, does not identify a population-level mental health crisis specific to May or to young adults. This has implications for workplace and educational mental health programs: rather than concentrating preventive efforts in May—as is common practice in Japanese organizations—resources may be more effectively distributed across the entire spring period (March–May) and targeted at all age groups. The elevated work-related suicide rate in May, while notable, reflects a general occupational pattern rather than a young-adult-specific adjustment crisis.

More broadly, this study illustrates the value of empirical testing of culturally accepted health beliefs. The gap between public perception (35–56% self-reported experience) and epidemiological evidence (no May-specific peak, weakest signal in the target demographic) is consistent with confirmation bias playing a role in sustaining the gogatsubyo narrative. However, because our analysis is limited to population-level suicide data—the most extreme manifestation of psychological distress—we cannot rule out the existence of milder, subclinical forms of May-specific maladjustment that may not manifest in suicide statistics. Individual-level studies using psychiatric consultation records, employee sick leave data, or ecological momentary assessment would be needed to fully evaluate the gogatsubyo phenomenon across the severity spectrum.

---

## References

[1] Kato TA, Kanba S. Modern-type depression as an "adjustment" disorder in Japan: the intersection of collectivistic society encountering an individualistic performance-based system. Am J Psychiatry. 2017;174(11):1051–1053. doi:10.1176/appi.ajp.2017.17010059

[2] Aistat Inc. Survey on gogatsubyo (May sickness) [Internet]. Tokyo: Aistat; 2022 [cited 2026 Mar 23]. Available from: https://istat.jp/archives/4617

[3] MS-Japan Corp. Survey on May sickness among management professionals (管理部門・士業の「五月病」実態調査) [Internet]. Tokyo: MS-Japan; 2024 [cited 2026 Mar 23]. Available from: https://company.jmsc.co.jp/info/2024/0531_11963.html

[4] Yu J, Yang D, Kim Y, Hashizume M, Gasparrini A, Armstrong B, et al. Seasonality of suicide: a multi-country multi-community observational study. Epidemiol Psychiatr Sci. 2020;29:e163. doi:10.1017/S2045796020000748

[5] Matsubayashi T, Ueda M, Yoshikawa K. School and seasonality in youth suicide: evidence from Japan. J Epidemiol Community Health. 2016;70(11):1122–1127. doi:10.1136/jech-2016-207583

[6] Okumura Y, Sugiyama N, Noda T, Tachimori H. Psychiatric admissions and length of stay during fiscal years 2014 and 2015 in Japan: a retrospective cohort study using a nationwide claims database. J Epidemiol. 2019;29(8):288–294. doi:10.2188/jea.JE20180096

[7] Ministry of Health, Labour and Welfare. Basic data on suicide in communities (地域における自殺の基礎資料) [Internet]. Tokyo: MHLW; [cited 2026 Mar 23]. Available from: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000140901.html

[8] Durkheim E. Le suicide: étude de sociologie. Paris: Félix Alcan; 1897.

[9] Woo JM, Okusaga O, Postolache TT. Seasonality of suicidal behavior. Int J Environ Res Public Health. 2012;9(2):531–547. doi:10.3390/ijerph9020531

[10] Nickerson RS. Confirmation bias: a ubiquitous phenomenon in many guises. Rev Gen Psychol. 1998;2(2):175–220. doi:10.1037/1089-2680.2.2.175

[11] Barnett AG, Dobson AJ. Excess in cardiovascular events on Mondays: a meta-analysis and prospective study. J Epidemiol Community Health. 2005;59(2):109–114. doi:10.1136/jech.2003.019489

[12] Raison CL, Klein HM, Steckler M. The moon and madness reconsidered. J Affect Disord. 1999;53(1):99–106. doi:10.1016/S0165-0327(99)00016-6

---

## Acknowledgments

This manuscript was drafted with the assistance of Claude Opus 4.6 (Anthropic), a large language model. The AI assisted with data processing, statistical code generation, literature review, and manuscript drafting. All analyses, interpretations, and final editorial decisions were made by the human author. All references were verified against PubMed and CrossRef databases; any errors remain the responsibility of the author.

## Author Contributions (CRediT)

**Mizuki Shirai:** Conceptualization, Methodology, Software, Formal Analysis, Investigation, Data Curation, Writing – Original Draft, Writing – Review & Editing, Visualization, Project Administration.

## Conflict of Interest

The author declares no conflicts of interest per ICMJE guidelines.

## Funding

This research received no external funding.

## Data Availability

Suicide statistics are publicly available from the Japanese Ministry of Health, Labour and Welfare [7]. Population estimates are publicly available from the Statistics Bureau of Japan (https://www.e-stat.go.jp/). Analysis code is available at https://github.com/rehabilitation-collaboration/gogatsubyo.

## Figure Legends

**Figure 1.** Monthly suicide rate pattern in Japan (2009–2024). Mean monthly suicide rate per 100,000 person-years across 16 years. Error bars represent standard deviations. May (20.5) is the second-highest month after March (20.6). December (16.0) is the reference month in regression analyses.

**Figure 2.** Forest plot of May incidence rate ratios (IRR) by subgroup. IRRs are from negative binomial regression with December as reference. Red indicates significant elevation (lower 95% CI > 1.0); blue indicates non-significant. Upper panel: age groups; lower panel: cause of death categories. The 20–29 age group has the lowest IRR among significant age groups. School-related suicides are non-significant.

**Figure 3.** Temporal stability of monthly IRR patterns across three eras (2009–2014, 2015–2019, 2020–2024). May IRR remains stable at approximately 1.28 across all periods, demonstrating robustness to COVID-19 effects and secular trends.

## Tables

**Table 1.** Descriptive statistics of monthly suicide counts by age group in Japan (2009–2024). Values are mean (SD) of monthly counts and rates per 100,000 person-years across 16 years.

**Table 2.** Monthly incidence rate ratios (IRR) from negative binomial regression (reference: December). All ages, 2009–2024. BH = Benjamini-Hochberg corrected significance. HAC IRR = Newey-West heteroscedasticity- and autocorrelation-consistent estimate.

**Table 3.** May incidence rate ratios by age group and cause of death. Upper panel: age-stratified analysis. Lower panel: cause-stratified analysis. BH = Benjamini-Hochberg corrected significance.

**Table 4.** Sensitivity analyses for May IRR. COVID exclusion, era comparison, and cause-specific analysis within the 20–29 age group.
