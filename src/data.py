
from pathlib import Path
from io import StringIO

import pandas as pd


def load_clean_mortality(html_path):
    """
    Extract and validate the SSA actuarial life table.

    Returns
    -------
    mortality : pandas.DataFrame
        Columns: age, sex, qx, lx, ex.
    n_removed : int
        Number of non-data rows removed.
    """

    html_path = Path(html_path)

    if not html_path.is_file():
        raise FileNotFoundError(
            f"Mortality file not found: {html_path}"
        )

    # Read the original HTML file
    html = html_path.read_text(encoding="utf-8")
    tables = pd.read_html(StringIO(html))

    # The inspected SSA file contains one mortality table
    raw = tables[0]

    if raw.shape[1] != 7:
        raise ValueError(
            "Unexpected table structure: expected 7 columns."
        )

    if not isinstance(raw.columns, pd.MultiIndex):
        raise ValueError(
            "Expected the SSA table to have multilevel headers."
        )

    groups = [
        str(value).strip().lower()
        for value in raw.columns.get_level_values(0)
    ]

    if groups[1:4] != ["male"] * 3:
        raise ValueError("Male columns are not as expected.")

    if groups[4:7] != ["female"] * 3:
        raise ValueError("Female columns are not as expected.")

    # Convert ages to numeric values.
    # The final explanatory footnote row becomes NaN.
    numeric_ages = pd.to_numeric(
        raw.iloc[:, 0], errors="coerce"
    )

    valid_rows = numeric_ages.notna()
    n_removed = int((~valid_rows).sum())

    raw_data = raw.loc[valid_rows].copy()
    ages = numeric_ages.loc[valid_rows].astype(int).to_numpy()

    def get_numeric_column(position):
        values = (
            raw_data.iloc[:, position]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        return pd.to_numeric(
            values, errors="coerce"
        ).to_numpy()

    # Convert wide-format columns into long-format records
    male = pd.DataFrame({
        "age": ages,
        "sex": "Male",
        "qx": get_numeric_column(1),
        "lx": get_numeric_column(2),
        "ex": get_numeric_column(3),
    })

    female = pd.DataFrame({
        "age": ages,
        "sex": "Female",
        "qx": get_numeric_column(4),
        "lx": get_numeric_column(5),
        "ex": get_numeric_column(6),
    })

    mortality = pd.concat(
        [male, female], ignore_index=True
    )

    # Order by age, displaying male before female
    mortality = mortality.sort_values(
        ["age", "sex"], ascending=[True, False]
    ).reset_index(drop=True)

    # Data-quality validation
    if mortality.isna().any().any():
        raise ValueError("Unexpected missing values.")

    if mortality.duplicated(["age", "sex"]).any():
        raise ValueError("Duplicate age-sex combinations.")

    if not mortality["qx"].between(0, 1).all():
        raise ValueError("Death probabilities must lie in [0, 1].")

    if (mortality["lx"] < 0).any():
        raise ValueError("Survivor counts cannot be negative.")

    if (mortality["ex"] < 0).any():
        raise ValueError("Life expectancy cannot be negative.")

    expected_ages = set(range(120))

    for sex in ["Male", "Female"]:
        observed_ages = set(
            mortality.loc[mortality["sex"] == sex, "age"]
        )

        if observed_ages != expected_ages:
            raise ValueError(
                f"Unexpected or missing ages for {sex}."
            )

    return mortality, n_removed
