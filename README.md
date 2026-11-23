# Predicting 30-day hospital readmission in patients with diabetes

Statistical inference, model comparison and calibration on 99,340 hospital encounters from the Diabetes 130-US hospitals dataset.

This repository holds a complete research project. A download script gets the data, one notebook runs the whole analysis and explains every output, and a 10-page paper reports the findings.

## About this research

**The problem.** When a patient with diabetes returns to hospital within 30 days of discharge it adds to hospital costs and affects patient outcomes (Clore et al., 2014). Hospitals would like to know what is linked to early readmission and whether it can be predicted well enough to direct follow-up care.

**The data.** 99,340 hospital stays from 69,987 patients at 130 US hospitals between 1999 and 2008, taken from the public Diabetes 130-US hospitals dataset.

**What the project does.**
- Describes who is readmitted and tests which factors are associated with it, including whether HbA1c measurement matters and whether that depends on the diagnosis.
- Trains and compares nine prediction models, from simple logistic regression to LightGBM and a neural network.
- Checks that predicted risks can be trusted as probabilities, which is called calibration, and tests whether recalibration helps.
- Explains what the best model relies on and checks whether it works equally well for women and men, for different ages and for the two largest race groups.
- Asks whether acting on the model would help patients through a decision curve analysis.
- Tests whether the common shortcut of splitting records at random, so the same patient appears in both training and test data, inflates the results.

**What it found.** Prior inpatient visits and discharge destination matter most. Models rank patients only moderately well (AUROC about 0.67) but their risk estimates are well calibrated. LightGBM beats regularised logistic regression by only 0.009 AUROC, so a simple transparent model is a defensible choice. Discrimination is lower for patients aged 70 and over. In this dataset a random split did not inflate performance, which was a surprise and is reported as it is.

**Why it matters.** The project shows a complete and careful workflow for clinical prediction. It separates patients across data splits, reports calibration and not only ranking accuracy, quantifies uncertainty with a patient-level bootstrap, tests every hypothesis it set in advance and states plainly where the results went against expectation.

## At a glance

| Item | Where |
|---|---|
| Data download and folder creation | `data_download.py` |
| Full analysis with explanations of every table and figure | `Diabetics.ipynb` |
| Written research paper that reads on GitHub, with figures and tables inline | [`REPORT.md`](REPORT.md) |
| Written research paper, about 3,100 words, 10 pages | `results/Readmission_Research_Report.pdf` |
| Every table the analysis produced | `results/` |
| Every plot the analysis produced | `figures/` |
| Raw and cleaned data | `data/` |
| Dependencies and BibTeX references | `requirements.txt`, `references.bib` |

## Project layout

The project lives in `/home/eoa/Documents/PHD/Diabetics`.

```text
Diabetics/
├── data_download.py            downloads the data and creates the three folders
├── Diabetics.ipynb             the analysis, 87 cells in 19 sections
├── REPORT.md                   the research paper laid out for GitHub, uses images from figures/
├── requirements.txt
├── references.bib
├── data/
│   ├── diabetic_data.csv       raw data, written by data_download.py
│   ├── IDS_mapping.csv         lookup for the id columns, written by data_download.py
│   ├── analysis_cohort.csv.gz  cleaned cohort, written by the notebook
│   └── split_assignment.csv    train, validation, calibration and test label for every encounter
├── results/                    16 tables and summaries plus the PDF report
└── figures/                    20 plots
```

The `data` folder is listed in `.gitignore` so it is not committed to GitHub. The raw files are downloaded by `data_download.py` and the cleaned files are rebuilt by the notebook.

## Quick start

1. Install the packages with `pip install -r requirements.txt`.
2. Download the data by running `data_download.py`. In Spyder open the file and press F5. In a terminal run `python data_download.py`. It creates `data`, `results` and `figures` and skips the download if `data/diabetic_data.csv` already exists.
3. Open `Diabetics.ipynb` in Jupyter and run all cells. The notebook does not download anything. It reads `data/diabetic_data.csv` and writes everything back into the same project folder.

The notebook finds the project through `PROJECT_DIR` in its setup cell, which is set to `/home/eoa/Documents/PHD/Diabetics`. If that folder does not exist it checks the current folder and its parent and then searches below the home folder. Change `PROJECT_DIR` if you move the project.

Set `FAST = True` in the setup cell for a quick test on a 30 percent subsample with fewer bootstrap resamples. A full run took about 10 minutes on a single CPU core in my test.

## Research questions and answers

| Question | Answer from this analysis |
|---|---|
| RQ1 How does readmission vary across patient and encounter characteristics | The overall rate is 11.39 percent. It rises from 8.6 to 26.4 percent with prior inpatient visits and is higher after discharge to places other than home (14.6 against 9.3 percent). Sex and race differ little |
| RQ2 Which factors stay associated after adjustment and is the HbA1c finding reproduced | Prior inpatient visits (odds ratio 1.30 per visit), discharge home (0.67), prescribed diabetes medication (1.19) and HbA1c measurement (0.87). The HbA1c link differs by primary diagnosis (interaction p 0.0034) |
| RQ3 Does a naive split inflate performance | No. A random encounter-level split put 35.7 percent of test rows in contact with training patients but did not raise AUROC. The intervals are wide enough to allow a small effect |
| RQ4 Which model discriminates best | LightGBM with AUROC 0.6745, only 0.009 above L2 logistic regression. The other flexible models are not distinguishable from logistic regression |
| RQ5 Are predictions calibrated and does recalibration help | All models are reasonably calibrated. A small underestimate of risk comes from a higher readmission rate in the test set (11.82 against 11.39 percent). Platt scaling helps slightly |
| RQ6 Does performance differ by subgroup | No sex difference. Discrimination is lower at age 70 and over (0.642) than under 50 (0.725). The two largest race groups perform alike |
| RQ7 Would acting on the model add net benefit | Yes from about 5 to 30 percent thresholds. At 10 percent the model avoids 16 unnecessary follow-ups per 100 patients compared with treating everyone |

Five hypotheses were written before looking at results.

| Hypothesis | Verdict |
|---|---|
| H1 Prior inpatient visits are the strongest factor | Largely supported. Discharge destination is a close competitor |
| H2 The HbA1c association differs by primary diagnosis | Supported |
| H3 A naive split inflates AUROC | Not supported |
| H4 Boosting improves only slightly on logistic regression | Supported |
| H5 Flexible models are less well calibrated than logistic regression | Not supported. LightGBM and the neural network had the lowest calibration error |

## Methods in brief

- **Cohort.** 101,766 encounters from 130 US hospitals. Encounters ending in death or hospice (2,423) and 3 with invalid gender were removed, leaving 99,340 encounters from 69,987 patients. The outcome is readmission within 30 days.
- **Statistics.** Wilson intervals for rates. Chi-square tests with Cramér's V and Mann-Whitney tests on one index encounter per patient. Benjamini-Hochberg correction within each family of tests. Multivariable logistic regression with patient-clustered standard errors and a variance inflation check. A likelihood ratio test for the HbA1c by diagnosis interaction.
- **Split.** Whole patients are assigned to train (60 percent), validation (10 percent), calibration (10 percent) and test (20 percent) sets and a check confirms that no patient is in two sets.
- **Models.** Nine models. A prevalence-only reference, a five-predictor logistic model, L2 and L1 logistic regression, a decision tree, a random forest, HistGradientBoosting, a neural network and LightGBM. Hyperparameters are chosen on the validation set only.
- **Evaluation.** AUROC, AUPRC, Brier score, calibration slope, calibration-in-the-large and expected calibration error with a patient-clustered bootstrap of 200 resamples. Platt scaling and isotonic regression fitted on the calibration set. SHAP values from LightGBM, subgroup analysis, decision curve analysis and a leakage experiment.

## What is in `figures/`

Figures 1 to 9 of the paper are marked in the last column.

| File | Shows | Paper |
|---|---|---|
| 01_missingness.png | Missing values by column | |
| 02_encounters_per_patient.png | How many encounters each patient has | |
| 03_rates_by_group.png | Readmission rate with 95 percent intervals by group | Figure 1 |
| 04_numeric_distributions.png | Numeric features for readmitted and not readmitted patients | |
| 05_correlation_heatmap.png | Spearman correlations among numeric features and the outcome | |
| 06_rate_by_patient_encounters.png | Readmission rate by number of encounters per patient | |
| 07_cramers_v.png | Strength of association for each categorical factor | |
| 08_probability_of_superiority.png | Effect size for each numeric factor | |
| 09_odds_ratio_forest.png | Adjusted odds ratios from the logistic regression | Figure 2 |
| 10_a1c_by_diagnosis.png | HbA1c measurement and readmission by diagnosis group | Figure 3 |
| 11_auroc_differences.png | Paired AUROC differences against L2 logistic regression | |
| 12_discrimination.png | ROC curves, precision recall curves and AUROC by model | Figure 4 |
| 13_calibration_all_models.png | Calibration of eight models | Figure 5 |
| 14_recalibration_effect.png | Brier score, ECE and slope before and after recalibration | |
| 15_calibration_best_model.png | Calibration of LightGBM before and after Platt scaling | |
| 16_shap_summary.png | Top features by SHAP value and the effect of prior inpatient visits | Figure 6 |
| 17_shap_beeswarm_numeric.png | Direction of the effect of each numeric feature | |
| 18_subgroup_auroc.png | AUROC by sex, age band and race | Figure 7 |
| 19_decision_curve.png | Net benefit against threshold probability | Figure 8 |
| 20_leakage_experiment.png | Patient-level split against encounter-level random split | Figure 9 |

## What is in `results/`

| File | Contents |
|---|---|
| cohort_flow.json | Encounters and patients before and after cleaning |
| eda_rates_by_group.csv | Readmission rate with Wilson intervals by group |
| stats_chi_square.csv | Chi-square tests, Cramér's V and adjusted p-values |
| stats_mann_whitney.csv | Mann-Whitney tests and probability of superiority |
| stats_logistic_odds_ratios.csv | Adjusted odds ratios with clustered intervals |
| stats_a1c_by_diagnosis.csv | Odds ratio of HbA1c measurement within each diagnosis group |
| split_summary.csv | Encounters, patients and readmission rate in each split |
| model_tuning.csv | Validation AUROC and chosen settings for each model |
| test_metrics_uncalibrated.csv | Test performance of all nine models |
| test_auroc_differences_vs_logistic_L2.csv | Paired AUROC differences with bootstrap intervals |
| test_metrics_recalibration.csv | Test performance before and after Platt scaling and isotonic regression |
| shap_mean_abs.csv | Mean absolute SHAP value of every feature |
| subgroup_results.csv | Subgroup AUROC, calibration slope and observed to expected ratio |
| decision_curve_table.csv | Net benefit and interventions avoided at selected thresholds |
| leakage_experiment.csv | AUROC under the two splitting strategies |
| environment.json | Software versions, seed and number of bootstrap resamples |
| Readmission_Research_Report.pdf | The research paper |

## Reproducibility and testing

- The random seed is 42 and the bootstrap uses 200 resamples.
- The saved results come from a run with Python 3.12.3, NumPy 2.5.4, pandas 3.0.6, SciPy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, LightGBM 4.7.0 and shap 0.54.1. Other versions can change the last decimal places.
- The notebook runs without the shap package and skips only the dot plot in that case. The bar chart of SHAP values uses LightGBM's own TreeSHAP output.
- The outputs saved in the notebook show the paths of the machine that ran it. They update when you run the notebook again.
- The download script has 14 doctests that need no internet connection. Run them with `python -m doctest -v data_download.py`.

## Limitations

- The data cover 1999 to 2008 in US hospitals so practice and populations have changed.
- There is no external validation and the test set comes from the same hospitals.
- Readmission is only observed within the same hospital system so some events are missed.
- Prior visit counts may not be available at discharge in every setting.
- Odds ratios and SHAP values describe associations and model behaviour and not causal effects.
- Race is used only to assess subgroup performance and small race groups could not be assessed.
- This is a research exercise and not a clinical tool.

## Data, licence and citation

Clore, J., Cios, K., DeShazo, J. and Strack, B. (2014) *Diabetes 130-US hospitals for years 1999-2008* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J

The dataset is released under the CC BY 4.0 licence. It accompanies Strack et al. (2014).

## Author

Eugene Opoku Akosah, MSc Data Science, Aberystwyth University.

## References

Benjamini, Y. and Hochberg, Y. (1995) 'Controlling the false discovery rate: a practical and powerful approach to multiple testing', *Journal of the Royal Statistical Society: Series B*, 57(1), pp. 289-300.

Breiman, L. (2001) 'Random forests', *Machine Learning*, 45(1), pp. 5-32.

Brier, G.W. (1950) 'Verification of forecasts expressed in terms of probability', *Monthly Weather Review*, 78(1), pp. 1-3.

Clore, J., Cios, K., DeShazo, J. and Strack, B. (2014) *Diabetes 130-US hospitals for years 1999-2008* [Dataset]. UCI Machine Learning Repository. Available at: https://doi.org/10.24432/C5230J

Collins, G.S. et al. (2024) 'TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods', *BMJ*, 385, e078378. Available at: https://doi.org/10.1136/bmj-2023-078378

Cramér, H. (1946) *Mathematical methods of statistics*. Princeton: Princeton University Press.

Efron, B. and Tibshirani, R.J. (1993) *An introduction to the bootstrap*. New York: Chapman and Hall.

Field, C.A. and Welsh, A.H. (2007) 'Bootstrapping clustered data', *Journal of the Royal Statistical Society: Series B*, 69(3), pp. 369-390. Available at: https://doi.org/10.1111/j.1467-9868.2007.00593.x

Harris, C.R. et al. (2020) 'Array programming with NumPy', *Nature*, 585, pp. 357-362.

Hunter, J.D. (2007) 'Matplotlib: a 2D graphics environment', *Computing in Science and Engineering*, 9(3), pp. 90-95.

Kapoor, S. and Narayanan, A. (2023) 'Leakage and the reproducibility crisis in machine-learning-based science', *Patterns*, 4(9), 100804. Available at: https://doi.org/10.1016/j.patter.2023.100804

Ke, G. et al. (2017) 'LightGBM: a highly efficient gradient boosting decision tree', in *Advances in Neural Information Processing Systems 30*, pp. 3146-3154.

Lundberg, S.M. and Lee, S.-I. (2017) 'A unified approach to interpreting model predictions', in *Advances in Neural Information Processing Systems 30*, pp. 4765-4774.

Lundberg, S.M. et al. (2020) 'From local explanations to global understanding with explainable AI for trees', *Nature Machine Intelligence*, 2(1), pp. 56-67. Available at: https://doi.org/10.1038/s42256-019-0138-9

Mann, H.B. and Whitney, D.R. (1947) 'On a test of whether one of two random variables is stochastically larger than the other', *Annals of Mathematical Statistics*, 18(1), pp. 50-60.

McKinney, W. (2010) 'Data structures for statistical computing in Python', in *Proceedings of the 9th Python in Science Conference*, pp. 56-61.

Pedregosa, F. et al. (2011) 'Scikit-learn: machine learning in Python', *Journal of Machine Learning Research*, 12, pp. 2825-2830.

Platt, J. (1999) 'Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods', in Smola, A.J., Bartlett, P., Schölkopf, B. and Schuurmans, D. (eds.) *Advances in Large Margin Classifiers*. Cambridge, MA: MIT Press, pp. 61-74.

Seabold, S. and Perktold, J. (2010) 'Statsmodels: econometric and statistical modeling with Python', in *Proceedings of the 9th Python in Science Conference*, pp. 92-96.

Strack, B. et al. (2014) 'Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000 clinical database patient records', *BioMed Research International*, 2014, 781670. Available at: https://doi.org/10.1155/2014/781670

Tibshirani, R. (1996) 'Regression shrinkage and selection via the lasso', *Journal of the Royal Statistical Society: Series B*, 58(1), pp. 267-288.

Van Calster, B. et al. (2019) 'Calibration: the Achilles heel of predictive analytics', *BMC Medicine*, 17, 230. Available at: https://doi.org/10.1186/s12916-019-1466-7

Vickers, A.J. and Elkin, E.B. (2006) 'Decision curve analysis: a novel method for evaluating prediction models', *Medical Decision Making*, 26(6), pp. 565-574. Available at: https://doi.org/10.1177/0272989X06295361

Virtanen, P. et al. (2020) 'SciPy 1.0: fundamental algorithms for scientific computing in Python', *Nature Methods*, 17, pp. 261-272.

Wilson, E.B. (1927) 'Probable inference, the law of succession, and statistical inference', *Journal of the American Statistical Association*, 22(158), pp. 209-212.

Zadrozny, B. and Elkan, C. (2002) 'Transforming classifier scores into accurate multiclass probability estimates', in *Proceedings of the 8th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp. 694-699.



