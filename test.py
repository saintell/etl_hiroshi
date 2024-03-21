import re
import chardet
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

# Widget para cargar archivo y obtener la ruta de la carpeta
st.title("Seleccionar Carpeta")
uploaded_file = st.file_uploader("Cargar archivo", type=["txt", "csv", "xlsx"])

if uploaded_file is not None:
    folder_path = os.path.dirname(uploaded_file.name)
    file_path = uploaded_file.name

    # Intenta adivinar la codificación del archivo
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    # Intenta leer el archivo con la codificación adivinada y manejo de errores
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            lines = f.readlines()
        df = pd.DataFrame([line.split('\t') for line in lines])
    except UnicodeDecodeError:
        st.error("Error al leer el archivo. Asegúrate de utilizar la codificación correcta.")

    # Leer el archivo y extraer las líneas de interés
    with open(file_path, 'r') as file:
        contenido = file.read()

    # Dividir la cadena por líneas
    lineas = contenido.split('\n')

    data = []  # Lista para almacenar las líneas que cumplen con el criterio

    extrayendo = False  # Variable para rastrear si estamos extrayendo líneas

    for linea in lineas:
        # Buscar la expresión "09LT0401 (A-4)" en cada línea
        match = re.search(r'09LT0401 \(A-4\)', linea)

        if match:
            # Si se encuentra la expresión, establecer la variable para comenzar a extraer líneas
            extrayendo = True

        if extrayendo:
            # Agregar la línea a la lista
            data.append(linea)

    # Crear un DataFrame de Pandas con los datos
    df = pd.DataFrame([linea.split('\t') for linea in data])

    # Creamos una función personalizada para aplicar la expresión regular y extraer la fecha
    def extraer_fecha(texto):
        match = re.search(r'#(.*?)#', texto)
        if match:
            return match.group(1)
        else:
            return texto

    # Aplicamos la función a la columna 0 y creamos una nueva columna llamada "Fecha"
    df[0] = df[0].apply(extraer_fecha)

    # Crear un nuevo DataFrame con las columnas necesarias y filtrar las filas con fechas nulas
    # Crear un DataFrame con formato de columnas numéricas
    df_grafico = pd.DataFrame({
        'Fecha': pd.to_datetime(df.iloc[:, 0], errors='coerce'),
        'Parametro 1': pd.to_numeric(df.iloc[:, 1], errors='coerce'),
        'Parametro 2': pd.to_numeric(df.iloc[:, 2], errors='coerce'),
        'Parametro 3': pd.to_numeric(df.iloc[:, 3], errors='coerce'),
        'Parametro 4': pd.to_numeric(df.iloc[:, 4], errors='coerce'),
        'Parametro 5': pd.to_numeric(df.iloc[:, 5], errors='coerce')
    }).dropna(subset=['Fecha'])

    # Sidebar para seleccionar columnas y tipo de gráfico
    selected_columns = st.sidebar.multiselect('Seleccionar columnas', df_grafico.columns)
    chart_type = st.sidebar.selectbox('Seleccionar tipo de gráfico', ['linea', 'puntos', 'barras'])

    if selected_columns:  # Asegúrate de que se seleccionen columnas antes de intentar graficar
        # Graficar
        plt.figure(figsize=(10, 6))

        if chart_type == 'linea':
            for col in selected_columns:
                plt.plot(df_grafico['Fecha'], df_grafico[col], marker='o')
            plt.title('Gráfico de Línea')
            plt.xlabel('Fecha')
            plt.ylabel('Valores')
        elif chart_type == 'puntos':
            if len(selected_columns) >= 2:
                for col in selected_columns:
                    plt.scatter(df_grafico['Fecha'], df_grafico[col], label=col, marker='o')
                plt.title('Gráfico de Puntos')
                plt.xlabel('Fecha')
                plt.ylabel('Valores')
                plt.legend()
            else:
                st.error("Selecciona al menos dos columnas para el gráfico de puntos.")
        elif chart_type == 'barras':
            fig, ax = plt.subplots(figsize=(10, 6))
            df_grafico.plot(x='Fecha', y=selected_columns, kind='bar', ax=ax)
            plt.title('Gráfico de Barras')

        # Mostrar el gráfico
        st.pyplot(plt.gcf())
    else:
        st.error("Por favor, selecciona al menos una columna para graficar.")
else:
    st.warning("Por favor, carga un archivo para continuar.")
