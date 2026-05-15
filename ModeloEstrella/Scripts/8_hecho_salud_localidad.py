"""
hecho_salud_localidad.py
Genera la tabla de hechos de salud animal por localidad y año.
Une las tres fuentes de salud en un solo dataset:
  - Enfermedades zoonóticas (base, tiene el evento y los casos)
  - Cobertura de vacunación antirrábica (una fila por año x localidad)
  - Cumplimiento de reporte de zoonosis  (una fila por año x localidad)
Salida: DataLimpia/hecho_salud_localidad.csv

Dependencias: correr primero dim_localidad y dim_evento
"""

import unicodedata
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"

# Enfermedades zoonoticas 
enf = pd.read_csv(
    RAW / "osb_saludambiental_enfermedades_zoonoticas.csv",
    sep=";",
    encoding="utf-8"
)
enf["localidad"] = enf["Localidad"].str.strip().str.title()

# Excluir "Distrito" (resumen de Bogotá, no es localidad real)
enf = enf[enf["localidad"].str.lower() != "distrito"]

enf = enf.rename(columns={
    "Año":              "anio",
    "Casos notificados": "casos_zoonosis",
    "Evento":           "evento",
    "Especie":          "especie_afectada"
})

# Cobertura antirrábica
cob = pd.read_csv(
    RAW / "osb_saludamb-cobert_antirrab.csv",
    sep=";",
    encoding="cp850"
)
# Renombrar primera columna a "anio" sin importar cómo quedó el encoding de "Año"
cob = cob.rename(columns={cob.columns[0]: "anio"})
cob["localidad"] = cob["localidad"].str.strip().str.title()
# El archivo llama "Candelaria" a lo que el resto llama "La Candelaria"
cob["localidad"] = cob["localidad"].replace("Candelaria", "La Candelaria")

# El separador decimal del archivo es coma (ej: "13,9") — convertir a punto
cob["cobertura_vacuna"] = (cob["Cobertura"]
                           .astype(str)
                           .str.replace(",", ".", regex=False))
cob["cobertura_vacuna"] = pd.to_numeric(cob["cobertura_vacuna"], errors="coerce")

# Excluir la fila "Distrito" que es un resumen de toda Bogotá, no una localidad
cob = cob[cob["localidad"].str.lower() != "distrito"]
cob = cob[["anio", "localidad", "cobertura_vacuna"]]

# Cumplimiento de reporte 
cum = pd.read_csv(
    RAW / "osb_saludambiental-cumplimientoreportezoonosis.csv",
    sep=";",
    encoding="utf-8"
)
cum["localidad"] = cum["localidad"].str.strip().str.title()
cum = cum[cum["localidad"].str.lower() != "distrito"]
# Mismo ajuste: "Candelaria" → "La Candelaria"
cum["localidad"] = cum["localidad"].replace("Candelaria", "La Candelaria")

# "Resultado" viene como string "36%" — extraer solo el número
cum["pct_cumplimiento"] = pd.to_numeric(
    cum["Resultado"].astype(str).str.replace("%", "", regex=False).str.strip(),
    errors="coerce"
)
cum = cum.rename(columns={"Año": "anio"})[["anio", "localidad", "pct_cumplimiento"]]

# Unir las tres fuentes por (anio, localidad)
# Se usa clave sin acentos para que "San Cristobal" == "San Cristóbal" entre archivos
# Cobertura y cumplimiento se repiten por cada evento del mismo año/localidad

def sin_acentos(s):
    nfkd = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

for df in [enf, cob, cum]:
    df["_loc"] = df["localidad"].apply(sin_acentos)

hecho = enf.merge(cob.drop(columns="localidad"),  on=["anio", "_loc"], how="left")
hecho = hecho.merge(cum.drop(columns="localidad"), on=["anio", "_loc"], how="left")
hecho = hecho.drop(columns=["_loc"])

# Reemplazar localidad y evento por llaves foráneas 
dim_localidad = pd.read_csv(OUT / "dim_localidad.csv")
dim_evento    = pd.read_csv(OUT / "dim_evento.csv")

# Join sin acentos para que "San Cristobal" == "San Cristóbal", etc.
hecho["_key"]                        = hecho["localidad"].apply(sin_acentos)
dim_localidad["_key"]                = dim_localidad["localidad"].apply(sin_acentos)
hecho = hecho.merge(dim_localidad[["id_localidad", "_key"]], on="_key", how="left")
hecho = hecho.drop(columns=["_key"])
hecho = hecho.merge(dim_evento,    on=["evento", "especie_afectada"],               how="left")

# Tabla final 
hecho = hecho[["anio", "id_localidad", "id_evento",
               "casos_zoonosis", "cobertura_vacuna", "pct_cumplimiento"]].copy()

hecho.insert(0, "id_hecho", range(1, len(hecho) + 1))

# Verificar FKs sin match
nulos = hecho[["id_localidad", "id_evento"]].isnull().sum()
fks_con_nulos = nulos[nulos > 0]
if not fks_con_nulos.empty:
    print("FKs con valores sin match:", fks_con_nulos.to_dict())
else:
    print("Todos los FKs resolvieron correctamente")

hecho.to_csv(OUT / "hecho_salud_localidad.csv", index=False, encoding="utf-8")
print(f"hecho_salud_localidad.csv: {len(hecho):,} filas")
