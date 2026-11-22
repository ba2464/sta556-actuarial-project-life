
import numpy as np
import pandas as pd


def term_death_probabilities(mortality, sex, entry_age, term):
    """
    Calculate death-year probabilities for a term life policy.

    Returns
    -------
    death_table : DataFrame
        Probability of death in each policy year.
    term_survival : float
        Probability of surviving the entire term.
    """
    if term <= 0 or entry_age < 0:
        raise ValueError("Invalid entry age or term.")

    ages = np.arange(entry_age, entry_age + term)

    subset = mortality.loc[
        mortality["sex"] == sex, ["age", "qx"]
    ]

    if subset["age"].duplicated().any():
        raise ValueError("Duplicate ages in mortality schedule.")

    qx_series = subset.set_index("age")["qx"].reindex(ages)

    if qx_series.isna().any():
        raise ValueError("Missing required mortality ages.")

    qx = qx_series.to_numpy(dtype=float)

    if not np.all((qx >= 0) & (qx <= 1)):
        raise ValueError("Invalid mortality probabilities.")

    # Survival to the beginning of each policy year
    survival_to_start = np.concatenate(
        ([1.0], np.cumprod(1 - qx)[:-1])
    )

    # Unconditional probability of dying in each year
    death_probabilities = survival_to_start * qx

    # Probability of surviving the full policy term
    term_survival = float(np.prod(1 - qx))

    # Check the complete probability distribution
    total_probability = (
        death_probabilities.sum() + term_survival
    )

    if not np.isclose(total_probability, 1.0):
        raise ValueError("Probabilities do not sum to one.")

    death_table = pd.DataFrame({
        "policy_year": np.arange(1, term + 1),
        "attained_age": ages,
        "qx": qx,
        "survival_to_start": survival_to_start,
        "death_probability": death_probabilities,
    })

    return death_table, term_survival


def term_epv(death_table, benefit, interest_rate):
    """
    Calculate the expected present value of a term
    life insurance benefit paid at year-end of death.
    """
    if benefit <= 0:
        raise ValueError("Benefit must be positive.")

    if interest_rate <= -1:
        raise ValueError("Invalid interest rate.")

    years = death_table["policy_year"].to_numpy()
    death_probs = death_table["death_probability"].to_numpy()

    discount_factors = (1 + interest_rate) ** (-years)

    epv = benefit * np.sum(
        discount_factors * death_probs
    )

    return float(epv)


def portfolio_moments(
    death_table,
    benefit,
    interest_rate,
    n_policies
):
    """
    Calculate the theoretical mean and standard deviation
    of aggregate discounted claims for an independent,
    homogeneous portfolio.
    """

    if n_policies <= 0 or benefit <= 0:
        raise ValueError("Invalid portfolio assumptions.")

    if interest_rate <= -1:
        raise ValueError("Interest rate must exceed -1.")

    years = death_table["policy_year"].to_numpy()
    probabilities = death_table[
        "death_probability"
    ].to_numpy(dtype=float)

    discount_factors = (1 + interest_rate) ** (-years)

    present_values = benefit * discount_factors

    # First moment for one policy
    individual_mean = np.sum(
        probabilities * present_values
    )

    # Second moment for one policy
    second_moment = np.sum(
        probabilities * present_values**2
    )

    # Variance for one policy
    individual_variance = (
        second_moment - individual_mean**2
    )

    # Aggregate portfolio moments
    aggregate_mean = n_policies * individual_mean

    aggregate_sd = np.sqrt(
        n_policies * max(individual_variance, 0.0)
    )

    return float(aggregate_mean), float(aggregate_sd)
