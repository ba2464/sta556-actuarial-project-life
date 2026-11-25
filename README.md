# Mortality-Driven Term Life Insurance Risk

### A Reproducible Monte Carlo Study Using U.S. Social Security Life Tables

This project examines how sex-specific mortality assumptions affect the **expected present value** and **variability** of death-benefit payments in hypothetical 20-year term life insurance portfolios. It uses the **2023 U.S. Social Security Administration (SSA) period life table**, standard actuarial probability calculations, and Monte Carlo simulation.

**Author:** Bright Antwi  
**Course:** STA 556

All data preparation, calculations, simulation, and figure generation are performed in Python notebooks and reusable `src/` modules. The Quarto report presents the methodology, results, and interpretations without embedding the analysis code.

## Research question

Under identical term life insurance assumptions, how do the male and female mortality schedules in the 2023 SSA period life table affect expected aggregate discounted death benefits, portfolio variability, and upper-tail claims risk?

## Study design

| Assumption | Value |
|---|---|
| Mortality source | 2023 SSA period life table, male and female schedules |
| Issue age | 40 years |
| Coverage term | 20 years (attained ages 40–59) |
| Death benefit | USD 100,000 per policy |
| Benefit payment | End of the policy year of death |
| Annual effective interest rate | 3% |
| Portfolio size | 1,000 identical, independent policies per mortality scenario |
| Monte Carlo replications | 10,000 portfolios per scenario |
| Random-number seed | 2026 |

The two scenarios are **separate hypothetical portfolios** rather than an empirically observed comparison of insured individuals. The same published period mortality rates are applied throughout the 20-year term; mortality improvement, policy lapses, expenses, investment uncertainty, and dependence between policyholders are not modeled.

## Selected results

| Measure | Male mortality | Female mortality |
|---|---:|---:|
| Probability of death during the 20-year term | 10.7504% | 6.4398% |
| Expected present value per policy | USD 7,541.96 | USD 4,478.56 |
| Theoretical aggregate expected claims | USD 7,541,955.57 | USD 4,478,555.18 |
| Simulated aggregate mean | USD 7,524,475.04 | USD 4,471,203.68 |
| Simulated aggregate standard deviation | USD 693,674.57 | USD 545,481.31 |
| Simulated coefficient of variation | 9.22% | 12.20% |
| Empirical 95th percentile of aggregate claims | USD 8,670,598.66 | USD 5,392,666.48 |

Under the modeled assumptions, the male mortality schedule produces higher expected claims and greater **absolute** variability. The female scenario has higher **relative** variability as measured by the coefficient of variation. These results describe the specified simulation model, not actual insurer pricing or capital requirements.

## Repository structure

```text
sta556-actuarial-project-life/
├── data/
│   ├── raw/
│   │   └── ssa_life_table_2023.html
│   └── processed/
│       └── ssa_mortality_clean.csv
├── notebooks/
│   ├── 01_data_extraction_and_cleaning.ipynb
│   ├── 02_data_preparation_validation.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_actuarial_calculations.ipynb
│   └── 05_monte_carlo_validation.ipynb
├── src/
│   ├── data.py
│   ├── life_math.py
│   └── simulation.py
├── results/                 # Generated Markdown tables included in the report
├── figures/                 # Generated mortality, survival, and claims figures
├── reports/
│   ├── final_project.qmd    # Code-free Quarto report source
│   └── final_project.html   # Rendered HTML report
├── _quarto.yml
├── requirements.txt
└── README.md
```

The `src/` modules implement data loading and validation, actuarial probability and present-value calculations, and the portfolio simulation. Notebooks call these modules and save the tables and figures used by the report.

## Setup

**Requirements:** Python, [Visual Studio Code](https://code.visualstudio.com/) with the Python and Jupyter extensions (or another environment capable of running `.ipynb` notebooks), and [Quarto](https://quarto.org/docs/get-started/) for rendering the report.

Open the project folder in a terminal. To create a virtual environment and install the Python dependencies on **Windows PowerShell**:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On **macOS or Linux**:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

In VS Code, select the `.venv` Python interpreter/kernel when opening the notebooks. Run the notebooks from within the project folder (or its `notebooks/` subfolder); the notebooks resolve and use the repository root for file paths.

## Reproduce the analysis

Run the notebooks in numerical order, using **Run All** for each notebook:

1. **`01_data_extraction_and_cleaning.ipynb`** — Inspect the saved SSA HTML table, extract the male and female mortality records, and save a cleaned CSV.
2. **`02_data_preparation_validation.ipynb`** — Reproduce the formal cleaning and data-quality checks and generate the processed mortality data and validation tables. This notebook also regenerates the CSV, independently of the exploratory extraction in Notebook 01.
3. **`03_exploratory_analysis.ipynb`** — Produce descriptive mortality summaries, selected-age comparisons, age-specific mortality curves, and 20-year survival curves.
4. **`04_actuarial_calculations.ipynb`** — Calculate term death probabilities, individual-policy expected present values, and associated actuarial report tables.
5. **`05_monte_carlo_validation.ipynb`** — Simulate aggregate discounted claims, create male and female claims histograms, summarize the simulation distributions, and compare simulated with analytical portfolio moments.

The notebooks write their outputs to `data/processed/`, `results/`, and `figures/`. The final Quarto document includes these saved outputs; rendering it does **not** rerun the simulations.

After executing the notebooks, render the report from the **repository root**:

```bash
quarto render reports/final_project.qmd
```

Open `reports/final_project.html` to view the final report. The HTML output uses embedded resources so that the rendered report can be shared as a standalone HTML file.

## Reproducibility and numerical validation

- The source mortality table is preserved as a local HTML snapshot in `data/raw/`, so the analysis does not depend on the SSA website remaining unchanged during execution.
- Both mortality scenarios use an explicitly initialized NumPy random-number generator with seed **2026**. The same generator is advanced sequentially through the male and female simulations.
- Analytical results provide benchmarks for checking simulated portfolio means and standard deviations.
- The Python packages used are listed in `requirements.txt`. Their versions are **not pinned**, so exact results and rendering may depend on the software environment; record package versions if strict environment-level reproduction is required.

## Data source

Social Security Administration, Office of the Chief Actuary. (2026). *Actuarial Life Table: 2023 period life table as used in the 2026 Trustees Report*. https://www.ssa.gov/oact/STATS/table4c6.html

The analysis uses the locally saved 2023 mortality-table snapshot rather than automatically downloading the latest table. The cleaned dataset contains 240 age–sex records, covering ages 0 through 119 for each mortality schedule.

## Interpretation and limitations

This is a **controlled actuarial simulation**, not an insurance pricing system. SSA period mortality rates describe a broad population rather than a medically underwritten life insurance portfolio. The study assumes independent policyholder outcomes, a fixed interest rate, constant benefits, and no lapses or expenses. The empirical 95th percentile summarizes the simulated aggregate-claims distribution under those assumptions; it should not be interpreted as an insurer's required capital or a regulatory solvency measure.

For detailed methodology, mathematical derivations, figures, numerical validation, and discussion, see **[`reports/final_project.html`](reports/final_project.html)**.
