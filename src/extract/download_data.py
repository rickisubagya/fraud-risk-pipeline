import shutil
from pathlib import Path

import kagglehub

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")
shutil.copy(Path(path) / "creditcard.csv", RAW_DIR / "creditcard.csv")
print("Downloaded creditcard.csv to data/raw")