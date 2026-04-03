from .cocomo import cocomo_basic
from .fpa import calculate_ufp, fp_to_loc

def estimate_using_cocomo(kloc, project_type, cost_per_pm):
    return cocomo_basic(kloc, project_type, cost_per_pm)


def estimate_using_fpa(fp, language, cost_per_pm):
    loc = fp_to_loc(fp, language)
    kloc = loc / 1000
    return cocomo_basic(kloc, "organic", cost_per_pm)
