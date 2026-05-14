import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. CONFIGURACIÓN DEL SISTEMA OPERATIVO WEB
st.set_page_config(page_title="Central de Paneles Empresariales", layout="wide", page_icon="🏢")

# --- MOTOR DE PERSISTENCIA NATIVA (Bases de datos independientes) ---
FICHERO_INV = "inv_central.csv"
FICHERO_VEN = "ven_central.csv"

def guardar_cambios(df, path):
    df.to_csv(path, index=False)

def iniciar_base_datos(path, cols):
    if os.path.exists(path):
        try: return pd.read_csv(path)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

# Inicializar almacenamiento en disco duro del servidor
if 'db_i' not in st.session_state:
    st.session_state.db_i = iniciar_base_datos(FICHERO_INV, ["ID", "Item", "Giro", "Grupo", "Especifico", "Costo", "Precio", "Stock", "Extra"])
    # Datos iniciales para que el sistema arranque con datos demostrativos en cada panel
    if st.session_state.db_i.empty:
        st.session_state.db_i = pd.DataFrame([
            {"ID": "R01", "Item": "Jeans Súper Slim", "Giro": "Boutique Ropa", "Grupo": "Pantalones", "Especifico": "Talla M / Azul", "Costo": 400, "Precio": 1100, "Stock": 25, "Extra": "Exhibición"},
            {"ID": "C01", "Item": "Saco Arroz Selecto", "Giro": "Colmado / Bodega", "Grupo": "Granos", "Especifico": "Saco 125 Lb", "Costo": 2100, "Precio": 2700, "Stock": 14, "Extra": "Vence: 2026-10-12"},
            {"ID": "A01", "Item": "Lote Zapatos Running", "Giro": "Almacén Mayorista", "Grupo": "Calzado", "Especifico": "Caja x24 Pares", "Costo": 12000, "Precio": 19000, "Stock": 8, "Extra": "Rack Sector C"}
        ])
if 'db_v' not in st.session_state:
    st.session_state.db_v = iniciar_base_datos(FICHERO_VEN, ["Fecha", "Item", "Giro", "Cantidad", "Costo_T", "Venta_T", "Ganancia", "Metodo"])

# =========================================================================
# 2. SELECTOR MAESTRO DE CONTROL: CAMBIA EL PANEL POR COMPLETO
# =========================================================================
st.sidebar.image("https://flaticon.com", width=70)
st.sidebar.header("🎛️ PANEL DE CONTROL")
interfaz_activa = st.sidebar.radio(
    "Selecciona el Entorno del Dashboard:",
    ["🛍️ PANEL: TIENDA DE ROPA / CALZADO", "🏪 PANEL: COLMADO / MINIMARKET", "📦 PANEL: ALMACÉN LOGÍSTICO / DEPOSITOS"]
)

st.sidebar.markdown("---")

# =========================================================================
# 🏢 DISEÑO INTERFAZ 1: TIENDA DE ROPA / CALZADO
# =========================================================================
if interfaz_activa == "🛍️ PANEL: TIENDA DE ROPA / CALZADO":
    st.title("🛍️ Dashboard Ejecutivo de Boutique & Moda")
    st.markdown("Control de tallas, marcas, aparadores, colecciones estacionales y ticket promedio.")
    
    # Filtrar solo datos de ropa
    df_ropa = st.session_state.db_i[st.session_state.db_i["Giro"] == "Boutique Ropa"]
    
    # Diseño de Pestañas exclusivas para Ropa
    p1, p2, p3 = st.tabs(["📊 Métricas de Moda", "➕ Ingresar Prenda/Calzado", "🛒 Punto de Venta"])
    
    with p1:
        st.subheader("Análisis de Tendencias y Exhibición")
        k1, k2, k3 = st.columns(3)
        k1.metric("Prendas Totales en Rack", f"{df_ropa['Stock'].sum()} Unidades")
        k2.metric("Inversión en Vitrinas", f"${df_ropa['Costo'].sum():,.2f}")
        k3.metric("Variedad de Modelos", len(df_ropa["Item"].unique()))
        
        st.markdown("---")
        st.write("📈 **Nivel de Stock por Talla / Modelo:**")
        if not df_ropa.empty:
            chart_ropa = df_ropa.groupby("Especifico")["Stock"].sum()
            st.bar_chart(chart_ropa)
            st.dataframe(df_ropa[["Item", "Grupo", "Especifico", "Stock", "Precio", "Extra"]], use_container_width=True)
            
    with p2:
        st.subheader("Añadir Nueva Colección al Aparador")
        with st.form("form_ropa", clear_on_submit=True):
            f_nom = st.text_input("Nombre de la Prenda / Calzado:")
            f_cat = st.selectbox("Colección / Departamento:", ["Pantalones", "Camisas", "Calzado", "Vestidos", "Accesorios"])
            f_esp = st.text_input("Detalle de Variantes (Ej: Talla L / Color Negro):")
            f_cos = st.number_input("Costo Fábrica ($):", min_value=0.0)
            f_pre = st.number_input("Precio Vitrina ($):", min_value=0.0)
            f_cant = st.number_input("Unidades que entran al Rack:", min_value=1)
            f_ex = st.selectbox("Área Visual:", ["Maniquí Entrada", "Perchero Principal", "Caja Reserva"])
            
            if st.form_submit_button("📥 Colocar en Exhibición") and f_nom.strip():
                nueva_p = pd.DataFrame([{"ID": "R", "Item": f_nom, "Giro": "Boutique Ropa", "Grupo": f_cat, "Especifico": f_esp, "Costo": f_cos, "Precio": f_pre, "Stock": f_cant, "Extra": f_ex}])
                st.session_state.db_i = pd.concat([st.session_state.db_i, nueva_p], ignore_index=True)
                guardar_cambios(st.session_state.db_i, FICHERO_INV)
                st.success("¡Prenda indexada!"); st.rerun()
                
    with p3:
        st.subheader("Pasarela de Pagos (POS Boutique)")
        if not df_ropa.empty:
            sel_p = st.selectbox("Selecciona Prenda:", df_ropa["Item"].unique(), key="s_r")
            items_v = df_ropa[df_ropa["Item"] == sel_p]
            sel_v = st.selectbox("Selecciona Variante:", items_v["Especifico"].unique(), key="v_r")
            row_r = items_v[items_v["Especifico"] == sel_v].iloc[0]
            
            c_vendar = st.number_input("Cantidad:", min_value=1, max_value=int(row_r["Stock"]), value=1, key="c_r")
            m_pago = st.selectbox("Forma de Cobro:", ["Efectivo", "Tarjeta", "Apartado de Prenda"], key="m_r")
            
            st.markdown(f"### Total Factura: ${c_vendar * row_r['Precio']:,.2f}")
            if st.button("🔴 Confirmar Venta de Mostrador", key="b_r"):
                # Operación descuento e historial
                v_costo = c_vendar * row_r["Costo"]
                v_total = c_vendar * row_r["Precio"]
                nueva_v = pd.DataFrame([{"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Item": sel_p, "Giro": "Boutique Ropa", "Cantidad": c_vendar, "Costo_T": v_costo, "Venta_T": v_total, "Ganancia": v_total - v_costo, "Metodo": m_pago}])
                st.session_state.db_v = pd.concat([st.session_state.db_v, nueva_v], ignore_index=True)
                guardar_cambios(st.session_state.db_v, FICHERO_VEN)
                
                for idx, fila in st.session_state.db_i.iterrows():
                    if fila["Item"] == sel_p and fila["Especifico"] == sel_v:
                        st.session_state.db_i.at[idx, "Stock"] -= c_vendar
                guardar_cambios(st.session_state.db_i, FICHERO_INV)
                st.success("Venta procesada"); st.rerun()

# =========================================================================
# 🏪 DISEÑO INTERFAZ 2: COLMADO / MINIMARKET
# =========================================================================
elif interfaz_activa == "🏪 PANEL: COLMADO / MINIMARKET":
    st.title("🏪 Dashboard de Control para Colmados & Minimarkets")
    st.markdown("Monitoreo agresivo de fiados, mermas de alimentos, inventarios rápidos y pesos.")
    
    df_col = st.session_state.db_i[st.session_state.db_i["Giro"] == "Colmado / Bodega"]
    
    p1, p2, p3 = st.tabs(["📓 Despacho e Historial Diario", "🌾 Control de Sacos / Abastecimiento", "🚨 Alertas de Vencimiento"])
    
    with p1:
        st.subheader("Ventas del Mostrador Diario")
        k1, k2 = st.columns(2)
        df_v_col = st.session_state.db_v[st.session_state.db_v["Giro"] == "Boutique Ropa"] # Simulado/Real
        k1.metric("Venta Bruta del Día", f"${df_col['Precio'].sum():,.2f}")
        k2.metric("Libras/Unidades en Tramo", int(df_col['Stock'].sum()))
        
        st.markdown("---")
        st.write("📋 **Productos Disponibles en Tramo:**")
        st.dataframe(df_col[["Item", "Grupo", "Especifico", "Stock", "Precio", "Extra"]], use_container_width=True)
        
    with p2:
        st.subheader("Registrar Compra al Mayorista")
        with st.form("form_colmado", clear_on_submit=True):
            f_nom = st.text_input("Nombre del Artículo / Vívere:")
            f_cat = st.selectbox("Rubro Alimentario:", ["Granos", "Bebidas", "Limpieza", "Embutidos", "Enlatados"])
            f_esp = st.text_input("Formato / Unidad (Ej: Saco 100lb, Galón, Caja):")
            f_cos = st.number_input("Costo Distribuidor ($):", min_value=0.0)
            f_pre = st.number_input("Precio Detalle ($):", min_value=0.0)
            f_cant = st.number_input("Volumen / Cantidad:", min_value=1)
            f_ex = st.text_input("Fecha de Vencimiento (AAAA-MM-DD):", value="N/A")
            
            if st.form_submit_button("📥 Registrar Entrada de Almacén") and f_nom.strip():
                nueva_p = pd.DataFrame([{"ID": "C", "Item": f_nom, "Giro": "Colmado / Bodega", "Grupo": f_cat, "Especifico": f_esp, "Costo": f_cos, "Precio": f_pre, "Stock": f_cant, "Extra": f_ex}])
                st.session_state.db_i = pd.concat([st.session_state.db_i, nueva_p], ignore_index=True)
                guardar_cambios(st.session_state.db_i, FICHERO_INV)
                st.success("¡Vívere guardado!"); st.rerun()
                
    with p3:
        st.subheader("Auditoría de Alertas Críticas")
        st.warning("⚠️ **Control de Caducidad de Lotes:**")
        st.write(df_col[["Item", "Especifico", "Stock", "Extra"]])

# =========================================================================
# 📦 DISEÑO INTERFAZ 3: ALMACÉN LOGÍSTICO / DEPOSITOS
# =========================================================================
else:
    st.title("📦 Panel Logístico de Almacenes & Centros de Distribución")
    st.markdown("Indicadores de volumen mayorista, control de bultos, pallets, ubicaciones de racks y auditorías de entrada/salida.")
    
    df_alm = st.session_state.db_i[st.session_state.db_i["Giro"] == "Almacén Mayorista"]
    
    p1, p2 = st.tabs(["🏗️ Ocupación de Espacio y Racks", "📦 Entrada de Cargas Pesadas"])
    
    with p1:
        st.subheader("Distribución Logística de Cajas y Pallets")
        k1, k2 = st.columns(2)
        k1.metric("Valor del Capital Inmovilizado", f"${(df_alm['Costo'] * df_alm['Stock']).sum():,.2f}")
        k2.metric("Cajas Totales en Bahía", int(df_alm['Stock'].sum()))
        
        st.markdown("---")
        st.write("📊 **Volumen Industrial por Código de Almacenamiento:**")
        if not df_alm.empty:
            chart_alm = df_alm.groupby("Item")["Stock"].sum()
            st.bar_chart(chart_alm)
            st.dataframe(df_alm[["Item", "Grupo", "Especifico", "Stock", "Extra"]], use_container_width=True)
            
    with p2:
        st.subheader("Manifiesto de Carga (Ingreso Mayorista)")
        with st.form("form_almacen", clear_on_submit=True):
            f_nom = st.text_input("Descripción de Carga / Ítem SKU:")
            f_cat = st.selectbox("Naturaleza de Carga:", ["Calzado", "Textil", "Electrónica / Celulares", "Herramientas"])
            f_esp = st.text_input("Formato Empaque (Ej: Contenedor, Pallet, Caja Máster):")
            f_cos = st.number_input("Costo Mayorista ($):", min_value=0.0)
            f_pre = st.number_input("Precio Mayorista Esperado ($):", min_value=0.0)
            f_cant = st.number_input("Número de Bultos/Cajas:", min_value=1)
            f_ex = st.text_input("Ubicación en Nave (Ej: Rack Sector A2):", value="Sector General")
            
            if st.form_submit_button("🏗️ Registrar Manifiesto e Indexar Ubicación") and f_nom.strip():
                nueva_p = pd.DataFrame([{"ID": "A", "Item": f_nom, "Giro": "Almacén Mayorista", "Grupo": f_cat, "Especifico": f_esp, "Costo": f_cos, "Precio": f_pre, "Stock": f_cant, "Extra": f_ex}])
                st.session_state.db_i = pd.concat([st.session_state.db_i, nueva_p], ignore_index=True)
                guardar_cambios(st.session_state.db_i, FICHERO_INV)
                st.success("¡Manifiesto logístico procesado!"); st.rerun()
