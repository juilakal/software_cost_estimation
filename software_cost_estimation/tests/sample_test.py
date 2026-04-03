import sys,os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.estimator import estimate_using_cocomo

effort, time, cost = estimate_using_cocomo(10, "organic", 50000)

print("Effort:", effort)
print("Time:", time)
print("Cost:", cost)
