# Script for preprocessing raw data
def load_and_clean(path):
    import pandas as pd
    df = pd.read_csv(path)
    df.dropna(inplace=True)
    return df