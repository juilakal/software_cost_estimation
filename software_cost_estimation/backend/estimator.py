from .cocomo import cocomo_basic
from .fpa import calculate_ufp, fp_to_loc


def estimate_using_cocomo(kloc, project_type, cost_per_pm):
    """Direct Basic COCOMO I from KLOC and mode."""
    if kloc <= 0:
        raise ValueError("KLOC must be positive")
    if cost_per_pm < 0:
        raise ValueError("cost_per_pm cannot be negative")
    return cocomo_basic(kloc, project_type, cost_per_pm)


def estimate_using_fpa(fp, language, cost_per_pm, project_type="organic"):
    """
    Hybrid FPA path: convert aggregate function points to estimated LOC, then KLOC,
    then apply Basic COCOMO I using the selected project mode.

    This is a common back-of-envelope bridge when only total FP and language are known.
    """
    if fp <= 0:
        raise ValueError("Function points must be positive")
    if cost_per_pm < 0:
        raise ValueError("cost_per_pm cannot be negative")
    loc = fp_to_loc(fp, language)
    kloc = loc / 1000.0
    return cocomo_basic(kloc, project_type, cost_per_pm)
