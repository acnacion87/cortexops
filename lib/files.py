import pandas as pd
import json

def save_to_csv(data, path):
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    print(f"\nSaved {len(df)} records to {path}.")

def save_to_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        print(f"\nSaved {len(data)} records to {path}.")