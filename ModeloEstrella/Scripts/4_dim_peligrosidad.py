"""
dim_peligrosidad.py
Genera la dimensión de peligrosidad del animal (SI / NO).
Fuente: reporte_corte_31_07_2020_microchips.csv
Salida: DataLimpia/dim_peligrosidad.csv
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(
    RAW / "reporte_corte_31_07_2020_microchips.csv",
    sep=";",
    encoding="latin-1",
    usecols=["potencialmente_peligroso"]
)

dim = (df.drop_duplicates()
         .dropna()
         .sort_values("potencialmente_peligroso")
         .reset_index(drop=True))

dim.insert(0, "id_peligrosidad", dim.index + 1)
dim = dim.rename(columns={"potencialmente_peligroso": "es_peligroso"})

dim.to_csv(OUT / "dim_peligrosidad.csv", index=False, encoding="utf-8")
print(f"dim_peligrosidad.csv: {len(dim)} filas")
print(dim.to_string(index=False))
