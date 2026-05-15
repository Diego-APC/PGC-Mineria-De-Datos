"""
dim_tamano.py
Genera la dimensión de tamaño del animal con un orden numérico de menor a mayor.
Fuente: reporte_corte_31_07_2020_microchips.csv
Salida: DataLimpia/dim_tamano.csv
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
    encoding="cp850",
    usecols=["tamano_animal"]
)

dim = (df.drop_duplicates()
         .dropna()
         .reset_index(drop=True))

dim.insert(0, "id_tamanio", dim.index + 1)
dim = dim.rename(columns={"tamano_animal": "tamanio"})

# Orden de menor a mayor
ORDEN = {
    "toys - enano": 1,
    "miniatura":    1,
    "pequeño":      2,
    "mediano":      3,
    "grande":       4,
    "gigante":      5,
}
dim["orden"] = dim["tamanio"].str.lower().str.strip().map(ORDEN)

# Si algún valor no quedó mapeado aparecerá como NaN
sin_orden = dim[dim["orden"].isna()]
if not sin_orden.empty:
    print("Valores sin orden asignado (revisar ORDEN):")
    print(sin_orden)

dim["orden"] = dim["orden"].fillna(-1).astype(int)

dim.to_csv(OUT / "dim_tamanio.csv", index=False, encoding="utf-8")
print(f"dim_tamanio.csv: {len(dim)} filas")
print(dim.to_string(index=False))
