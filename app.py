#Librería para trabajar con archivos del sistema (la usamos para ver la fecha del CSV)
import os

#Librería para leer y manejar tablas de datos
import pandas as pd
#Librería para hacer gráficos interactivos
import plotly.express as px
#Librería que convierte este script en una app web
import streamlit as st

# ---------- 1. Configuración de la página ----------
#Título de la pestaña del navegador, icono y diseño a todo el ancho
st.set_page_config(page_title="Concellos de Galicia", page_icon="📊", layout="wide")

#Color fijo para cada concello en todos los gráficos
COLORES = {"Vilalba": "#2a78d6", "Ordes": "#eb6834", "Salvaterra de Miño": "#1baf7a"}


# ---------- 2. Carga de datos ----------
#Guarda el resultado en memoria para no releer los CSV en cada clic
@st.cache_data
#Función que carga los datos; si 'version' cambia, vuelve a leerlos
def cargar_datos(version):
    # 'version' = fecha de modificación del CSV: si el notebook lo regenera, la caché se renueva sola
    # Lee la tabla de indicadores de población
    ind = pd.read_csv("data/processed/indicadores_poblacion.csv")
    # Lee la tabla larga con todos los indicadores
    tidy = pd.read_csv("data/processed/concellos_tidy.csv")
    # Devuelve las dos tablas
    return ind, tidy


#Carga los datos pasando la fecha de modificación del CSV
ind, tidy = cargar_datos(os.path.getmtime("data/processed/concellos_tidy.csv"))

# ---------- 3. Barra lateral ----------
#Título de la barra lateral
st.sidebar.title("Opciones")
#Lista de concellos sin repetir y ordenada
todos = sorted(ind["concello"].unique())
#Selector de concellos; guarda los que elige el usuario
concellos = st.sidebar.multiselect("Concellos", options=todos, default=todos)

# Primer y último año disponibles en los datos
anyo_min, anyo_max = int(ind["anyo"].min()), int(ind["anyo"].max())
# Deslizador de años: empieza en 2010 y llega al último año
rango = st.sidebar.slider("Años", anyo_min, anyo_max, (2010, anyo_max))

# Botón para elegir entre índice base 100 o habitantes
modo = st.sidebar.radio("Mostrar población como", ["Índice base 100", "Habitantes"])
# Texto pequeño con las fuentes
st.sidebar.caption("Fuentes: INE e IGE")

# Si no hay ningún concello elegido...
if not concellos:
    # ...muestra un aviso amarillo...
    st.warning("Elige al menos un concello en la barra lateral.")
    # ...y para la app aquí para que no falle lo de abajo
    st.stop()

# Filtra los concellos y años elegidos
datos = ind[ind["concello"].isin(concellos) & ind["anyo"].between(*rango)]
# Población de cada concello en el primer año del rango
base = datos[datos["anyo"] == rango[0]].set_index("concello")["total"]
# Calcula el índice base 100 (población / población base x 100)
datos = datos.assign(indice=datos["total"] / datos["concello"].map(base) * 100)

# ---------- 4. Título y tarjetas ----------
#Título principal de la app
st.title("📊 Vilalba, Ordes y Salvaterra de Miño")
#Subtítulo con el rango de años elegido
st.caption(f"Población, sexo, extranjeros y edad media · {rango[0]}–{rango[1]}")


#Función para formatear números
def formato(n):
    # Pone el punto de miles al estilo español (13.852)
    return f"{n:,.0f}".replace(",", ".")


#Crea una columna por cada concello elegido
columnas = st.columns(len(concellos))
#Recorre cada columna junto con su concello
for col, concello in zip(columnas, concellos):
    #Datos del concello en el último año del rango
    fila = ind[(ind["concello"] == concello) & (ind["anyo"] == rango[1])]
    #Datos del concello en el año anterior
    previa = ind[(ind["concello"] == concello) & (ind["anyo"] == rango[1] - 1)]
    #Población del último año
    actual = fila["total"].iloc[0]
    #Por defecto, sin variación
    delta = None
    #Si existe el dato del año anterior...
    if not previa.empty:
        # ...calcula la diferencia de habitantes...
        cambio = actual - previa["total"].iloc[0]
        # ...y le da formato con signo, p. ej. "+65 vs 2024"
        delta = f"{cambio:+,.0f} vs {rango[1] - 1}".replace(",", ".")
    # Dibuja la tarjeta con nombre, población y variación
    col.metric(f"{concello} ({rango[1]})", formato(actual), delta)

# ---------- 5. Gráfico de población ----------
# Subtítulo de la sección
st.subheader("Evolución de la población")
# Elige qué columna dibujar según el botón de la barra lateral
y = "indice" if modo == "Índice base 100" else "total"
# Gráfico de líneas: una línea por concello, colores fijos y etiquetas en español
fig = px.line(
    datos, x="anyo", y=y, color="concello", color_discrete_map=COLORES, markers=True,
    labels={"anyo": "Año", "indice": f"Índice ({rango[0]} = 100)", "total": "Habitantes", "concello": ""},
)
# Solo en modo índice...
if y == "indice":
    # ...dibuja una línea gris de referencia en 100
    fig.add_hline(y=100, line_dash="dot", line_color="gray")
# Muestra el gráfico en la app
st.plotly_chart(fig)

# ---------- 6. % de mujeres y edad media ----------
# Divide la pantalla en dos columnas
col1, col2 = st.columns(2)

# Columna izquierda
with col1:
    # Subtítulo "% de mujeres"
    st.subheader("% de mujeres")
    # Gráfico de líneas del % de mujeres por año
    fig = px.line(
        datos, x="anyo", y="pct_mujeres", color="concello", color_discrete_map=COLORES,
        labels={"anyo": "Año", "pct_mujeres": "% de mujeres", "concello": ""},
    )
    # Línea de referencia en el 50 %
    fig.add_hline(y=50, line_dash="dot", line_color="gray")
    # Muestra el gráfico
    st.plotly_chart(fig)

# Columna derecha
with col2:
    # Subtítulo "Edad media"
    st.subheader("Edad media (último dato)")
    # Filtra solo las filas de edad media de los concellos elegidos
    edad = tidy[(tidy["indicador"] == "edad_media") & tidy["concello"].isin(concellos)]
    # Se queda con el último año disponible de cada concello y sexo
    edad = edad.sort_values("anyo").groupby(["concello", "sexo"]).tail(1)
    # Barras agrupadas por sexo con el valor escrito encima
    fig = px.bar(
        edad, x="concello", y="valor", color="sexo", barmode="group", text_auto=".1f",
        labels={"concello": "", "valor": "Años", "sexo": ""},
    )
    # Fija el eje Y entre 40 y 55 años para que se vean las diferencias
    fig.update_yaxes(range=[40, 55])
    # Muestra el gráfico
    st.plotly_chart(fig)

# ---------- 7. Población extranjera ----------
# Subtítulo de la sección
st.subheader("Población extranjera")
# Filtra el % de extranjeros de los concellos elegidos
pct = tidy[(tidy["indicador"] == "pct_extranjeros") & tidy["concello"].isin(concellos)]
# Filtra el número total de extranjeros
num = tidy[(tidy["indicador"] == "extranjeros") & (tidy["sexo"] == "total") & tidy["concello"].isin(concellos)]

# Dos columnas: la izquierda el doble de ancha
col3, col4 = st.columns([2, 1])
# Columna izquierda
with col3:
    # Gráfico de líneas del % de extranjeros por año
    fig = px.line(
        pct, x="anyo", y="valor", color="concello", color_discrete_map=COLORES, markers=True,
        labels={"anyo": "Año", "valor": "% de población extranjera", "concello": ""},
    )
    # Un año en cada marca del eje (sin decimales)
    fig.update_xaxes(dtick=1)
    # Muestra el gráfico
    st.plotly_chart(fig)
# Columna derecha
with col4:
    # Último año con datos de extranjeros
    ultimo_ext = num["anyo"].max()
    # Número de extranjeros de ese año, unido con su %, con columnas en español
    tabla = (num[num["anyo"] == ultimo_ext][["concello", "valor"]]
             .merge(pct[pct["anyo"] == ultimo_ext][["concello", "valor"]], on="concello", suffixes=("", "_pct"))
             .rename(columns={"concello": "Concello", "valor": "Extranjeros", "valor_pct": "%"}))
    # Quita los decimales (618.0 -> 618)
    tabla["Extranjeros"] = tabla["Extranjeros"].astype(int)
    # Año en negrita encima de la tabla
    st.markdown(f"**Año {ultimo_ext}**")
    # Muestra la tabla sin la columna de números de fila
    st.dataframe(tabla, hide_index=True)
# Nota con la fuente y cómo se calculan los extranjeros
st.caption("Fuente: INE, Censo anual de población. Extranjeros = población total − nacionalidad española.")

# ---------- 8. Conclusiones y fuentes ----------
# Recuadro azul de conclusiones (escribe aquí tus frases)
st.info(
    "**Conclusiones**\n\n"
    "- **Población:** Salvaterra de Miño es el único concello que crece con claridad: +12,3 % desde 2010 "
    "(de 9.456 a 10.617 habitantes), sobre todo a partir de 2019. Ordes se mantiene estable (+0,9 %) "
    "y Vilalba pierde un 9,6 % (de 15.327 a 13.852), aunque en 2025 repunta ligeramente.\n"
    "- **Envejecimiento:** Vilalba es el más envejecido, con 50,5 años de edad media, unos 3 años más que "
    "Ordes (47,3) y 4 más que Salvaterra (46,3). En los tres, las mujeres tienen unos 3 años más de media que los hombres.\n"
    "- **Hombres y mujeres:** Vilalba tiene la mayor proporción de mujeres (51,6 %) y ha ido subiendo desde 2010, "
    "algo coherente con una población más envejecida. Salvaterra está prácticamente equilibrado (50,05 %).\n"
    "- **Población extranjera:** crece en los tres desde 2022. Salvaterra tiene el porcentaje más alto (10,3 % en 2025), "
    "Ordes el crecimiento más rápido (del 4,9 % al 8,7 %, de 618 a 1.122 personas) y Vilalba el más bajo (6,6 %).\n"
    "- **En resumen:** los concellos con más llegada de población extranjera (Salvaterra y Ordes) son los que ganan "
    "o mantienen habitantes, mientras que Vilalba, más envejecido y con menos inmigración, sigue perdiendo población."
)
# Pie con las fuentes y el autor
st.caption(
    "Fuentes: INE (Cifras oficiales de población, Revisión del Padrón Municipal) · "
    "IGE (fichas municipales). Elaborado por Hugo Corral Muiño."
)
