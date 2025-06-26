import streamlit as st
import ifcopenshell
import ifcopenshell.util.element
import pandas as pd
import tempfile
from rapidfuzz import process, fuzz
import unicodedata
import re
from datetime import datetime
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
import json
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

# --- AQUÍ VA TU LISTA DE CLASIFICACION_MATERIALES ---
CLASIFICACION_MATERIALES = [
    {"Codigo":"HUE.MT.1.1","Categoria":"MT","Unidad":"m3","Denominacion":"Zahorra natural","Factor de Emision":12.8,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.25,"Keywords":["zahorra"]},
    {"Codigo":"HUE.MT.01.2","Categoria":"MT","Unidad":"m3","Denominacion":"Zahorra artificial","Factor de Emision":11.2,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.25,"Keywords":["zahorra"]},
    {"Codigo":"HUE.MT.01.3","Categoria":"MT","Unidad":"t","Denominacion":"Agregados (general)","Factor de Emision":3.7,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1,"Keywords":["agregado"]},
    {"Codigo":"HUE.MT.01.4","Categoria":"MT","Unidad":"m3","Denominacion":"Agua","Factor de Emision":0.319,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.25,"Keywords":["agua"]},
    {"Codigo":"HUE.MT.02.1","Categoria":"MT","Unidad":"t","Denominacion":"Cemento (general)","Factor de Emision":771,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.02.2","Categoria":"MT","Unidad":"t","Denominacion":"CEM I (Portland Cement)","Factor de Emision":866,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.02.3","Categoria":"MT","Unidad":"t","Denominacion":"CEM II","Factor de Emision":709,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.02.4","Categoria":"MT","Unidad":"t","Denominacion":"CEM III A","Factor de Emision":461,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.02.5","Categoria":"MT","Unidad":"t","Denominacion":"CEM III B","Factor de Emision":247,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.02.6","Categoria":"MT","Unidad":"t","Denominacion":"CEM V","Factor de Emision":502,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["cemento"]},
    {"Codigo":"HUE.MT.2.7","Categoria":"MT","Unidad":"t","Denominacion":"Suelo-cemento","Factor de Emision":26.96,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.5,"Keywords":["suelo cemento"]},
    {"Codigo":"HUE.MT.2.8","Categoria":"MT","Unidad":"t","Denominacion":"Grava-cemento","Factor de Emision":31.25,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.5,"Keywords":["grava cemento"]},
    {"Codigo":"HUE.MT.03.1","Categoria":"MT","Unidad":"t","Denominacion":"Barras de acero corrugado para hormigón armado (99% de material reciclado)","Factor de Emision":722,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["acero","metal"]},
    {"Codigo":"HUE.MT.03.2","Categoria":"MT","Unidad":"t","Denominacion":"Barras de acero corrugado para hormigón armado (59% de material reciclado)","Factor de Emision":1400,"Unidades":"kg CO2 eq / t","Grado de certidumbre":2,"Keywords":["acero","metal"]},
    {"Codigo":"HUE.MT.03.3","Categoria":"MT","Unidad":"t","Denominacion":"Barras de acero corrugado para hormigón armado (39% de material reciclado)","Factor de Emision":1860,"Unidades":"kg CO2 eq / t","Grado de certidumbre":2,"Keywords":["acero","metal"]},
    {"Codigo":"HUE.MT.04.1","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón (general)","Factor de Emision":244,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.25,"Keywords":["hormigon","hormigón"]},
    {"Codigo":"HUE.MT.04.2","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa ? 25 MPa","Factor de Emision":196.34,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.5,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.3","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa > 25 MPa","Factor de Emision":260.61,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":1.5,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.4","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 15/20 MPa","Factor de Emision":235,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.5","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 20/25 Mpa","Factor de Emision":251.45,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.6","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 25/30 Mpa","Factor de Emision":265.55,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.7","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 30/35 Mpa","Factor de Emision":282,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.8","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 35/40 Mpa","Factor de Emision":310.2,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.9","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón en masa 40/45 MPa","Factor de Emision":354.85,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon masa","hormigón masa"]},
    {"Codigo":"HUE.MT.04.10","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón armado 20/25 Mpa","Factor de Emision":296.687,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon armado","hormigón armado"]},
    {"Codigo":"HUE.MT.04.11","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón armado 25/30 Mpa","Factor de Emision":310.787,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon armado","hormigón armado"]},
    {"Codigo":"HUE.MT.04.12","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón armado 30/35 Mpa","Factor de Emision":327.237,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon armado","hormigón armado"]},
    {"Codigo":"HUE.MT.04.13","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón armado 35/40 Mpa","Factor de Emision":355.437,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon armado","hormigón armado"]},
    {"Codigo":"HUE.MT.04.14","Categoria":"MT","Unidad":"m3","Denominacion":"Hormigón armado 40/45 MPa","Factor de Emision":400.087,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["hormigon armado","hormigón armado"]},
    {"Codigo":"HUE.MT.05.1","Categoria":"MT","Unidad":"kg","Denominacion":"Producto filmógeno de curado para hormigón","Factor de Emision":14,"Unidades":"kg CO2 eq / kg","Grado de certidumbre":1.25,"Keywords":["filmogeno","curado"]},
    {"Codigo":"HUE.MT.06.1","Categoria":"MT","Unidad":"kg","Denominacion":"Plastificante para hormigón","Factor de Emision":13.73,"Unidades":"kg CO2 eq / kg","Grado de certidumbre":1.25,"Keywords":["plastificante"]},
    {"Codigo":"HUE.MT.07.1","Categoria":"MT","Unidad":"t","Denominacion":"Betún (general)","Factor de Emision":174.244,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["betun","betún"]},
    {"Codigo":"HUE.MT.07.2","Categoria":"MT","Unidad":"t","Denominacion":"Emulsión bituminosa (general)","Factor de Emision":203.746,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["emulsion","bituminosa"]},
    {"Codigo":"HUE.MT.08.1","Categoria":"MT","Unidad":"t","Denominacion":"Mezclas en caliente (con filler de recuperación: calizo)","Factor de Emision":46.34,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["mezcla caliente"]},
    {"Codigo":"HUE.MT.14.2","Categoria":"MT","Unidad":"m3","Denominacion":"Mortero de cemento de dosificación M-7,5 (1:5)","Factor de Emision":312,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["mortero"]},
    {"Codigo":"HUE.MT.14.3","Categoria":"MT","Unidad":"m3","Denominacion":"Mortero de cemento de dosificación M-10 (1:4)","Factor de Emision":364,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["mortero"]},
    {"Codigo":"HUE.MT.14.4","Categoria":"MT","Unidad":"m3","Denominacion":"Mortero de cemento de dosificación M-15 (1:3)","Factor de Emision":442,"Unidades":"kg CO2 eq / m3","Grado de certidumbre":2,"Keywords":["mortero"]},
    {"Codigo":"HUE.MT.11.1","Categoria":"MT","Unidad":"kg","Denominacion":"Acero galvanizado","Factor de Emision":2340.5,"Unidades":"kg CO2 eq / kg","Grado de certidumbre":1,"Keywords":["acero","galvanizado","metal"]},
    {"Codigo":"HUE.MT.11.2","Categoria":"MT","Unidad":"kg","Denominacion":"Acero estructural S275 perfil laminado","Factor de Emision":1.735,"Unidades":"kg CO2 eq / kg","Grado de certidumbre":1.25,"Keywords":["acero estructural"]},
    {"Codigo":"HUE.MT.11.3","Categoria":"MT","Unidad":"m","Denominacion":"Barrera de seguridad con Perfil de doble onda de acero galvanizado","Factor de Emision":37.8,"Unidades":"kg CO2 eq / m","Grado de certidumbre":1.5,"Keywords":["barrera","acero"]},
    {"Codigo":"HUE.MT.11.4","Categoria":"MT","Unidad":"m","Denominacion":"Poste de perfil de acero galvanizado C-120 para barrera de seguridad","Factor de Emision":23.848,"Unidades":"kg CO2 eq / m","Grado de certidumbre":1.5,"Keywords":["poste","acero"]},
    {"Codigo":"HUE.MT.13.1","Categoria":"MT","Unidad":"t","Denominacion":"Pintura para marcas viales","Factor de Emision":2.805,"Unidades":"kg CO2 eq / t","Grado de certidumbre":1.25,"Keywords":["pintura"]},
    # ... (añade el resto de tu tabla aquí con sus keywords)
]

UNIDADES_CONVERSION = {
    'milimetros cubicos': 1e-9, 'centimetros cubicos': 1e-6, 'metros cubicos': 1,
    'm3': 1, 'cm3': 1e-6, 'mm3': 1e-9, 'm²': 1, 'm2': 1, 'mm2': 1e-6, 'cm2': 1e-4,
    'metros cuadrados': 1, 'metros': 1, 'm': 1, 'mm': 1e-3, 'cm': 1e-2,
}

def convertir_unidades(valor, unidad_origen):
    if not unidad_origen:
        return valor
    key = str(unidad_origen).lower().replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u")
    return valor * UNIDADES_CONVERSION.get(key, 1)

def normalizar_texto(texto):
    texto = str(texto)
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[_\-]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    for palabra in ["cte", "blq", "gen", "general", "unnamed"]:
        texto = texto.replace(palabra, "")
    return texto

def clasificar_material_robusto(material_nombre, threshold=60):
    nombre_norm = normalizar_texto(material_nombre)
    mejor_item = None
    mejor_score = 0
    for item in CLASIFICACION_MATERIALES:
        score = 0
        for kw in item.get("Keywords", []):
            if re.search(r'\b' + re.escape(kw) + r'\b', nombre_norm, flags=re.IGNORECASE):
                score += 2 if len(kw) > 4 else 1
        if score > mejor_score:
            mejor_score = score
            mejor_item = item
    if mejor_score >= 2:
        return mejor_item, 100, mejor_item["Denominacion"]
    denominaciones = [normalizar_texto(item["Denominacion"]) for item in CLASIFICACION_MATERIALES]
    resultado = process.extractOne(nombre_norm, denominaciones, scorer=fuzz.token_sort_ratio)
    if resultado and resultado[1] >= threshold:
        idx = denominaciones.index(resultado[0])
        return CLASIFICACION_MATERIALES[idx], resultado[1], CLASIFICACION_MATERIALES[idx]["Denominacion"]
    return {
        "Codigo": "",
        "Categoria": "",
        "Unidad": "",
        "Denominacion": "",
        "Factor de Emision": "",
        "Unidades": "",
        "Grado de certidumbre": ""
    }, 0, ""

def extraer_info_ifc(modelo):
    info = {}
    try:
        proyecto = modelo.by_type("IfcProject")[0]
        info["Nombre proyecto"] = getattr(proyecto, "Name", "-") or "-"
        info["Descripción proyecto"] = getattr(proyecto, "Description", "-") or "-"
        info["GlobalId proyecto"] = getattr(proyecto, "GlobalId", "-") or "-"
    except Exception:
        info["Nombre proyecto"] = "-"
        info["Descripción proyecto"] = "-"
        info["GlobalId proyecto"] = "-"
    try:
        site = modelo.by_type("IfcSite")[0]
        info["Nombre emplazamiento"] = getattr(site, "Name", "-") or "-"
        info["Longitud"] = getattr(site, "RefLongitude", "-") or "-"
        info["Latitud"] = getattr(site, "RefLatitude", "-") or "-"
        info["Elevación"] = getattr(site, "RefElevation", "-") or "-"
        info["Dirección"] = getattr(site, "Description", "-") or "-"
    except Exception:
        info["Nombre emplazamiento"] = "-"
        info["Longitud"] = "-"
        info["Latitud"] = "-"
        info["Elevación"] = "-"
        info["Dirección"] = "-"
    try:
        unidades = modelo.by_type("IfcUnitAssignment")[0].Units
        info["Unidades"] = ", ".join(set([u.UnitType for u in unidades if hasattr(u, "UnitType")]))
    except Exception:
        info["Unidades"] = "-"
    try:
        productos = modelo.by_type("IfcProduct")
        info["Nº elementos"] = len(productos)
        tipos = [p.is_a() for p in productos if hasattr(p, "is_a")]
        tipos_unicos = pd.Series(tipos).value_counts().to_dict()
        info["Tipos de entidades"] = tipos_unicos
    except Exception:
        info["Nº elementos"] = "-"
        info["Tipos de entidades"] = "-"
    return info

def analizar_ifc(uploaded_file, _progress_callback=None):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    modelo = ifcopenshell.open(tmp_path)
    info_ifc = extraer_info_ifc(modelo)
    materiales_data = {}
    elementos = modelo.by_type("IfcProduct")
    total = len(elementos)
    for idx, elemento in enumerate(elementos):
        if _progress_callback:
            _progress_callback(idx / total)
        materiales = ifcopenshell.util.element.get_materials(elemento)
        for material in materiales:
            material_name = material.Name or "Sin nombre"
            if material_name not in materiales_data:
                materiales_data[material_name] = {'volumen': 0.0, 'area': 0.0, 'longitud': 0.0}
        qtos = ifcopenshell.util.element.get_psets(elemento, qtos_only=True)
        for qto_name, qto_data in qtos.items():
            for prop_name, valor in qto_data.items():
                unidad = None
                if isinstance(valor, dict) and 'value' in valor and 'unit' in valor:
                    unidad = valor['unit']
                    valor = valor['value']
                if "Volume" in prop_name:
                    for material in materiales:
                        materiales_data[material.Name]['volumen'] += convertir_unidades(valor, unidad)
                elif "Area" in prop_name:
                    for material in materiales:
                        materiales_data[material.Name]['area'] += convertir_unidades(valor, unidad)
                elif "Length" in prop_name:
                    for material in materiales:
                        materiales_data[material.Name]['longitud'] += convertir_unidades(valor, unidad)
    df_rows = []
    for material, datos in materiales_data.items():
        clasificacion, similitud, denominacion_encontrada = clasificar_material_robusto(material)
        df_rows.append({
            "Material": material,
            "Volumen (m³)": datos['volumen'],
            "Área (m²)": datos['area'],
            "Longitud (m)": datos['longitud'],
            "Similitud (%)": similitud,
            "Denominación encontrada": denominacion_encontrada,
            **clasificacion
        })
    df = pd.DataFrame(df_rows)
    df["Huella CO2e (kg)"] = df.apply(
        lambda row: row["Volumen (m³)"] * row["Factor de Emision"] if row["Factor de Emision"] != "" else 0,
        axis=1
    )
    df["Huella Mín (kg)"] = df.apply(
        lambda row: row["Huella CO2e (kg)"] * (1 - row["Grado de certidumbre"]/10) if row["Factor de Emision"] != "" else 0,
        axis=1
    )
    df["Huella Máx (kg)"] = df.apply(
        lambda row: row["Huella CO2e (kg)"] * (1 + row["Grado de certidumbre"]/10) if row["Factor de Emision"] != "" else 0,
        axis=1
    )
    return df, info_ifc

def actualizar_clasificacion_manual(df, clasificaciones_manuales):
    denominacion2item = {item["Denominacion"]: item for item in CLASIFICACION_MATERIALES}
    for material, denominacion in clasificaciones_manuales.items():
        if denominacion and denominacion in denominacion2item:
            item = denominacion2item[denominacion]
            for col in ["Codigo","Categoria","Unidad","Denominacion","Factor de Emision","Unidades","Grado de certidumbre"]:
                df.loc[df["Material"] == material, col] = item[col]
            df.loc[df["Material"] == material, "Similitud (%)"] = 100
            df.loc[df["Material"] == material, "Denominación encontrada"] = denominacion
            df.loc[df["Material"] == material, "Huella CO2e (kg)"] = (
                df.loc[df["Material"] == material, "Volumen (m³)"] * item["Factor de Emision"]
            )
            df.loc[df["Material"] == material, "Huella Mín (kg)"] = (
                df.loc[df["Material"] == material, "Huella CO2e (kg)"] * (1 - item["Grado de certidumbre"]/10)
            )
            df.loc[df["Material"] == material, "Huella Máx (kg)"] = (
                df.loc[df["Material"] == material, "Huella CO2e (kg)"] * (1 + item["Grado de certidumbre"]/10)
            )
    return df

def detectar_anomalias(df):
    anomalias = []
    for _, row in df.iterrows():
        if row['Similitud (%)'] < 40 and row['Huella CO2e (kg)'] > 1000:
            anomalias.append(f"⚠️ Material '{row['Material']}' tiene baja similitud pero alta huella.")
    return anomalias

def exportar_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

def exportar_json(df):
    return df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8")

def fig_to_base64(fig):
    buf = BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def detectar_materiales_dudosos(df, umbral_similitud=70):
    """Devuelve materiales con similitud baja o sin clasificar."""
    dudosos = df[df["Similitud (%)"] < umbral_similitud]
    return dudosos[["Material", "Similitud (%)", "Denominación encontrada"]]

def checklist_propiedades_material(row):
    """Devuelve una lista de advertencias si faltan magnitudes clave."""
    advertencias = []
    if row["Volumen (m³)"] == 0:
        advertencias.append("Volumen 0")
    if row["Área (m²)"] == 0:
        advertencias.append("Área 0")
    if row["Longitud (m)"] == 0:
        advertencias.append("Longitud 0")
    if row["Similitud (%)"] < 70:
        advertencias.append("Similitud baja")
    if row["Denominacion"] == "":
        advertencias.append("Sin clasificación")
    return ", ".join(advertencias) if advertencias else "OK"

def resumen_validacion_ifc(info_ifc, df):
    """Devuelve un resumen textual de la calidad y fiabilidad del modelo IFC."""
    resumen = []
    resumen.append(f"Proyecto: {info_ifc.get('Nombre proyecto', '-')}")
    resumen.append(f"Descripción: {info_ifc.get('Descripción proyecto', '-')}")
    resumen.append(f"Archivo GlobalId: {info_ifc.get('GlobalId proyecto', '-')}")
    resumen.append(f"Unidades detectadas: {info_ifc.get('Unidades', '-')}")
    resumen.append(f"Nº de elementos IFC: {info_ifc.get('Nº elementos', '-')}")
    resumen.append(f"Tipos de entidades: {', '.join(str(k) for k in info_ifc.get('Tipos de entidades', {}).keys())}")
    resumen.append(f"Materiales extraídos: {len(df)}")
    resumen.append(f"Materiales bien clasificados (≥70%): {(df['Similitud (%)'] >= 70).sum()}")
    resumen.append(f"Materiales dudosos: {(df['Similitud (%)'] < 70).sum()}")
    return "\n".join(resumen)

def generar_informe_pdf(
    df_filtrado, total_vol, total_area, total_long, co2_total, pct_bien, info_ifc, logo_path=None
):

    buffer = io.BytesIO()
    fecha_analisis = datetime.now().strftime('%Y-%m-%d %H:%M')
    materiales_dudosos = detectar_materiales_dudosos(df_filtrado)
    resumen_validacion = resumen_validacion_ifc(info_ifc, df_filtrado)
    checklist = df_filtrado.apply(checklist_propiedades_material, axis=1)

    with PdfPages(buffer) as pdf:
        # Portada (A3 vertical)
        fig = plt.figure(figsize=(11.69, 16.54))
        gs = gridspec.GridSpec(4, 1, height_ratios=[1, 2, 1, 1])
        ax0 = plt.subplot(gs[0]); ax0.axis('off')
        ax1 = plt.subplot(gs[1]); ax1.axis('off')
        ax1.text(0.5, 0.7, "Informe de Análisis de Materiales IFC", fontsize=28, ha='center', weight='bold')
        ax1.text(0.5, 0.5, f"Proyecto: {info_ifc.get('Nombre proyecto', '-')}", fontsize=18, ha='center')
        ax1.text(0.5, 0.4, f"Fecha de análisis: {fecha_analisis}", fontsize=16, ha='center')
        ax2 = plt.subplot(gs[2]); ax2.axis('off')
        resumen_text = (
            f"Volumen total: {total_vol:,.2f} m³\n"
            f"Área total: {total_area:,.2f} m²\n"
            f"Longitud total: {total_long:,.2f} m\n"
            f"CO₂ total: {co2_total:,.2f} kg\n"
            f"Materiales bien clasificados: {pct_bien:.1f}%"
        )
        ax2.text(0.5, 0.5, resumen_text, ha='center', va='center', fontsize=18, bbox=dict(facecolor='#e0f7fa', alpha=0.7, boxstyle='round,pad=0.6'))
        ax3 = plt.subplot(gs[3]); ax3.axis('off')
        ax3.text(0.5, 0.2, "Generado con materiales-ifc", fontsize=14, ha='center', color='gray')
        pdf.savefig(fig)
        plt.close(fig)

        # Resumen de validación y fiabilidad (A3 horizontal)
        fig, ax = plt.subplots(figsize=(16.54, 8.27))
        ax.axis('off')
        ax.text(0, 1, "Resumen de validación y fiabilidad del modelo IFC:", fontsize=16, weight='bold', va='top')
        ax.text(0, 0.95, resumen_validacion, fontsize=13, va='top')
        ax.text(0, 0.3, "Recomendación: Valide su archivo IFC con servicios externos como buildingSMART Spain o usBIM.checker para asegurar la conformidad y fiabilidad del modelo.\n", fontsize=11, color="gray")
        pdf.savefig(fig)
        plt.close(fig)

        # Tabla de materiales y checklist de fiabilidad (A3 horizontal)
        fig, ax = plt.subplots(figsize=(16.54, max(8.27, 0.5 + 0.35*len(df_filtrado))))
        ax.axis('off')
        cols_tabla = [col for col in ["Material", "Volumen (m³)", "Área (m²)", "Longitud (m)", "Similitud (%)", "Denominación encontrada", "Codigo", "Denominacion", "Huella CO2e (kg)", "Huella Mín (kg)", "Huella Máx (kg)"] if col in df_filtrado.columns]
        tabla = ax.table(
            cellText=[list(row) + [checklist.iloc[i]] for i, row in enumerate(df_filtrado[cols_tabla].values)],
            colLabels=cols_tabla + ["Checklist fiabilidad"],
            loc='center',
            cellLoc='center',
            colColours=["#e0f7fa"] * (len(cols_tabla)+1)
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(12)
        tabla.scale(1.2, 1.2)
        plt.title("Tabla de materiales extraídos y checklist de fiabilidad", fontsize=14, pad=10)
        pdf.savefig()
        plt.close()

        # Materiales dudosos (A3 horizontal)
        if not materiales_dudosos.empty:
            fig, ax = plt.subplots(figsize=(16.54, max(4, 0.5 + 0.3*len(materiales_dudosos))))
            ax.axis('off')
            tabla = ax.table(
                cellText=materiales_dudosos.values,
                colLabels=materiales_dudosos.columns,
                loc='center',
                cellLoc='center',
                colColours=["#ffcdd2"] * len(materiales_dudosos.columns)
            )
            tabla.auto_set_font_size(False)
            tabla.set_fontsize(12)
            tabla.scale(1.2, 1.2)
            plt.title("Materiales dudosos o no clasificados", fontsize=14, pad=10, color='red')
            pdf.savefig()
            plt.close()

        # Estadísticas de dispersión (A3 horizontal)
        fig, ax = plt.subplots(figsize=(16.54, 6))
        ax.axis('off')
        stats = df_filtrado[["Volumen (m³)", "Área (m²)", "Longitud (m)", "Huella CO2e (kg)"]].describe().T
        ax.table(cellText=stats.values, colLabels=stats.columns, rowLabels=stats.index, loc='center')
        plt.title("Estadísticas descriptivas de magnitudes extraídas", fontsize=14, pad=10)
        pdf.savefig()
        plt.close()

        # --- GRÁFICOS DE APOYO ---
        # Gráfico de barras de volumen por material
        if "Volumen (m³)" in df_filtrado.columns:
            fig, ax = plt.subplots(figsize=(16, 7))
            sns.barplot(data=df_filtrado, x="Material", y="Volumen (m³)", ax=ax, palette="Blues_d")
            ax.set_title("Volumen por Material", fontsize=16)
            ax.set_ylabel("Volumen (m³)"); ax.set_xlabel("Material")
            plt.xticks(rotation=60, ha='right', fontsize=10)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Gráfico de barras de área por material
        if "Área (m²)" in df_filtrado.columns:
            fig, ax = plt.subplots(figsize=(16, 7))
            sns.barplot(data=df_filtrado, x="Material", y="Área (m²)", ax=ax, palette="Oranges_d")
            ax.set_title("Área por Material", fontsize=16)
            ax.set_ylabel("Área (m²)"); ax.set_xlabel("Material")
            plt.xticks(rotation=60, ha='right', fontsize=10)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Gráfico de barras de longitud por material
        if "Longitud (m)" in df_filtrado.columns:
            fig, ax = plt.subplots(figsize=(16, 7))
            sns.barplot(data=df_filtrado, x="Material", y="Longitud (m)", ax=ax, palette="Greens_d")
            ax.set_title("Longitud por Material", fontsize=16)
            ax.set_ylabel("Longitud (m)"); ax.set_xlabel("Material")
            plt.xticks(rotation=60, ha='right', fontsize=10)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Gráfico de barras de huella CO2e por material
        if "Huella CO2e (kg)" in df_filtrado.columns:
            fig, ax = plt.subplots(figsize=(16, 7))
            sns.barplot(data=df_filtrado, x="Material", y="Huella CO2e (kg)", ax=ax, palette="Reds")
            ax.set_title("Huella de CO₂ por Material", fontsize=16)
            ax.set_ylabel("CO₂ (kg)"); ax.set_xlabel("Material")
            plt.xticks(rotation=60, ha='right', fontsize=10)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Pie chart de porcentaje de volumen
        if "Volumen (m³)" in df_filtrado.columns and df_filtrado["Volumen (m³)"].sum() > 0:
            fig, ax = plt.subplots(figsize=(10, 10))
            df_percent = df_filtrado.copy()
            df_percent["% Volumen"] = 100 * df_percent["Volumen (m³)"] / df_percent["Volumen (m³)"].sum()
            wedges, texts, autotexts = ax.pie(df_percent["% Volumen"], labels=df_percent["Material"], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.set_title("Porcentaje de Volumen por Material", fontsize=16)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Boxplot de huella CO2e
        if "Huella CO2e (kg)" in df_filtrado.columns:
            fig, ax = plt.subplots(figsize=(10, 7))
            sns.boxplot(data=df_filtrado, y="Huella CO2e (kg)", color="#ff9800", ax=ax)
            sns.stripplot(data=df_filtrado, y="Huella CO2e (kg)", color="#222", ax=ax, jitter=True)
            ax.set_title("Boxplot de Huella de CO₂", fontsize=16)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        # Heatmap de correlación entre magnitudes
        magnitudes = ["Volumen (m³)", "Área (m²)", "Longitud (m)", "Huella CO2e (kg)", "Huella Mín (kg)", "Huella Máx (kg)"]
        cols_corr = [col for col in magnitudes if col in df_filtrado.columns]
        if len(cols_corr) > 1:
            fig, ax = plt.subplots(figsize=(10, 8))
            corr = df_filtrado[cols_corr].corr()
            sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
            ax.set_title("Heatmap de correlación entre magnitudes", fontsize=16)
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    buffer.seek(0)
    return buffer.getvalue()

def ifc_coord_to_decimal(coord):
    if isinstance(coord, (list, tuple)) and len(coord) >= 3:
        sign = -1 if coord[0] < 0 else 1
        return sign * (abs(coord[0]) + coord[1] / 60 + coord[2] / 3600)
    try:
        return float(coord)
    except Exception:
        return None

def ifc_coord_to_decimal(coord):
    if isinstance(coord, (list, tuple)) and len(coord) >= 3:
        sign = -1 if coord[0] < 0 else 1
        return sign * (abs(coord[0]) + coord[1] / 60 + coord[2] / 3600)
    try:
        return float(coord)
    except Exception:
        return None

def generar_mapa_3d_materiales(df, info_ifc):
    # Obtén la ubicación del emplazamiento
    lat = ifc_coord_to_decimal(info_ifc.get("Latitud", None))
    lon = ifc_coord_to_decimal(info_ifc.get("Longitud", None))
    elev = info_ifc.get("Elevación", 0)
    # Simula dispersión de materiales en torno al emplazamiento para visualización
    if lat is not None and lon is not None and not df.empty:
        rng = np.random.default_rng(42)
        lats = lat + rng.normal(0, 0.0005, size=len(df))
        lons = lon + rng.normal(0, 0.0005, size=len(df))
        zs = df["Huella CO2e (kg)"].values
        fig = go.Figure(data=[
            go.Scatter3d(
                x=lons, y=lats, z=zs,
                mode='markers+text',
                marker=dict(
                    size=10 + 15 * (zs - zs.min()) / (zs.max() - zs.min() + 1e-6),
                    color=zs,
                    colorscale='YlOrRd',
                    colorbar=dict(title="CO₂ (kg)"),
                    opacity=0.85,
                ),
                text=df["Material"].values,
                hovertemplate="<b>%{text}</b><br>Lat: %{y:.5f}<br>Lon: %{x:.5f}<br>CO₂: %{z:,.1f} kg"
            )
        ])
        fig.update_layout(
            scene=dict(
                xaxis_title='Longitud',
                yaxis_title='Latitud',
                zaxis_title='Huella CO₂ (kg)',
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5),
            ),
            title="Mapa 3D ambiental de materiales - Huella de carbono",
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig
    else:
        return None


def generar_mapa_calor(df, info_ifc):
    lat = ifc_coord_to_decimal(info_ifc.get("Latitud", None))
    lon = ifc_coord_to_decimal(info_ifc.get("Longitud", None))
    if lat is not None and lon is not None:
        df_map = pd.DataFrame({
            'lat': [lat],
            'lon': [lon],
            'CO2e': [df["Huella CO2e (kg)"].sum()]
        })
        fig = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            size="CO2e",
            color="CO2e",
            color_continuous_scale="YlOrRd",
            size_max=50,
            zoom=10,
            hover_data={"CO2e": True, "lat": True, "lon": True}
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        return fig
    else:
        return None

st.set_page_config(page_title="Análisis IFC", page_icon="brick", layout="wide")

with st.sidebar:
    st.title("Análisis IFC")
    uploaded_file = st.file_uploader("Sube tu archivo IFC", type=["ifc"])

    with st.expander("⚙️ Parámetros avanzados"):
        similitud_min = st.slider("Similitud mínima (%)", 0, 100, 60, step=5, key="threshold")
        mostrar_no_clasificados = st.checkbox("Mostrar materiales no clasificados", True, key="show_unmatched")
    with st.expander("🔎 Búsqueda avanzada y filtros", expanded=False):
        filtro = st.text_input("Buscar material por nombre", "")
        denom_filtro = st.text_input("Filtrar por denominación encontrada", "")
    st.markdown('---')

if uploaded_file:
    progress_bar = st.progress(0, text="Analizando archivo IFC...")
    df, info_ifc = analizar_ifc(uploaded_file, _progress_callback=lambda x: progress_bar.progress(x))
    progress_bar.empty()
    st.success("¡Archivo analizado correctamente!")

    st.sidebar.markdown("### Clasificación manual de materiales")
    materiales_disponibles = df["Material"].tolist()
    if materiales_disponibles:
        material_a_editar = st.sidebar.selectbox(
            "Selecciona el material a editar",
            materiales_disponibles,
            key="material_a_editar_sidebar"
        )
        denominaciones_oficiales = [item["Denominacion"] for item in CLASIFICACION_MATERIALES]
        actual = df.loc[df["Material"] == material_a_editar, "Denominacion"].values[0]
        filtro_denominacion = st.sidebar.text_input("Buscar denominación oficial", "", key="sidebar_filtro_denominacion")
        opciones_desplegable = [""] + [d for d in denominaciones_oficiales if filtro_denominacion.lower() in d.lower()] + ["Otra..."]
        index_actual = opciones_desplegable.index(actual) if actual in opciones_desplegable else 0
        seleccion = st.sidebar.selectbox(
            f"Selecciona nueva denominación oficial para '{material_a_editar}'",
            opciones_desplegable,
            index=index_actual,
            key=f"manual_{material_a_editar}_sidebar"
        )
        denominacion_final = seleccion
        if seleccion == "Otra...":
            denominacion_final = st.sidebar.text_input("Introduce tu denominación personalizada", key=f"otra_{material_a_editar}_sidebar")
        clasificacion_manual = {}
        if st.sidebar.button("Actualizar clasificación manual", key=f"update_manual_{material_a_editar}_sidebar"):
            clasificacion_manual[material_a_editar] = denominacion_final
            st.session_state['clasificacion_manual'] = st.session_state.get('clasificacion_manual', {})
            st.session_state['clasificacion_manual'].update(clasificacion_manual)
            st.rerun()

    clasificaciones_manuales = st.session_state.get('clasificacion_manual', {})
    df = actualizar_clasificacion_manual(df, clasificaciones_manuales)

    df_filtrado = df.copy()
    if filtro:
        df_filtrado = df_filtrado[df_filtrado["Material"].str.contains(filtro, case=False)]
    if denom_filtro:
        df_filtrado = df_filtrado[df_filtrado["Denominación encontrada"].str.contains(denom_filtro, case=False)]
    if not mostrar_no_clasificados:
        df_filtrado = df_filtrado[df_filtrado["Similitud (%)"] > 0]
    df_filtrado = df_filtrado[df_filtrado["Similitud (%)"] >= similitud_min]

    total_vol = df_filtrado["Volumen (m³)"].sum()
    total_area = df_filtrado["Área (m²)"].sum()
    total_long = df_filtrado["Longitud (m)"].sum()
    co2_total = df_filtrado["Huella CO2e (kg)"].sum()
    pct_bien = (df_filtrado["Similitud (%)"] >= 70).sum() / len(df_filtrado) * 100 if len(df_filtrado) else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Volumen total (m³)", f"{total_vol:,.2f}")
    col2.metric("Área total (m²)", f"{total_area:,.2f}")
    col3.metric("Longitud total (m)", f"{total_long:,.2f}")
    col4.metric(
        "CO₂ total (kg)",
        f"{co2_total:,.2f}",
        delta=f"[{df_filtrado['Huella Mín (kg)'].sum():,.2f} - {df_filtrado['Huella Máx (kg)'].sum():,.2f}] kg",
        delta_color="off"
    )
    col5.metric("Clasificados bien (%)", f"{pct_bien:.1f} %", help="Porcentaje de materiales con similitud ≥ 70%")

    st.markdown(f"""
        <div style='background:#e0f7fa;padding:1.5em 1em 1em 1em;border-radius:12px;margin-bottom:1.5em;'>
        <span style='font-size:1.5em;color:#1b1b1b'><b>🌍 Huella de carbono total:</b> <span style='color:#1b1b1b;font-weight:bold'>{co2_total:,.2f} kg CO₂</span> <span style='font-size:1em;color:#666'>(rango: {df_filtrado['Huella Mín (kg)'].sum():,.2f} - {df_filtrado['Huella Máx (kg)'].sum():,.2f} kg)</span></span>
        </div>
        """, unsafe_allow_html=True)

    anomalias = detectar_anomalias(df_filtrado)
    if anomalias:
        st.error("### Alertas de Calidad de Datos\n" + "\n\n".join(anomalias))

    # --- DESCARGAS DESDE UN DESPLEGABLE ---
    with st.expander("⬇️ Descargas de datos e informes"):
        opcion_descarga = st.selectbox(
            "Selecciona el formato de descarga",
            [
                "Excel (.xlsx)",
                "JSON (.json)",
                "Informe PDF (.pdf)"
            ],
            key="descarga_select"
        )
        if opcion_descarga == "Excel (.xlsx)":
            st.download_button(
                "Descargar Excel",
                data=exportar_excel(df_filtrado),
                file_name="materiales_ifc.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="descarga_excel"
            )
        elif opcion_descarga == "JSON (.json)":
            st.download_button(
                "Descargar JSON",
                data=exportar_json(df_filtrado),
                file_name="materiales_ifc.json",
                mime="application/json",
                key="descarga_json"
            )
        elif opcion_descarga == "Informe PDF (.pdf)":
            pdf_bytes = generar_informe_pdf(
                df_filtrado, total_vol, total_area, total_long, co2_total, pct_bien, info_ifc
            )
            st.download_button(
                "Descargar Informe PDF",
                data=pdf_bytes,
                file_name="informe_materiales_ifc.pdf",
                mime="application/pdf",
                key="descarga_pdf"
            )

    tab1, tab2, tab3, tab4, tab_dashboard, tab_3d = st.tabs(
        ["Materiales", "Gráficos", "Resumen", "Detalles IFC", "Otras métricas", "Mapa 3D Ambiental"]
    )

    with tab1:
        st.subheader("Datos extraídos")
        st.dataframe(
            df_filtrado[["Material", "Volumen (m³)", "Área (m²)", "Longitud (m)"]].sort_values(by="Volumen (m³)",
                                                                                               ascending=False))

        if st.checkbox("Mostrar resumen estadístico de magnitudes"):
            st.write(df_filtrado[["Volumen (m³)", "Área (m²)", "Longitud (m)"]].describe())

        default_cols = ["Material", "Volumen (m³)", "Área (m²)", "Longitud (m)", "Similitud (%)", "Denominación encontrada", "Codigo", "Denominacion", "Huella CO2e (kg)", "Huella Mín (kg)", "Huella Máx (kg)"]
        options_cols = [col for col in default_cols if col in df.columns]
        cols_to_show = st.multiselect(
            "Columnas a mostrar",
            options=list(df.columns),
            default=options_cols,
            key="cols_to_show_tab1"
        )
        def estilo_materiales(row):
            styles = []
            for col, val in row.items():
                if col == "Similitud (%)":
                    if val >= 90:
                        bg = "#8fd19e"; color = "#222"
                    elif val >= 70:
                        bg = "#ffe082"; color = "#222"
                    elif val > 0:
                        bg = "#f7a6a6"; color = "#222"
                    else:
                        bg = "#fbe9e7"; color = "#222"
                    styles.append(f"background-color: {bg}; color: {color}; font-weight:bold;")
                elif col == "Huella CO2e (kg)":
                    bg = "#ff9800"; color = "#fff"
                    styles.append(f"background-color: {bg}; color: {color}; font-weight:bold;")
                elif col == "Huella Mín (kg)":
                    bg = "#ffd699"; color = "#222"
                    styles.append(f"background-color: {bg}; color: {color};")
                elif col == "Huella Máx (kg)":
                    bg = "#e65100"; color = "#fff"
                    styles.append(f"background-color: {bg}; color: {color};")
                elif col == "Volumen (m³)":
                    bg = "#e3f2fd"; color = "#222"
                    styles.append(f"background-color: {bg}; color: {color};")
                elif col == "Área (m²)":
                    bg = "#90caf9"; color = "#222"
                    styles.append(f"background-color: {bg}; color: {color};")
                elif col == "Longitud (m)":
                    bg = "#1565c0"; color = "#fff"
                    styles.append(f"background-color: {bg}; color: {color};")
                else:
                    styles.append("")
            return styles
        st.dataframe(
            df_filtrado[cols_to_show].style.apply(estilo_materiales, axis=1),
            use_container_width=True, hide_index=True
        )

    with tab2:
        subtabs = st.tabs(["Volumen", "Área", "Longitud", "CO₂ por material", "Porcentaje Volumen"])
        with subtabs[0]:
            fig1 = px.bar(df_filtrado, x="Material", y="Volumen (m³)", color="Material", height=400, text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)
        with subtabs[1]:
            fig2 = px.bar(df_filtrado, x="Material", y="Área (m²)", color="Material", height=400, text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)
        with subtabs[2]:
            fig3 = px.bar(df_filtrado, x="Material", y="Longitud (m)", color="Material", height=400, text_auto=True)
            st.plotly_chart(fig3, use_container_width=True)
        with subtabs[3]:
            fig4 = px.bar(
                df_filtrado,
                x="Material",
                y="Huella CO2e (kg)",
                color="Material",
                height=400,
                text_auto=True,
                labels={"Huella CO2e (kg)": "CO₂ (kg)"}
            )
            if "Huella Máx (kg)" in df_filtrado.columns and "Huella Mín (kg)" in df_filtrado.columns:
                fig4.update_traces(
                    error_y=dict(
                        type="data",
                        array=df_filtrado["Huella Máx (kg)"] - df_filtrado["Huella CO2e (kg)"],
                        arrayminus=df_filtrado["Huella CO2e (kg)"] - df_filtrado["Huella Mín (kg)"]
                    )
                )
            st.plotly_chart(fig4, use_container_width=True)
        with subtabs[4]:
            df_percent = df_filtrado.copy()
            df_percent["% Volumen"] = 100 * df_percent["Volumen (m³)"] / total_vol if total_vol else 0
            fig5 = px.pie(df_percent, names="Material", values="% Volumen", title="Porcentaje de Volumen por Material")
            st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        st.markdown(f"""
        - Número de materiales detectados: `{len(df_filtrado)}`
        - Número de materiales bien clasificados (≥70%): `{(df_filtrado['Similitud (%)'] >= 70).sum()}`
        - Huella de carbono total: `{co2_total:,.2f} kg CO₂`
        - Rango de incertidumbre: `[ {df_filtrado['Huella Mín (kg)'].sum():,.2f} - {df_filtrado['Huella Máx (kg)'].sum():,.2f} ] kg CO₂`
        - Material con mayor impacto: `{df_filtrado.loc[df_filtrado['Huella CO2e (kg)'].idxmax()]['Material'] if not df_filtrado.empty else '-'}`

        **Fecha de análisis:** `{datetime.now().strftime('%Y-%m-%d %H:%M')}`
        """)

    with tab4:
        info_cols = st.columns(4)
        info_cols[0].metric("Archivo IFC", uploaded_file.name)
        info_cols[1].metric("Proyecto", info_ifc.get("Nombre proyecto", "-"))
        info_cols[2].metric("Nº elementos", info_ifc.get("Nº elementos", "-"))
        info_cols[3].metric("Fecha análisis", datetime.now().strftime("%Y-%m-%d %H:%M"))

        st.markdown(f"""
            - **Descripción del proyecto:** {info_ifc.get("Descripción proyecto", "-")}
            - **GlobalId del proyecto:** {info_ifc.get("GlobalId proyecto", "-")}
            - **Nombre emplazamiento:** {info_ifc.get("Nombre emplazamiento", "-")}
            - **Longitud:** {info_ifc.get("Longitud", "-")}
            - **Latitud:** {info_ifc.get("Latitud", "-")}
            - **Elevación:** {info_ifc.get("Elevación", "-")}
            - **Dirección:** {info_ifc.get("Dirección", "-")}
            - **Unidades:** {info_ifc.get("Unidades", "-")}
            """)

        tipos = info_ifc.get("Tipos de entidades", {})
        if tipos and isinstance(tipos, dict):
            st.markdown("**Tipos de entidades presentes:**")
            st.dataframe(pd.DataFrame(list(tipos.items()), columns=["Tipo IFC", "Cantidad"]), hide_index=True)

        lat = ifc_coord_to_decimal(info_ifc.get("Latitud", None))
        lon = ifc_coord_to_decimal(info_ifc.get("Longitud", None))
        if lat is not None and lon is not None:
            st.markdown("**Ubicación del emplazamiento:**")
            df_map = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(df_map)
        else:
            st.warning("No se pudieron mostrar las coordenadas en el mapa.")

    with tab_dashboard:
        st.markdown("### Dashboard comparativo y mapa de impacto")
        materiales_sel = st.multiselect(
            "Materiales a comparar",
            options=df_filtrado["Material"].unique(),
            default=df_filtrado["Material"].unique()[:5],
        )
        magnitudes_sel = st.multiselect(
            "Magnitudes a mostrar",
            options=[
                "Volumen (m³)",
                "Área (m²)",
                "Longitud (m)",
                "Huella CO2e (kg)",
                "Huella Mín (kg)",
                "Huella Máx (kg)",
            ],
            default=["Volumen (m³)", "Huella CO2e (kg)"],
        )
        df_dash = df_filtrado[df_filtrado["Material"].isin(materiales_sel)]

        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        with row1_col1:
            st.markdown("#### Magnitudes por Material")
            fig_bar = go.Figure()
            colors = ["#90caf9", "#1976d2", "#1565c0", "#ff9800", "#ffd699", "#e65100"]
            for i, mag in enumerate(magnitudes_sel):
                fig_bar.add_trace(
                    go.Bar(
                        x=df_dash["Material"],
                        y=df_dash[mag],
                        name=mag,
                        marker_color=colors[i % len(colors)],
                    )
                )
            fig_bar.update_layout(
                barmode="group",
                xaxis_title="Material",
                yaxis_title="Valor",
                legend_title="Magnitud",
                height=350,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with row1_col2:
            st.markdown("#### Radar comparativo")
            if len(materiales_sel) > 1 and len(magnitudes_sel) > 1:
                fig_radar = go.Figure()
                for i, mat in enumerate(materiales_sel):
                    fig_radar.add_trace(
                        go.Scatterpolar(
                            r=[df_dash[df_dash["Material"] == mat][mag].values[0] for mag in magnitudes_sel],
                            theta=magnitudes_sel,
                            fill="toself",
                            name=mat,
                        )
                    )
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    height=350,
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Selecciona al menos 2 materiales y 2 magnitudes para el radar.")

        with row2_col1:
            st.markdown("#### Distribución de Volumen (%)")
            if "Volumen (m³)" in df_dash.columns:
                fig_pie = px.pie(
                    df_dash,
                    names="Material",
                    values="Volumen (m³)",
                    title="Distribución de Volumen (%)",
                    color_discrete_sequence=px.colors.sequential.Blues,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("#### Boxplot de Huella CO₂")
            if "Huella CO2e (kg)" in df_dash.columns:
                fig_box = px.box(
                    df_dash,
                    y="Huella CO2e (kg)",
                    points="all",
                    color="Material",
                    title="Distribución de Huella CO₂",
                    color_discrete_sequence=px.colors.sequential.Oranges,
                )
                st.plotly_chart(fig_box, use_container_width=True)

        with row2_col2:
            st.markdown("#### Evolución de Huella CO₂")
            if "Huella CO2e (kg)" in magnitudes_sel:
                fig_line = go.Figure()
                for mag, colr in zip(
                        ["Huella CO2e (kg)", "Huella Mín (kg)", "Huella Máx (kg)"],
                        ["#ff9800", "#ffd699", "#e65100"]
                ):
                    if mag in df_dash.columns and mag in magnitudes_sel:
                        fig_line.add_trace(
                            go.Scatter(
                                x=df_dash["Material"],
                                y=df_dash[mag],
                                mode="lines+markers",
                                name=mag,
                                line=dict(color=colr),
                            )
                        )
                fig_line.update_layout(
                    xaxis_title="Material",
                    yaxis_title="CO₂ (kg)",
                    legend_title="Magnitud",
                    height=350,
                )
                st.plotly_chart(fig_line, use_container_width=True)

            st.markdown("#### Heatmap de correlación")
            if len(magnitudes_sel) > 1:
                corr = df_dash[magnitudes_sel].corr()
                fig_heat = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale="Blues",
                    title="Correlación entre magnitudes",
                    aspect="auto"
                )
                st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("#### Mapa de calor de impacto (ubicación del emplazamiento)")
        fig_mapa = generar_mapa_calor(df, info_ifc)
        if fig_mapa:
            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.info("No hay coordenadas geográficas suficientes para el mapa de calor.")

    with tab_3d:
        st.markdown("### Mapa 3D ambiental de materiales (Huella de carbono)")
        fig_3d = generar_mapa_3d_materiales(df_filtrado, info_ifc)
        if fig_3d:
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("No hay coordenadas geográficas suficientes o datos ambientales para mostrar el mapa 3D.")
        st.info("El eje Z representa la huella de carbono de cada material en el emplazamiento. El tamaño y color del punto indican el impacto ambiental relativo.")
