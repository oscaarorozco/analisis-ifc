# Análisis de Materiales y Huella de Carbono en Archivos IFC

Esta aplicación permite analizar archivos IFC (Industry Foundation Classes) para extraer información sobre materiales, calcular su huella de carbono y generar informes visuales y descargables. Está orientada a ingenieros, arquitectos y técnicos que deseen evaluar el impacto ambiental de sus modelos BIM.
 

## 🚀 Características principales

  

-  **Carga de archivos IFC** y extracción automática de materiales y magnitudes (volumen, área, longitud).

-  **Clasificación inteligente de materiales** mediante similitud textual y palabras clave.

-  **Cálculo de huella de carbono (CO₂e)** por material y total del proyecto.

-  **Corrección manual de clasificaciones** para afinar los resultados.

-  **Visualización interactiva** de datos, gráficos y mapas 3D.

-  **Exportación de resultados** a Excel, JSON e informes PDF detallados.

-  **Alertas y checklist de fiabilidad** para mejorar la calidad de los datos.

  
  

## 🖥️ Demo rápida

  1. Ejecuta la aplicación:


```bash

streamlit  run  app.py

```

  

2. Sube tu archivo IFC desde la barra lateral.

3. Explora los resultados, corrige clasificaciones si lo necesitas y descarga los informes.

  

## 📦 Instalación

  

### Requisitos previos

  

- Python 3.8 o superior (recomendado Python 3.10+)

- pip actualizado

  
  

### Instalación de dependencias

  

Ejecuta en tu terminal:

  

```bash

pip  install  streamlit  ifcopenshell  pandas  rapidfuzz  matplotlib  plotly  numpy  seaborn  openpyxl

```

  

>  **Nota:**

> Si tienes problemas con `ifcopenshell`, consulta [su documentación oficial](https://github.com/IfcOpenShell/IfcOpenShell) para instalar la versión compatible con tu sistema operativo y versión de Python.

  

### Clona este repositorio

  

```bash

git  clone  https://github.com/oscaarorozco/analisis-ifc.git

cd  analisis-ifc

```

  
  

## ⚙️ Uso

  

1. Lanza la aplicación con Streamlit:

  

```bash

streamlit  run  app.py

```

  

2. Accede desde tu navegador.

3. Sube un archivo IFC usando el panel lateral.

4. Ajusta los parámetros de similitud y filtros según tus necesidades.

5. Revisa las tablas, gráficos y alertas generadas.

6. Descarga los resultados en Excel, JSON o PDF desde el apartado de descargas.

  

## 📝 Explicación de la aplicación

  

-  **Carga y análisis IFC:**

El sistema procesa el archivo IFC, identifica todos los materiales y extrae sus magnitudes (volumen, área, longitud).

-  **Clasificación de materiales:**

Se compara cada material con una base de datos de materiales y palabras clave para asignar la denominación y el factor de emisión de CO₂ más adecuado.

-  **Cálculo de huella de carbono:**

Se multiplica el volumen (u otra magnitud relevante) por el factor de emisión correspondiente.

-  **Corrección manual:**

Puedes corregir la clasificación de cualquier material desde la barra lateral.

-  **Visualización y exportación:**

Visualiza gráficos de barras, mapas 3D y descarga los resultados en varios formatos.
  

## 🛠️ Personalización y lista de materiales

  

- Puedes ampliar la tabla de materiales (`CLASIFICACION_MATERIALES`) en el código para adaptarla a tus necesidades.

- Adapta los umbrales de similitud y las palabras clave según los materiales de tus proyectos.
