"""
dim_localidad.py
Genera la dimensión de localidad enriquecida con:
  - Métricas del perfil de mascotas (desde microchip)
  - Sub Red administrativa (desde enfermedades zoonóticas)
Fuente: microchips + osb_saludambiental_enfermedades_zoonoticas.csv
Salida: DataLimpia/dim_localidad.csv

"""

import unicodedata
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"
OUT.mkdir(exist_ok=True)

mc = pd.read_csv(
    RAW / "reporte_corte_31_07_2020_microchips.csv",
    sep=";",
    encoding="cp850"
)

# Normalizar: quitar espacios y Title
mc["localidad"] = mc["localidad_territorializacion"].str.strip().str.title()

# Excluir registros sin localidad real (no son localidades oficiales de Bogotá)
EXCLUIR = {"No Determinada", "Area Metropolitana", "Área Metropolitana"}
mc = mc[~mc["localidad"].isin(EXCLUIR)]

# Calcular perfil de mascotas por localidad
agg = mc.groupby("localidad").agg(
    total_mascotas  = ("microchip_animal",         "count"),
    pct_caninos     = ("especie",                  lambda x: round((x.str.title() == "Canino").mean() * 100, 1)),
    pct_felinos     = ("especie",                  lambda x: round((x.str.title() == "Felino").mean() * 100, 1)),
    pct_peligrosos  = ("potencialmente_peligroso", lambda x: round((x.str.upper() == "SI").mean() * 100, 1)),
    pct_hembras     = ("sexo_animal",              lambda x: round((x.str.title() == "Hembra").mean() * 100, 1))
).reset_index()

# Los archivos de salud son UTF-8 (diferente al microchip que es cp850)
salud = pd.read_csv(
    RAW / "osb_saludambiental_enfermedades_zoonoticas.csv",
    sep=";",
    encoding="utf-8"
)
salud["localidad"] = salud["Localidad"].str.strip().str.title()

# Cada localidad tiene una sola sub_red fija; tomamos la primera aparicion
sub_red = (salud[["localidad", "Sub Red"]]
           .drop_duplicates("localidad")
           .rename(columns={"Sub Red": "sub_red"}))

# Función que quita acentos y pasa a minusculas — se usa como clave de join
# para que "Santa Fé" == "Santa Fe" y "San Cristóbal" == "San Cristobal"
def sin_acentos(s):
    nfkd = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

agg["_key"]     = agg["localidad"].apply(sin_acentos)
sub_red["_key"] = sub_red["localidad"].apply(sin_acentos)

# Unir por la clave sin acentos; mantener el nombre original del microchip
dim = agg.merge(sub_red[["_key", "sub_red"]], on="_key", how="left")
dim = dim.drop(columns=["_key"])
dim = dim.sort_values("localidad").reset_index(drop=True)
dim.insert(0, "id_localidad", dim.index + 1)

# Localidades del microchip sin sub_red en salud quedaran como NaN 
sin_subred = dim[dim["sub_red"].isna()]["localidad"].tolist()
if sin_subred:
    print(f"Localidades sin sub_red (revisar nombre): {sin_subred}")

dim.to_csv(OUT / "dim_localidad.csv", index=False, encoding="utf-8")
print(f"dim_localidad.csv: {len(dim)} filas")
print(dim[["id_localidad", "localidad", "sub_red", "total_mascotas"]].to_string(index=False))
