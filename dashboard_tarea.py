# dashboard_tarea.py

import streamlit as st
import pandas as pd
import plotly.express as px
import math


# 1......
# Título y descripción
st.title("📊 Dashboard Interactivo de Ventas")
st.markdown("""
Este dashboard permite visualizar la evolución de las ventas, con datos limpios y transformados para facilitar el análisis temporal.
Incluye filtros interactivos y múltiples vistas para comprender mejor el comportamiento de las ventas.
""")

# Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce')
    df['Day'] = df['Date'].dt.day_name()
    df['Month'] = df['Date'].dt.month_name()
    df['Hour'] = df['Time'].dt.hour
    return df.dropna()

df = cargar_datos()

# Filtro de fechas
st.subheader("📅 Filtrar por Rango de Fechas")
fecha_min = df['Date'].min()
fecha_max = df['Date'].max()

fecha_inicio, fecha_fin = st.date_input(
    label="Selecciona el rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

df_filtrado = df[(df['Date'] >= pd.to_datetime(fecha_inicio)) & (df['Date'] <= pd.to_datetime(fecha_fin))]
# Filtro por línea de producto (si existe esta columna)
if 'Product line' in df.columns:
    st.subheader("📦 Filtrar por Línea de Producto")
    opciones = st.multiselect("Selecciona una o más líneas de producto:", df['Product line'].unique())
    if opciones:
        df_filtrado = df_filtrado[df_filtrado['Product line'].isin(opciones)]
# Filtro por mes
st.subheader("📆 Filtrar por Mes")
meses_unicos = df_filtrado['Month'].unique().tolist()
meses_ordenados = [m for m in ['January', 'February', 'March']
                   if m in meses_unicos]

meses_seleccionados = st.multiselect("Selecciona uno o más meses:", meses_ordenados)

if meses_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Month'].isin(meses_seleccionados)]
st.markdown("---")
# Métricas clave
st.subheader("📌 Indicadores Clave")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Ventas Totales", f"${df_filtrado['Total'].sum():,.2f}")

with col2:
    promedio_diario = df_filtrado.groupby('Date')['Total'].sum().mean()
    st.metric("📊 Promedio Diario", f"${promedio_diario:,.2f}")

with col3:
    st.metric("🧾 Total Transacciones", f"{len(df_filtrado):,}")

# Gráfico 1: Ventas Totales por Día
st.subheader("📈 Ventas Totales por Día")

ventas_diarias = df_filtrado.groupby('Date')['Total'].sum().reset_index()

fig1 = px.line(
    ventas_diarias,
    x='Date',
    y='Total',
    title='Evolución de las Ventas Totales',
    markers=True,
    labels={'Date': 'Fecha', 'Total': 'Ventas Totales (USD)'},
    template='plotly_white'
)

fig1.update_traces(line_color='darkorange')
fig1.update_layout(title_x=0.5)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Cantidad de Transacciones por Día
st.subheader("🧾 Cantidad de Transacciones por Día")

transacciones = df_filtrado.groupby('Date').size().reset_index(name='Cantidad')

fig2 = px.bar(
    transacciones,
    x='Date',
    y='Cantidad',
    title='Cantidad de Transacciones por Día',
    labels={'Cantidad': 'Número de Transacciones'},
    template='plotly_white'
)

st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Promedio de Ventas por Día de la Semana
st.subheader("📅 Promedio de Ventas por Día de la Semana")

ventas_dia = df_filtrado.groupby('Day')['Total'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
]).reset_index()

fig3 = px.bar(
    ventas_dia,
    x='Day',
    y='Total',
    title='Promedio de Ventas por Día de la Semana',
    labels={'Total': 'Promedio de Ventas (USD)'},
    template='plotly_white',
    color_discrete_sequence=['#636EFA']
)

st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Distribución de Ventas por Hora
st.subheader("⏰ Distribución de Ventas por Hora del Día")

fig4 = px.histogram(
    df_filtrado,
    x='Hour',
    y='Total',
    nbins=24,
    title='Distribución de Ventas por Hora',
    labels={'Hour': 'Hora del Día', 'Total': 'Ventas Totales'},
    template='plotly_white'
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Reflexión final
st.markdown("### 💬 Reflexión")
st.markdown("""
Gracias a la interactividad del dashboard, el usuario puede explorar distintos periodos de tiempo y visualizar 
patrones temporales en las ventas, tales como horas de mayor actividad, días más rentables, y distribución 
de transacciones. Esta visualización mejora la toma de decisiones operativas y comerciales.
""")

# Gráfico 5

# Título
st.subheader("📈 Relación entre Costos e Ingreso Bruto")

# Gráfico de dispersión
fig_scatter = px.scatter(
    df,
    x='cogs',
    y='gross income',
    title='Relación entre Costo de Bienes Vendidos e Ingreso Bruto',
    labels={'cogs': 'Costo de Bienes Vendidos', 'gross income': 'Ingreso Bruto'},
    opacity=0.6,
    color_discrete_sequence=['darkorange']
)


fig_scatter.update_layout(template='plotly_white', title_x=0)

st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown("---")


# Gráfico 6 
# Contar frecuencia de métodos de pago
payment_counts = df['Payment'].value_counts().reset_index()
payment_counts.columns = ['Método de Pago', 'Frecuencia']

# Título
st.subheader("💳 Frecuencia de Métodos de Pago")

# Gráfico
fig_bar = px.bar(
    payment_counts,
    x='Método de Pago',
    y='Frecuencia',
    text='Frecuencia',
    color='Método de Pago',
    title='Frecuencia de Métodos de Pago',
    labels={'Frecuencia': 'Cantidad de Transacciones'}
)

fig_bar.update_traces(textposition='outside')
fig_bar.update_layout(template='plotly_white', title_x=0)

st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("---")


# Gráficos de burbuja - Ingresos diarios por línea de producto
# Título
st.subheader("💰 Ingreso diario (USD) por Línea de Producto")

# Agrupar por fecha y línea de producto
data_agrupada = df_filtrado.groupby(['Date', 'Product line']).agg({
    'Total': 'sum',
    'Quantity': 'sum'
}).reset_index()

# Renombrar lineas de productos
renombres = {
    "Electronic accessories": "Accesorios Electrónicos",
    "Fashion accessories": "Accesorios de Moda",
    "Food and beverages": "Comida y Bebidas",
    "Health and beauty": "Salud y Belleza",
    "Home and lifestyle": "Hogar y Estilo de Vida",
    "Sports and travel": "Deportes y Viajes"
}
data_agrupada['Product line'] = data_agrupada['Product line'].replace(renombres)

# Gráfico de burbujas
fig_bubble_pl = px.scatter(
    data_agrupada,
    x="Date",
    y="Total",
    size="Quantity",
    color="Product line",
    hover_name="Product line",
    size_max=60,
    title="Ingreso Diario (USD) por Línea de Producto",
    labels={
        "gross income": "Ingreso Bruto (USD)",
        "Product line": "Línea de Producto",
        "Quantity": "Cantidad Vendida",
        "Date": "Fecha",
        "Total": "Total de Ingresos"
    }
)

fig_bubble_pl.update_layout(template='plotly_white', title_x=0)
st.plotly_chart(fig_bubble_pl, use_container_width=True)

st.markdown("---")


# Gráfico de burbujas  - Ingresos diarios (USD) por sucursal

# Título
st.subheader("💵 Ingreso diario (USD) por Sucursal")

# Agrupar por fecha y sucursal
data_agrupada = df_filtrado.groupby(['Date', 'Branch']).agg({
    'Total': 'sum',
    'Quantity': 'sum'
}).reset_index()

# Gráfico de burbujas
fig_bubble = px.scatter(
    data_agrupada,
    x="Date",
    y="Total",
    size="Quantity",
    color="Branch",
    hover_name="Branch",
    size_max=60,
    title="Ingreso diario (USD) por sucursal",
    labels={
        "Branch": "Sucursal",
        "gross income": "Ingreso Bruto (USD)",
        "Quantity": "Cantidad Vendida",
        "Date": "Fecha",
        "Total": "Total de Ingresos (USD)"
    }
)


fig_bubble.update_layout(template='plotly_white', title_x=0)
st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")


### Gráfico 3D

st.subheader("📅 Ingreso diario por Línea de Producto")

# Agrupar por Fecha y Línea de Producto
data_agrupada = df_filtrado.groupby(['Date', 'Product line']).agg({
    'gross income': 'sum',
    'Invoice ID': 'count'
}).reset_index()

data_agrupada.rename(columns={'Invoice ID': 'ventas'}, inplace=True)

# Crear gráfico 3D por Línea de Producto
fig_gapminder_pl = px.scatter_3d(
    data_agrupada,
    x='Date',
    y='Product line',
    z='gross income',
    size='ventas',
    color='ventas',
    hover_data=['ventas', 'gross income'],
    title='Ingreso bruto diario por línea de produco',
    labels={
        'gross income': 'Ingreso Bruto',
        'ventas': 'Ventas',
        'Date': 'Fecha',
        'Product line': 'Línea de Producto'
    }
)

# Ajustar tamaño
fig_gapminder_pl.update_layout(
    template='plotly_white', 
    title_x=0,
    width=1200,
    height=800
)

st.plotly_chart(fig_gapminder_pl, use_container_width=True)
st.markdown("---")

### Gráfico 3D


# Agrupar por Fecha y Sucursal
data_agrupada = df_filtrado.groupby(['Date', 'Branch']).agg({
    'gross income': 'sum',
    'Invoice ID': 'count'
}).reset_index()

data_agrupada.rename(columns={'Invoice ID': 'ventas'}, inplace=True)

# Crear gráfico 3D tipo Gapminder
fig_gapminder_br = px.scatter_3d(
    data_agrupada,
    x='Date',
    y='Branch',
    z='gross income',
    size='ventas',
    color='ventas',
    hover_data=['ventas', 'gross income'],
    title='Ingreso bruto diario por sucursal (estilo Gapminder 3D)',
    labels={
        'gross income': 'Ingreso Bruto',
        'ventas': 'Ventas',
        'Date': 'Fecha',
        'Branch': 'Sucursal'
    }
)

# Ajuste de tamaño
fig_gapminder_br.update_layout(
    template='plotly_white',
    title_x=0,
    width=1200,
    height=800
)

st.plotly_chart(fig_gapminder_br, use_container_width=True)
st.markdown("---")