import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io
import chardet

# Configuración base de la infraestructura web
st.set_page_config(page_title="ERP Dashboard Universal", layout="wide", page_icon="🏬")

st.title("🏬 Sistema Universal de Analítica de Ventas")
st.markdown("Carga las ventas de **cualquier negocio** (Farmacia, Colmado, Ropa, Repuestos). El sistema se adapta a tus datos.")

# Función avanzada para leer archivos CSV/Excel con codificación oculta
def cargar_datos_seguro(file):
    try:
        if file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file)
        else:
            # Detectar la codificación del archivo de forma automática (evita errores de tildes o la Ñ)
            bytes_data = file.read(10000)
            file.seek(0)
            encoding_detectada = chardet.detect(bytes_data)['encoding'] or 'utf-8'
            return pd.read_csv(file, encoding=encoding_detectada, sep=None, engine='python')
    except Exception as e:
        st.error(f"Error al procesar la estructura del archivo: {e}")
        return None

# Función para compilar el PDF de auditoría de negocio
def generar_pdf_universal(df, nombre_negocio, c_prod, c_cat, c_cant, c_total, ingresos, unidades, articulos, ticket):
    pdf = FPDF()
    pdf.add_page()
    
    # Banner ejecutivo superior
    pdf.set_fill_color(31, 41, 55) # Gris Oxford Industrial
    pdf.rect(0, 0, 210, 38, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"REPORTE OPERATIVO DE VENTAS", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 8, f"Establecimiento: {nombre_negocio}", ln=True, align='C')
    
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    
    # KPIs Financieros
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 8, "Métricas Clave de Rendimiento", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 8, f" Volumen de Facturacion Total: ${ingresos:,.2f}", border=1)
    pdf.cell(95, 8, f" Volumen de Articulos Despachados: {unidades:,}", border=1, ln=True)
    pdf.cell(95, 8, f" Variedad de Catalogo Vendido: {articulos}", border=1)
    pdf.cell(95, 8, f" Ticket Promedio por Transaccion: ${ticket:,.2f}", border=1, ln=True)
    
    pdf.ln(12)
    
    # Tabla de Movimientos
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 8, "Auditoría de Inventario Vendido (Top 15)", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    # Encabezados Adaptativos de Tabla
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(243, 244, 246)
    pdf.cell(65, 8, f"Descripción ({c_prod})", border=1, fill=True)
    pdf.cell(50, 8, f"Categoría ({c_cat})", border=1, fill=True)
    pdf.cell(35, 8, "Cantidades", border=1, fill=True)
    pdf.cell(40, 8, "Monto Total", border=1, fill=True, ln=True)
    
    # Filas de la tabla
    pdf.set_font("Arial", '', 9)
    for _, row in df.head(15).iterrows():
        txt_p = str(row[c_prod])[:32]
        txt_c = str(row[c_cat])[:24]
        cant_v = float(row[c_cant]) if pd.notnull(row[c_cant]) else 0.0
        tot_v = float(row[c_total]) if pd.notnull(row[c_total]) else 0.0
        
        pdf.cell(65, 7, txt_p, border=1)
        pdf.cell(50, 7, txt_c, border=1)
        pdf.cell(35, 7, f"{cant_v:,}", border=1)
        pdf.cell(40, 7, f"${tot_v:,.2f}", border=1, ln=True)
        
    return pdf.output()

# --- INTERFAZ DE CONFIGURACIÓN LATERAL ---
st.sidebar.header("⚙️ Configuración del Sistema")
nombre_comercio = st.sidebar.text_input("Nombre de tu Negocio:", value="Mi Negocio")

# Carga de archivos independiente
archivo = st.sidebar.file_uploader("Sube tu archivo de ventas (Excel o CSV)", type=["csv", "xlsx"])

if archivo is not None:
    df_origen = cargar_datos_seguro(archivo)
    
    if df_origen is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 Mapeo de Columnas Inteligente")
        st.sidebar.write("Indícale al sistema qué columna representa cada dato:")
        
        # Selectores dinámicos basados en las columnas REALES del archivo del usuario
        lista_columnas = list(df_origen.columns)
        
        col_producto = st.sidebar.selectbox("¿Cuál es el Nombre del Producto/Medicamento/Artículo?", lista_columnas)
        col_categoria = st.sidebar.selectbox("¿Cuál es la Categoría/Laboratorio/Familia?", lista_columnas)
        col_cantidad = st.sidebar.selectbox("¿Cuál es la Cantidad Vendida?", lista_columnas)
        col_total = st.sidebar.selectbox("¿Cuál es el Total Dinero ($) de la venta?", lista_columnas)
        
        # Forzar conversión numérica de columnas críticas para evitar caídas de gráficos
        df_origen[col_cantidad] = pd.to_numeric(df_origen[col_cantidad], errors='coerce').fillna(0)
        df_origen[col_total] = pd.to_numeric(df_origen[col_total], errors='coerce').fillna(0)
        
        # Filtro de categorías interactivo
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Filtro de Datos")
        opciones_cat = df_origen[col_categoria].dropna().unique()
        categorias_seleccionadas = st.sidebar.multiselect("Filtrar por categorías:", opciones_cat, default=opciones_cat)
        
        # Procesar DataFrame Filtrado
        df_filtrado = df_origen[df_origen[col_categoria].isin(categorias_seleccionadas)]
        
        # --- PROCESAMIENTO FINANCIERO DE MÉTRICAS ---
        m_ingresos = df_filtrado[col_total].sum()
        m_unidades = df_filtrado[col_cantidad].sum()
        m_articulos = df_filtrado[col_producto].nunique()
        m_ticket = df_filtrado[col_total].mean() if len(df_filtrado) > 0 else 0
        
        # --- BOTÓN DE DESCARGA PDF ---
        st.sidebar.markdown("---")
        try:
            binario_pdf = generar_pdf_universal(
                df_filtrado, nombre_comercio, col_producto, col_categoria, 
                col_cantidad, col_total, m_ingresos, m_unidades, m_articulos, m_ticket
            )
            st.sidebar.download_button(
                label="🖨️ Descargar Reporte en PDF",
                data=bytes(binario_pdf),
                file_name=f"Reporte_{nombre_comercio.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.sidebar.error(f"Error al estructurar reporte PDF: {e}")
            
        # --- DISEÑO DASHBOARD VISUAL ---
        st.subheader(f"📈 Rendimiento Comercial de: {nombre_comercio}")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Facturación Total", f"${m_ingresos:,.2f}")
        with kpi2:
            st.metric("Volumen Unidades Vendidas", f"{m_unidades:,.0f}")
        with kpi3:
            st.metric("Artículos Únicos Despachados", f"{m_articulos:,}")
        with kpi4:
            st.metric("Ticket Promedio de Compra", f"${m_ticket:,.2f}")
            
        st.markdown("---")
        
        # --- GRÁFICOS ANALÍTICOS ---
        fila_graficos_1 = st.columns(2)
        
        with fila_graficos_1[0]:
            st.subheader("💰 Distribución de Ingresos por Categoría")
            ventas_por_cat = df_filtrado.groupby(col_categoria)[col_total].sum().reset_index()
            fig_barras = px.bar(ventas_por_cat, x=col_categoria, y=col_total, color=col_categoria, text_auto='.2s', template="plotly_white")
            st.plotly_chart(fig_barras, use_container_width=True)
            
        with fila_graficos_1[1]:
            st.subheader("🏆 Top Productos Más Rentables")
            top_productos = df_filtrado.groupby(col_producto)[col_total].sum().reset_index().sort_values(by=col_total, ascending=False).head(10)
            fig_tarta = px.pie(top_productos, values=col_total, names=col_producto, hole=0.3, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_tarta, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📋 Consola Detallada de Datos Operativos")
        st.dataframe(df_filtrado[[col_producto, col_categoria, col_cantidad, col_total]], use_container_width=True)
        
else:
    # Estado inicial cuando no hay datos
    st.info("💡 **Instrucciones para iniciar:** Sube cualquier archivo CSV o Excel de ventas en el panel izquierdo. No importa el nombre de tus columnas, tú mismo las asignarás en la pantalla.")
