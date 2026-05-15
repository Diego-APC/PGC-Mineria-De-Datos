"""
hecho_animal.py
Genera la tabla de hechos central: un registro por mascota registrada con microchip.
Reemplaza los atributos categóricos por llaves foráneas a las dimensiones.
Fuente: reporte_corte_31_07_2020_microchips.csv + todas las dimensiones
Salida: DataLimpia/hecho_animal.csv

Dependencias: correr primero dim_especie, dim_sexo, dim_tamanio, dim_peligrosidad, dim_localidad
"""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW  = BASE.parent / "Raw"
OUT  = BASE.parent / "DataLimpia"

# cargar dataset
mc = pd.read_csv(
    RAW / "reporte_corte_31_07_2020_microchips.csv",
    sep=";",
    encoding="cp850"
)

# El microchip viene con sufijo "-1" del sistema de exportación; lo removemos
mc["microchip_animal"] = mc["microchip_animal"].str.rsplit("-", n=1).str[0]

# Normalizar localidad igual que en dim_localidad para que el join funcione
mc["localidad"] = mc["localidad_territorializacion"].str.strip().str.title()

# Excluir registros sin localidad oficial (igual que en dim_localidad)
EXCLUIR = {"No Determinada", "Area Metropolitana", "Área Metropolitana"}
mc = mc[~mc["localidad"].isin(EXCLUIR)]

# Cargar dimensiones 
dim_especie      = pd.read_csv(OUT / "dim_especie.csv")
dim_sexo         = pd.read_csv(OUT / "dim_sexo.csv")
dim_tamanio       = pd.read_csv(OUT / "dim_tamanio.csv")
dim_peligrosidad = pd.read_csv(OUT / "dim_peligrosidad.csv")
dim_localidad    = pd.read_csv(OUT / "dim_localidad.csv")

# Reemplazar valores por llaves foráneas (merge) 
mc = mc.merge(dim_especie,      on="especie",                                         how="left")
mc = mc.merge(dim_sexo,         left_on="sexo_animal",            right_on="sexo",   how="left")
mc = mc.merge(dim_tamanio,       left_on="tamano_animal",           right_on="tamanio", how="left")
mc = mc.merge(dim_peligrosidad, left_on="potencialmente_peligroso", right_on="es_peligroso", how="left")
mc = mc.merge(dim_localidad[["id_localidad", "localidad"]], on="localidad",           how="left")

# Construir tabla de hechos con solo llaves foráneas 
hecho = mc[["microchip_animal", "id_especie", "id_sexo",
            "id_tamanio", "id_peligrosidad", "id_localidad"]].copy()

hecho.insert(0, "id_animal", range(1, len(hecho) + 1))

# Verificar que no quedaron FKs sin match (indica desalineación de valores)
nulos = hecho[["id_especie", "id_sexo", "id_tamanio", "id_peligrosidad", "id_localidad"]].isnull().sum()
fks_con_nulos = nulos[nulos > 0]
if not fks_con_nulos.empty:
    print("FKs con valores sin match:", fks_con_nulos.to_dict())
else:
    print("Todos los FKs resolvieron correctamente")

hecho.to_csv(OUT / "hecho_animal.csv", index=False, encoding="utf-8")
print(f"hecho_animal.csv: {len(hecho):,} filas")
