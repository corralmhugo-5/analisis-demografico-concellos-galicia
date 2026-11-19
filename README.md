# 📊 Vilalba, Ordes y Salvaterra de Miño: análisis demográfico

Dashboard interactivo en **Python + Streamlit** que compara la evolución demográfica de tres concellos gallegos con situaciones muy distintas:

| Concello | Provincia | Situación |
|---|---|---|
| Vilalba | Lugo | Interior, cabecera de la Terra Chá |
| Ordes | A Coruña | Eje A Coruña – Santiago |
| Salvaterra de Miño | Pontevedra | Frontera con Portugal |

## Qué analiza

- Evolución de la población 2010–2025 (en habitantes e índice base 100)
- Proporción de hombres y mujeres
- Edad media por sexo
- Población extranjera 2021–2025

## Conclusiones

- **Población:** Salvaterra de Miño es el único concello que crece con claridad (+12,3 % desde 2010). Ordes se mantiene estable (+0,9 %) y Vilalba pierde un 9,6 %.
- **Envejecimiento:** Vilalba es el más envejecido (50,5 años de edad media), frente a Ordes (47,3) y Salvaterra (46,3).
- **Hombres y mujeres:** Vilalba tiene la mayor proporción de mujeres (51,6 %), coherente con una población más envejecida; Salvaterra está prácticamente equilibrado.
- **Población extranjera:** crece en los tres desde 2022. Salvaterra tiene el porcentaje más alto (10,3 %) y Ordes el crecimiento más rápido (del 4,9 % al 8,7 %).
- **En resumen:** los concellos con más llegada de población extranjera son los que ganan o mantienen habitantes, mientras Vilalba sigue perdiendo población.

## Estructura del proyecto

```
├── app.py                         # Dashboard de Streamlit
├── notebooks/
│   └── 01_descarga_y_limpieza.ipynb   # Descarga, limpieza, control de calidad e indicadores
├── data/
│   ├── raw/          # Descargas originales del INE (no se suben: se regeneran con el notebook)
│   ├── manual/       # Edad media de las fichas municipales del IGE
│   └── processed/    # Datos limpios que usa la app
└── requirements.txt
```

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

# 1. (Opcional) Regenerar los datos: ejecutar el notebook notebooks/01_descarga_y_limpieza.ipynb
# 2. Lanzar la app
streamlit run app.py
```

## Datos y metodología

- **INE – Cifras oficiales de población** (Revisión del Padrón Municipal), vía API JSON: tablas 2868 (A Coruña), 2880 (Lugo) y 2890 (Pontevedra).
- **INE – Censo anual de población**, tabla 68537 (población por sexo y nacionalidad): *extranjeros = población total − nacionalidad española*.
- **IGE** (Instituto Galego de Estatística): edad media de las fichas municipales.
- Controles de calidad en el notebook: hombres + mujeres = total, años sin huecos y detección de saltos anuales anómalos.
- Las fichas municipales del IGE se descartaron como fuente de población extranjera porque sus cifras no cuadraban (hombres + mujeres ≠ total).

## Tecnologías

Python · pandas · Plotly · Streamlit · Jupyter · API del INE

## Autor

**Hugo Corral Muiño** – Máster en Big Data Analytics
