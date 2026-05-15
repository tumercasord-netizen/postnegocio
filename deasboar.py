import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. CONFIGURACIÓN DEL SISTEMA OPERATIVO CENTRAL (RESPONSIVO POR DEFECTO)
st.set_page_config(page_title="ERP Todo-En-Uno Pro", layout="wide", page_icon="🏢")

st.title("🏬 Sistema ERP Comercial Todo-En-Uno")
st.markdown("Gestión unificada para Almacén, Boutique, Celulares y Minimarket.")

# --- MOTOR DE BASE DE DATOS LOCAL (Persistencia en el Servidor) ---
FICHERO_INV = "inventario_central.csv"
FICHERO_VEN = "ventas_central.csv"
FICHERO_FIA = "fiados_central.csv"

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

def cargar_datos(archivo, columnas_defecto):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo)
        except: return pd.DataFrame(columns=columnas_defecto)
    return pd.DataFrame(columns=columnas_defecto)

# Inicializar bases de datos locales
if 'db_inv' not in st.session_state:
    df_i = cargar_datos(FICHERO_INV, ["Artículo", "Negocio/Área", "Categoría", "Costo", "Precio", "Stock", "Variante", "Ubicación", "Vencimiento"])
    if df_i.empty:
        # Datos semilla iniciales
        df_i = pd.DataFrame([
            {"Artículo": "Jeans Slim Fit", "Negocio/Área": "Boutique (Ropa/Calzado)", "Categoría": "Pantalones", "Costo": 400.0, "Precio": 1100.0, "Stock": 30, "Variante": "Talla M / Azul", "Ubicación": "Tramo Exhibición", "Vencimiento": "N/A"},
            {"Artículo": "iPhone 13 128GB", "Negocio/Área": "Tecnología & Celulares", "Categoría": "Smartphones", "Costo": 18000.0, "Precio": 25000.0, "Stock": 5, "Variante": "Negro / Libre", "Ubicación": "Vitrina Principal", "Vencimiento": "N/A"},
            {"Artículo": "Saco de Arroz 125lb", "Negocio/Área": "Minimarket & Colmado", "Categoría": "Granos", "Costo": 2200.0, "Precio": 2800.0, "Stock": 15, "Variante": "Premium", "Ubicación": "Almacén de Fondo", "Vencimiento": "2026-12-31"}
        ])
    st.session_state.db_inv = df_i

if 'db_ven' not in st.session_state:
    st.session_state.db_ven = cargar_datos(FICHERO_VEN, ["Fecha", "Artículo", "Negocio/Área", "Cantidad", "Costo_Total", "Venta_Total", "Ganancia_Neta", "Método"])

if 'db_fia' not in st.session_state:
    st.session_state.db_fia = cargar_datos(FICHERO_FIA, ["Fecha", "Cliente", "Concepto", "Monto", "Estado"])

# =========================================================================
# 2. PANEL LATERAL: ENTRADA DE STOCK (Se oculta limpiamente en el celular)
# =========================================================================
st.sidebar.header("⚙️ Entrada de Mercancía")
with st.sidebar.form("form_universal", clear_on_submit=True):
    area_destino = st.selectbox(
        "Área de Destino:",
        ["Boutique (Ropa/Calzado)", "Tecnología & Celulares", "Minimarket & Colmado", "Farmacia & Cosméticos", "Almacén Central / Depósito"]
    )
    
    in_nombre = st.text_input("Nombre del Artículo:")
    in_cat = st.text_input("Categoría (Ej: Jeans, Smartphones, Granos):", value="General")
    in_var = st.text_input("Variante (Ej: Talla L, 128GB, Marca):", value="N/A")
    in_ubica = st.text_input("Ubicación Física:", value="Mostrador")
    
    col_costo, col_precio = st.columns(2)
    in_costo = col_costo.number_input("Costo ($):", min_value=0.0, step=10.0)
    in_precio = col_precio.number_input("Precio ($):", min_value=0.0, step=10.0)
    
    in_stock = st.number_input("Cantidad Entrada:", min_value=1, step=1)
    
    in_vence = "N/A"
    if area_destino in ["Minimarket & Colmado", "Farmacia & Cosméticos"]:
        if st.checkbox("¿Tiene Vencimiento?"):
            in_vence = str(st.date_input("Vencimiento:", value=datetime.now().date() + timedelta(days=120)))
            
    if st.form_submit_button("📥 Guardar Stock", use_container_width=True):
        if in_nombre.strip():
            nueva_fila = pd.DataFrame([{
                "Artículo": in_nombre, "Negocio/Área": area_destino, "Categoría": in_cat,
                "Costo": in_costo, "Precio": in_precio, "Stock": in_stock, "Variante": in_var,
                "Ubicación": in_ubica, "Vencimiento": in_vence
            }])
            st.session_state.db_inv = pd.concat([st.session_state.db_inv, nueva_fila], ignore_index=True)
            guardar_datos(st.session_state.db_inv, FICHERO_INV)
            st.sidebar.success("¡Registrado!")
            st.rerun()

# --- BOTÓN PARA BORRAR BASE DE DATOS (Mantenimiento rápido) ---
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Resetear Datos de Prueba (Limpiar App)", type="secondary", use_container_width=True):
    st.session_state.db_inv = pd.DataFrame(columns=["Artículo", "Negocio/Área", "Categoría", "Costo", "Precio", "Stock", "Variante", "Ubicación", "Vencimiento"])
    st.session_state.db_ven = pd.DataFrame(columns=["Fecha", "Artículo", "Negocio/Área", "Cantidad", "Costo_Total", "Venta_Total", "Ganancia_Neta", "Método"])
    st.session_state.db_fia = pd.DataFrame(columns=["Fecha", "Cliente", "Concepto", "Monto", "Estado"])
    guardar_datos(st.session_state.db_inv, FICHERO_INV)
    guardar_datos(st.session_state.db_ven, FICHERO_VEN)
    guardar_datos(st.session_state.db_fia, FICHERO_FIA)
    st.sidebar.success("¡Base de datos limpia!")
    st.rerun()

# =========================================================================
# 3. PESTAÑAS OPERATIVAS ADAPTATIVAS A CUALQUIER PANTALLA
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Caja (Vender)", 
    "📓 Fiados", 
    "📦 Ver Stock",
    "⏳ Vencimientos",
    "📈 Reporte Diario"
])

# --- TAB 1: CAJA REGISTRADORA RESPONSIVA ---
with tab1:
    st.subheader("🛒 Terminal de Ventas")
    df_i = st.session_state.db_inv
    
    if not df_i.empty:
        col1, col2, col3 = st.columns([1, 1, 1]) # En PC va lado a lado, en Celular se apila solo
        
        with col1:
            area_sel = st.selectbox("Área comercial:", df_i["Negocio/Área"].unique())
            df_filtrado_area = df_i[df_i["Negocio/Área"] == area_sel]
            
            prod_sel = st.selectbox("Artículo:", df_filtrado_area["Artículo"].unique())
            df_vars = df_filtrado_area[df_filtrado_area["Artículo"] == prod_sel]
            var_sel = st.selectbox("Variante/Talla:", df_vars["Variante"].unique())
            
            datos_item = df_vars[df_vars["Variante"] == var_sel].iloc[0]
            
        with col2:
            max_existencias = int(datos_item["Stock"]) if int(datos_item["Stock"]) > 0 else 1
            cant_vender = st.number_input("Cantidad:", min_value=1, max_value=max_existencias, value=1)
            metodo_p = st.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta / Transferencia", "Fiado / Crédito", "Apartado"])
            
            cliente_deuda = ""
            if metodo_p in ["Fiado / Crédito", "Apartado"]:
                cliente_deuda = st.text_input("Nombre del Deudor:")
                
        with col3:
            st.info(f"📍 Ubicación: **{datos_item['Ubicación']}** | Stock Actual: **{datos_item['Stock']}**")
            total_operacion = cant_vender * datos_item['Precio']
            st.success(f"### Total: ${total_operacion:,.2f}")

        if st.button("🔴 CONFIRMAR FACTURA", use_container_width=True):
            if datos_item["Stock"] <= 0:
                st.error("Artículo agotado.")
            elif metodo_p in ["Fiado / Crédito", "Apartado"] and not cliente_deuda.strip():
                st.error("❌ Escribe el nombre del cliente.")
            else:
                # Descontar stock
                for idx, fila in df_i.iterrows():
                    if fila["Artículo"] == prod_sel and fila["Variante"] == var_sel and fila["Negocio/Área"] == area_sel:
                        st.session_state.db_inv.at[idx, "Stock"] -= cant_vender
                guardar_datos(st.session_state.db_inv, FICHERO_INV)
                
                # Registrar Venta
                v_costo = cant_vender * datos_item["Costo"]
                nueva_v = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Artículo": prod_sel, "Negocio/Área": area_sel,
                    "Cantidad": cant_vender, "Costo_Total": v_costo, "Venta_Total": total_operacion,
                    "Ganancia_Neta": total_operacion - v_costo, "Método": metodo_p
                }])
                st.session_state.db_ven = pd.concat([st.session_state.db_ven, nueva_v], ignore_index=True)
                guardar_datos(st.session_state.db_ven, FICHERO_VEN)
                
                # Registrar Fiado
                if metodo_p in ["Fiado / Crédito", "Apartado"]:
                    nueva_d = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_deuda,
                        "Concepto": f"{cant_vender}x {prod_sel} ({var_sel})", "Monto": total_operacion, "Estado": "Pendiente"
                    }])
                    st.session_state.db_fia = pd.concat([st.session_state.db_fia, nueva_d], ignore_index=True)
                    guardar_datos(st.session_state.db_fia, FICHERO_FIA)
                    
                st.success("¡Venta Exitosa!")
                st.rerun()
    else:
        st.info("Inventario vacío.")

# --- TAB 2: FIADOS ---
with tab2:
    st.subheader("📓 Libro de Deudas")
    df_f = st.session_state.db_fia
    if not df_f.empty:
        st.error(f"Dinero en la calle: **${df_f[df_f['Estado']=='Pendiente']['Monto'].sum():,.2f}**")
        st.dataframe(df_f, use_container_width=True)
        
        c1, c2 = st.columns(2)
        pendientes = df_f[df_f["Estado"] == "Pendiente"].index.tolist()
        if pendientes:
            idx_c = c1.selectbox("Cobrar a:", pendientes, format_func=lambda x: f"{df_f.at[x, 'Cliente']} - ${df_f.at[x, 'Monto']}")
            if c2.button("✔️ Registrar Cobro", use_container_width=True):
                st.session_state.db_fia.at[idx_c, "Estado"] = "Saldado"
                guardar_datos(st.session_state.db_fia, FICHERO_FIA)
                st.rerun()
    else:
        st.success("¡Cero deudas!")

# --- TAB 3: STOCK ---
with tab3:
    st.subheader("📦 Conteo de Existencias")
    df_i = st.session_state.db_inv
    if not df_i.empty:
        chart_data = df_i.groupby("Negocio/Área")["Stock"].sum()
        st.bar_chart(chart_data) # Gráfico adaptativo nativo
        st.dataframe(df_i, use_container_width=True)

# --- TAB 4: VENCIMIENTOS ---
with tab4:
    st.subheader("⏳ Alertas de Vencimiento")
    df_i = st.session_state.db_inv
    if not df_i.empty:
        df_vence = df_i[df_i["Vencimiento"] != "N/A"].copy()
        if not df_vence.empty:
            df_vence["Vencimiento_DT"] = pd.to_datetime(df_vence["Vencimiento"], errors='coerce').dt.date
            alertas = df_vence[df_vence["Vencimiento_DT"] <= (datetime.now().date() + timedelta(days=30))]
            if not alertas.empty:
                st.error("🚨 Lotes próximos a vencer (Menos de 30 días):")
                st.dataframe(alertas[["Artículo", "Negocio/Área", "Stock", "Vencimiento"]], use_container_width=True)
            else:
                st.success("Todo en orden con las fechas de caducidad.")

# --- TAB 5: CONTABILIDAD ---
with tab5:
    st.subheader("📈 Cuadre de Caja Central")
    df_v = st.session_state.db_ven
    if not df_v.empty:
        k1, k2, k3 = st.columns(3)
        k1.metric("Venta Bruta", f"${df_v['Venta_Total'].sum():,.2f}")
        k2.metric("Costo de Stock", f"${df_v['Costo_Total'].sum():,.2f}")
        k3.metric("Ganancia Limpia", f"${df_v['Ganancia_Neta'].sum():,.2f}")
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("Sin ventas registradas hoy.")
