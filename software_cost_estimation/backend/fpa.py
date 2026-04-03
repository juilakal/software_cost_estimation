def calculate_ufp(ei, eo, eq, ilf, eif):
    return (ei * 4) + (eo * 5) + (eq * 4) + (ilf * 10) + (eif * 7)


def fp_to_loc(fp, language="python"):
    loc_per_fp = {
        "python": 50,
        "java": 53,
        "c": 128
    }
    return fp * loc_per_fp[language]
