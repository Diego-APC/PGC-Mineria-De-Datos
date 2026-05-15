"""
dim_especie.py
Genera la dimensión de especie animal (Canino / Felino).
Fuente: reporte_corte_31_07_2020_microchips.csv
Salida: DataLimpia/dim_especie.csv

"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"
OUT.mkdir(exist_ok=True)

# Leer solo la columna necesaria — encoding latin-1 porque el archivo viene de Windows
df = pd.read_csv(
    RAW / "reporte_corte_31_07_2020_microchips.csv",
    sep=";",
    encoding="latin-1",
    usecols=["especie"]
)

# Valores únicos ordenados alfabéticamente + llave sustituta
dim = (df.drop_duplicates()
         .dropna()
         .sort_values("especie")
         .reset_index(drop=True))

dim.insert(0, "id_especie", dim.index + 1)

dim.to_csv(OUT / "dim_especie.csv", index=False, encoding="utf-8")
print(f"dim_especie.csv: {len(dim)} filas")
print(dim.to_string(index=False))
