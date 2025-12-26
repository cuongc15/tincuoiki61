import pandas as pd
from datetime import datetime

def save_result(name, school_class, score, answers, essays):
    record = {
        "name": name,
        "class": school_class,
        "score": score,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    df = pd.DataFrame([record])
    df.to_csv("results.csv", mode="a", header=False, index=False)
