"""
dim_sexo.py
Genera la dimensión de sexo del animal (Macho / Hembra).
Fuente: reporte_corte_31_07_2020_microchips.csv
Salida: DataLimpia/dim_sexo.csv

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
    usecols=["sexo_animal"]
)

dim = (df.drop_duplicates()
         .dropna()
         .sort_values("sexo_animal")
         .reset_index(drop=True))

dim.insert(0, "id_sexo", dim.index + 1)

dim = dim.rename(columns={"sexo_animal": "sexo"})

dim.to_csv(OUT / "dim_sexo.csv", index=False, encoding="utf-8")
print(f"dim_sexo.csv: {len(dim)} filas")
print(dim.to_string(index=False))
