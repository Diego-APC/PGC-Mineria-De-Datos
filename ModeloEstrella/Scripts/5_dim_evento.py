"""
dim_evento.py
Genera la dimensión de evento/enfermedad zoonótica y especie afectada.
Fuente: osb_saludambiental_enfermedades_zoonoticas.csv
Salida: DataLimpia/dim_evento.csv
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(
    RAW / "osb_saludambiental_enfermedades_zoonoticas.csv",
    sep=";",
    encoding="utf-8"
)

# Combinacion de enfermedad + especie afectada
dim = (df[["Evento", "Especie"]]
         .drop_duplicates()
         .dropna(subset=["Evento"])
         .sort_values(["Evento", "Especie"])
         .reset_index(drop=True))

dim.insert(0, "id_evento", dim.index + 1)
dim = dim.rename(columns={"Evento": "evento", "Especie": "especie_afectada"})


dim.to_csv(OUT / "dim_evento.csv", index=False, encoding="utf-8")
print(f"dim_evento.csv: {len(dim)} filas")
print(dim.to_string(index=False))
