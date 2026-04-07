"""
Function Point → LOC helpers (industry-average LOC per FP by language).

Used when the UI supplies an aggregate FP count rather than detailed EI/EO/… counts.
"""


def calculate_ufp(ei, eo, eq, ilf, eif):
    """Unadjusted function points from component counts (typical weighting scheme)."""
    return (ei * 4) + (eo * 5) + (eq * 4) + (ilf * 10) + (eif * 7)


def fp_to_loc(fp, language="python"):
    loc_per_fp = {
        "python": 50,
        "java": 53,
        "c": 128,
    }
    if language not in loc_per_fp:
        raise ValueError(f"language must be one of {list(loc_per_fp.keys())}, got {language!r}")
    return fp * loc_per_fp[language]
