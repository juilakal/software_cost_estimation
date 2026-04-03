def cocomo_basic(kloc, project_type, cost_per_pm):
    params = {
        "organic": (2.4, 1.05, 2.5, 0.38),
        "semi": (3.0, 1.12, 2.5, 0.35),
        "embedded": (3.6, 1.20, 2.5, 0.32)
    }

    a, b, c, d = params[project_type]

    effort = a * (kloc ** b)
    time = c * (effort ** d)
    cost = effort * cost_per_pm

    return effort, time, cost
