import streamlit as st
import pandas as pd
import plotly.express as px

#configuración de la página
st.set_page_config(page_title="Dashboard de Ventas", page_icon="📊", layout="wide")

#función para cargar y procesar los datos con cache
@st.cache_data
def load_data()->pd.DataFrame:
    """
    Carga los dos archivos csv dede Github Releases,
    los concatena y prepara las columnas necesarias
    
    Returns
        pd.DataFrame: DataFrame con todos los datos unidos y procesados
        
    """
    #cargamos los csv
    url1 = "https://github.com/ssanchezguillan/practica_final_streamlit/releases/download/v1.0/parte_1.csv"
    url2 = "https://github.com/ssanchezguillan/practica_final_streamlit/releases/download/v1.0/parte_2.csv"

    usecols = [
        "date", "store_nbr", "family", "sales", "onpromotion",
        "transactions", "city", "state", "store_type",
        "year", "month", "week", "day_of_week"
    ]

    df1 = pd.read_csv(url1, usecols=usecols, low_memory=False)
    df2 = pd.read_csv(url2, usecols=usecols, low_memory=False)

    df = pd.concat([df1,df2], ignore_index=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce") #convertimos la columna date a tipo datetime

    return df

#usamos spinner para avisar al usuario de que se están cargando los DataFrames
with st.spinner("Cargando datos..."):
    df = load_data()
st.success("Datos cargados correctamente") #confirmación visual de que se han descargado correctamente los DataFrames

tab1, tab2, tab3, tab4 = st.tabs(["Visión Global", "Análisis por Tiendas", "Análisis por Estado", "Extra"])

#------------------------------------
#PESTAÑA 1: VISION GLOBAL
with tab1:
    #título de la pestaña
    st.header("Visión Global de Ventas")
    st.write("Esta pestaña resume los KPIs generales del negocio")

    #CONTEOS GENERALES
    col1, col2, col3, col4 = st.columns(4)

    #número total de tiendas
    with col1:
        st.metric(label="Total Tiendas", value=df["store_nbr"].nunique())

    #número de total de productos en venta
    with col2:
        st.metric(label="Total Productos en Venta", value=df["family"].nunique())

    #estados en los que está la empresa
    with col3:
        st.metric(label="Estados en los que está la empresa", value=df["state"].nunique())

    #meses en los que se disponen datos para realizar el informe
    with col4:
        st.metric(label="Meses con Datos", value = df["month"].nunique())

    
    st.divider()

    #ANÁLISIS EN TÉRMINOS MEDIOS
    st.subheader("Análisis medio de ventas")

    #top 10 productos más vendidos
    top_productos = (df.groupby("family")["sales"].sum().sort_values(ascending=False).head(10).reset_index())
    
    #para representarlo dibujamos un gráfico de barras
    fig1 = px.bar(
        top_productos,
        x="sales",
        y="family",
        title="Top 10 productos más vendidos",
        labels={"sales":"Ventas Totales", "family": "Producto"})
    
    st.plotly_chart(fig1, use_container_width=True)

    #distribución de las ventas por tiendas
    ventas_tiendas = (df.groupby("store_nbr")["sales"].sum().reset_index())

    #para representarlo dibujamos un histograma
    fig2 = px.histogram(
        ventas_tiendas,
        x="sales",
        nbins = 30, 
        title = "Distribución de Ventas Totales por Tienda",
        labels={"sales": "Ventas por tienda"}
    )

    st.plotly_chart(fig2, use_container_width=True)


    #top 10 de tiendas con ventas en producto en promoción
    promo_stores = df[df["onpromotion"]>0]
    top_promo = (promo_stores.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10).reset_index())

    #lo representamos con un gráfico de barras
    fig3 = px.bar(
        top_promo,
        x="store_nbr",
        y="sales",
        title="Top 10 tiendas con ventas en productos en promoción",
        labels={"store_nbr":"Tienda", "sales":"Ventas en promoción"}
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    #ANÁLISIS DE ESTACIONALIDAD DE LAS VENTAS

    st.subheader("Estacionalidad de las ventas")
    #día de la semana con más ventas
    day = (df.groupby("day_of_week")["sales"].mean().reset_index())

    fig4 = px.bar(
        day,
        x="day_of_week",
        y="sales",
        title = "Ventas Promedio por Día de la Semana",
        labels = {"day_of_week":"Día", "sales":"Ventas Promedio"}
    )

    st.plotly_chart(fig4, use_container_width=True)

    #volumen de ventas medio por semana del año de todos los años del dataset
    week_sales = (df.groupby("week")["sales"].mean().reset_index())

    fig5 = px.line(
        week_sales, 
        x="week", 
        y="sales",
        title ="Ventas Medias por Semana del Año",
        labels={"week":"Semana", "sales":"Ventas Promedio"}  
    )
    st.plotly_chart(fig5, use_container_width=True)

    #volumen de ventas medio por mes en todos los años en dataset
    month_sales = (df.groupby("month")["sales"].mean().reset_index())

    fig6 = px.bar(
        month_sales, 
        x="month",
        y="sales",
        title="Ventas Medias por Mes",
        labels={"month":"Mes", "sales":"Ventas Promedio"}
    )

    st.plotly_chart(fig6, use_container_width=True)

#----------------------------------------
#PESTAÑA 2: 
with tab2:
    st.header("Análisis por Tienda")
    st.write("Selecciona una tienda para consultar sus métricas y comportamiento histórico")

    #DESPLEGABLE PARA ELEGIR LA TIENDA
    tiendas_disponibles = sorted(df["store_nbr"].unique()) #lista ordenada de tiendas

    tienda_seleccionada = st.selectbox("Selecciona una tienda:", tiendas_disponibles)

    #filtramos solo los datos en esa tienda
    df_tienda = df[df["store_nbr"] == tienda_seleccionada]

    st.divider()

    #ventas totales por año
    st.subheader("Ventas totales por año")
    ventas_por_year = (df_tienda.groupby("year")["sales"].sum().sort_index().reset_index())

    fig7 = px.bar(
        ventas_por_year,
        x="year", 
        y = "sales",
        title=f"Ventas Totales por Año - Tienda {tienda_seleccionada}",
        labels={"year":"Año", "sales":"Ventas Totales"}
    )
    st.plotly_chart(fig7, use_container_width=True)

    st.divider()

    #total de productos vendidos
    st.subheader("Total de productos vendidos")
    total_productos = df_tienda["sales"].sum()

    st.metric(
        label = f"Productos vendidos en la Tienda {tienda_seleccionada}",
        value = int(total_productos)
    )

    st.divider()

    #total de productos vendidos que estaban en promoción
    st.subheader("Total de productos vendidos en promoción")
    productos_promo = df_tienda[df_tienda["onpromotion"]>0]["sales"].sum()
    st.metric(
        label = f"Productos vendidos en la Tienda {tienda_seleccionada} en promoción",
        value = int(productos_promo)
    )
    st.divider()


#------------------------------------
#PESTAÑA 3

with tab3:
    st.header("Análisis por Estado")
    st.write("Selecciona un estado para analizar su comportamiento d eventas y actividad")

    #DESPLEGABLE DE ESTADOS
    estados_disponibles = sorted(df["state"].unique())
    estado_seleccionado = st.selectbox("Selecciona un estado:", estados_disponibles)

    #filtramos datos según el estado elegido
    df_estado = df[df["state"]==estado_seleccionado]

    st.divider()

    #número total de transacciones por año
    st.subheader("Total de transacciones por año")
    transacciones_por_year=(df_estado.groupby("year")["transactions"].sum().sort_index().reset_index())

    fig8 = px.bar(
        transacciones_por_year,
        x="year",
        y="transactions",
        title=f"Transacciones Totales por Año- Estado {estado_seleccionado}",
        labels={"year": "Año", "transactions": "Transacciones Totales"} 
    )
    st.plotly_chart(fig8, use_container_width=True)
    st.divider()

    #ranking de tiendas con más ventas
    st.subheader("Ranking de tiendas con más ventas")
    ranking_tiendas = (df_estado.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).reset_index().head(10))

    fig_b3 = px.bar(
        ranking_tiendas,
        x="store_nbr",
        y="sales",
        title=f"Top Tiendas por Ventas en el Estado {estado_seleccionado}",
        labels={"store_nbr": "Tienda", "sales": "Ventas Totales"}
    )

    st.plotly_chart(fig_b3, use_container_width=True)

    st.divider()

    #producto más vendido en la tienda
    st.subheader("Producto más vendido en el Estado")

    producto_estado = (df_estado.groupby("family")["sales"].sum().sort_values(ascending=False).reset_index())

    producto_top = producto_estado.iloc[0]

    st.metric(
        label="Producto más vendido",
        value=producto_top["family"],
        delta=f"{round(producto_top['sales'], 2)} ventas"
    )

    # Gráfico de barras de los 10 productos más vendidos
    fig9 = px.bar(
        producto_estado.head(10),
        x="sales",
        y="family",
        orientation="h",
        title=f"Top 10 Productos más Vendidos - Estado {estado_seleccionado}",
        labels={"family": "Producto", "sales": "Ventas Totales"}
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.divider()


#--------------------------
#PESTAÑA 4
with tab4:

    st.header("Insights Avanzados")
    st.write("Visualizaciones avanzadas para apoyar la toma de decisiones estratégicas")

    st.divider()

    #KPIs DESTACADAS DEL NEGOCIO
    st.subheader("Indicadores claves del negocio")

    col1, col2, col3 = st.columns(3)

    #ventas totales, el dinero generado por ventas
    ventas_totales = df["sales"].sum()

    #porcentaje de ventas en promoción
    ventas_promo = df[df["onpromotion"]>0]["sales"].sum()
    porcentaje_promo = (ventas_promo/ventas_totales)*100

    #tendencia vs año anterior, como cambian las ventas de un año a otro
    ventas_anuales = df.groupby("year")["sales"].sum()
    if len(ventas_anuales) >= 2:
        tendencia = ventas_anuales.iloc[-1] - ventas_anuales.iloc[-2]
    else:
        tendencia = 0

    with col1:
        st.metric(label="Ventas totales", value=f"{ventas_totales:,.0f} USD")

    with col2:
        st.metric(label="Porcentaje de Ventas en Promoción", value=f"{porcentaje_promo:.2f}%")
    
    with col3:
        st.metric(label="Variación en el último año", value=f"{tendencia:,.0f} USD")


    st.divider()

    #HEATMAP: VENTAS POR MES Y DÍA DE LA SEMANA
    st.subheader("Heatmap: Ventas por Mes y Día de la Semana")
    
    #para que no se ordenen por orden alfabético por defecto
    orden_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] 

    heatmap_data = (df.groupby(["day_of_week", "month"])["sales"].mean().reset_index())

    #convertimos a categoría ordenada
    heatmap_data["day_of_week"] = pd.Categorical(heatmap_data["day_of_week"], categories=orden_dias, ordered=True)

    heatmap_data = heatmap_data.sort_values(["day_of_week", "month"])

    fig_heat = px.density_heatmap(
        heatmap_data,
        x="month",
        y="day_of_week",
        z="sales",
        color_continuous_scale="Turbo",
        title="Heatmap de Ventas Promedio por Día y Mes"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    #CONTRIBUCIÓN POR TIPO DE TIENDA
    st.subheader("Contribución por Tipo de Tienda")

    contrib_store_type = (df.groupby("store_type")["sales"].sum().reset_index().sort_values("sales", ascending=False))

    fig_tipo = px.pie(
        contrib_store_type,
        names="store_type",
        values="sales",
        title="Proporción de Ventas por Tipo de Tienda",
        hole=0.4
    )

    st.plotly_chart(fig_tipo, use_container_width=True)

    st.divider()

    #¿QUÉ TIPO DE TIENDA RINDE MEJOR?
    st.subheader("Distribución de Ventas por Tipo de Tienda")

    fig_box = px.box(
        df,
        x="store_type",
        y="sales",
        title="Distribución de Ventas por Tipo de Tienda",
        labels={"store_type": "Tipo de tienda", "sales": "Ventas"}
    )

    st.plotly_chart(fig_box, use_container_width=True)

        
