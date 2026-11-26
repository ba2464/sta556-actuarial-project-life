
import numpy as np


def simulate_aggregate_claims(
    death_table,
    term_survival,
    n_policies,
    n_portfolios,
    benefit,
    interest_rate,
    rng
):
    """
    Simulate aggregate discounted death benefits.

    Assumes independent, identical policies using
    the same mortality schedule.

    Returns an array of aggregate present values,
    one value for each simulated portfolio.
    """

    if not isinstance(n_policies, (int, np.integer)) or n_policies <= 0:
        raise ValueError("n_policies must be a positive integer.")

    if not isinstance(n_portfolios, (int, np.integer)) or n_portfolios <= 0:
        raise ValueError("n_portfolios must be a positive integer.")

    if benefit <= 0 or interest_rate <= -1:
        raise ValueError("Invalid financial assumptions.")

    # Death in each policy year
    death_probs = death_table[
        "death_probability"
    ].to_numpy(dtype=float)

    # Complete outcome distribution:
    # death in years 1,...,20 or survive the term
    probabilities = np.append(
        death_probs,
        term_survival
    )

    if (
        not np.isfinite(probabilities).all()
        or (probabilities < 0).any()
        or not np.isclose(probabilities.sum(), 1.0)
    ):
        raise ValueError("Invalid outcome probabilities.")

    years = death_table[
        "policy_year"
    ].to_numpy(dtype=float)

    # Discounted benefit for each death year
    present_values = benefit * (
        1 + interest_rate
    ) ** (-years)

    # No death benefit when the policyholder
    # survives the entire 20-year term
    outcome_values = np.append(
        present_values,
        0.0
    )

    # Simulate death counts by outcome category
    counts = rng.multinomial(
        n_policies,
        probabilities,
        size=n_portfolios
    )

    # Sum discounted payments per simulated portfolio
    aggregate_claims = counts @ outcome_values

    return aggregate_claims
