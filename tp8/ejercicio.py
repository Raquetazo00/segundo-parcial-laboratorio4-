import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración de la página
st.set_page_config(page_title="Datos de Ventas", layout="wide")

# Función para mostrar información del alumno
def mostrar_informacion_alumno():
    with st.container():
        st.markdown("### Información del Alumno")
        st.markdown('**Legajo:** 59.099')
        st.markdown('**Nombre:** Moyano Berrondo Tahiel Lisandro')
        st.markdown('**Comisión:** C5')

# Mostrar información del alumno en la barra lateral
st.sidebar.title("Información")
mostrar_informacion_alumno()

# Especifica la carpeta donde se encuentra el archivo CSV
folder_path = "ruta/a/tu/carpeta"  # Reemplaza con la ruta correcta
filename = "datos_ventas.csv"  # Nombre del archivo CSV

# Cargar archivo CSV desde la carpeta especificada
file_path = os.path.join(folder_path, filename)

# Verificar si el archivo existe
if os.path.exists(file_path):
    # Leer los datos
    data = pd.read_csv(file_path)
    
    sucursales = ["Todas"] + data["Sucursal"].unique().tolist()

    # Filtro por sucursal
    sucursal = st.sidebar.selectbox("Seleccionar Sucursal", sucursales)
    if sucursal != "Todas":
        data = data[data["Sucursal"] == sucursal]

    # Mostrar análisis por producto
    st.title(f"Datos de {'Todas las Sucursales' if sucursal == 'Todas' else sucursal}")

    for producto in data["Producto"].unique():
        producto_data = data[data["Producto"] == producto]

        # Calcular métricas totales
        total_ingreso = producto_data["Ingreso_total"].sum()
        total_unidades = producto_data["Unidades_vendidas"].sum()
        total_costo = producto_data["Costo_total"].sum()

        precio_promedio = total_ingreso / total_unidades if total_unidades > 0 else 0
        margen_promedio = ((total_ingreso - total_costo) / total_ingreso) * 100 if total_ingreso > 0 else 0
        unidades_vendidas = total_unidades

        # Calcular métricas del mes pasado
        producto_data["Fecha"] = pd.to_datetime(
            producto_data["Año"].astype(str) + "-" + producto_data["Mes"].astype(str) + "-01", errors="coerce"
        )
        producto_data = producto_data.dropna(subset=["Fecha"])
        producto_data = producto_data.sort_values("Fecha")

        if len(producto_data) > 1:
            # Obtener datos del último mes y del mes anterior
            datos_actuales = producto_data.iloc[-1]
            datos_pasados = producto_data.iloc[-2]

            precio_promedio_pasado = datos_pasados["Ingreso_total"] / datos_pasados["Unidades_vendidas"] if datos_pasados["Unidades_vendidas"] > 0 else 0
            margen_promedio_pasado = ((datos_pasados["Ingreso_total"] - datos_pasados["Costo_total"]) / datos_pasados["Ingreso_total"]) * 100 if datos_pasados["Ingreso_total"] > 0 else 0
            unidades_vendidas_pasadas = datos_pasados["Unidades_vendidas"]
        else:
            precio_promedio_pasado = precio_promedio
            margen_promedio_pasado = margen_promedio
            unidades_vendidas_pasadas = unidades_vendidas

        # Variaciones porcentuales
        variacion_precio = ((precio_promedio - precio_promedio_pasado) / precio_promedio_pasado * 100) if precio_promedio_pasado > 0 else 0
        variacion_margen = ((margen_promedio - margen_promedio_pasado) / margen_promedio_pasado * 100) if margen_promedio_pasado > 0 else 0
        variacion_unidades = ((unidades_vendidas - unidades_vendidas_pasadas) / unidades_vendidas_pasadas * 100) if unidades_vendidas_pasadas > 0 else 0

        # Mostrar métricas y variaciones
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader(producto)
            st.metric("Precio Promedio", f"${precio_promedio:,.2f}", f"{variacion_precio:.2f}%")
            st.metric("Margen Promedio", f"{margen_promedio:.2f}%", f"{variacion_margen:.2f}%")
            st.metric("Unidades Vendidas", f"{unidades_vendidas:,.0f}", f"{variacion_unidades:.2f}%")

        with col2:
            # Gráfico de evolución
            producto_data_grouped = producto_data.groupby(["Año", "Mes"]).agg({
                "Unidades_vendidas": "sum",
                "Ingreso_total": "sum"
            }).reset_index()

            producto_data_grouped["Fecha"] = pd.to_datetime(
                producto_data_grouped["Año"].astype(str) + "-" + producto_data_grouped["Mes"].astype(str) + "-01",
                errors="coerce"
            )
            producto_data_grouped = producto_data_grouped.dropna(subset=["Fecha"])
            producto_data_grouped = producto_data_grouped.sort_values("Fecha")

            # Crear el gráfico
            plt.figure(figsize=(10, 4))
            plt.plot(producto_data_grouped["Fecha"], producto_data_grouped["Ingreso_total"], label="Ingreso Total")
            plt.plot(
                producto_data_grouped["Fecha"],
                np.poly1d(np.polyfit(
                    np.arange(len(producto_data_grouped["Fecha"])),
                    producto_data_grouped["Ingreso_total"], 1
                ))(np.arange(len(producto_data_grouped["Fecha"]))),
                label="Tendencia", linestyle="--"
            )
            plt.title("Evolución de Ventas Mensual")
            plt.xlabel("Fecha")
            plt.ylabel("Ingreso Total")
            plt.legend()
            st.pyplot(plt)

else:
    st.info(f"No se encontró el archivo en la ruta: {file_path}. Por favor, verifica la ubicación del archivo.")
