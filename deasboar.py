import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. CONFIGURACIÓN DEL SISTEMA OPERATIVO CENTRAL
st.set_page_config(page_title="ERP Multi-Negocio Todo-En-Uno", layout="wide", page_icon="🏢")

st.title("🏬 Sistema ERP Comercial Todo-En-Uno")
st.markdown("Plataforma unificada: Controla Almacén, Boutique de Ropa, Celulares y Minimarket desde un solo lugar.")

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

# Inicializar las tablas del sistema
if 'db_inv' not in st.session_state:
    df_i = cargar_datos(FICHERO_INV, ["Artículo", "Negocio/Área", "Categoría", "Costo", "Precio", "Stock", "Variante", "Ubicación", "Vencimiento"])
    if df_i.empty:
        # Datos semilla para demostrar que conviven todos los negocios juntos
        df_i = pd.DataFrame([
            {"Artículo": "Jeans Slim Fit", "Negocio/Área": "Boutique (Ropa/Calzado)", "Categoría": "Pantalones", "Costo": 400.0, "Precio": 1100.0, "Stock": 30, "Variante": "Talla M / Azul", "Ubicación": "Tramo Exhibición", "Vencimiento": "N/A"},
            {"Artículo": "iPhone 13 128GB", "Negocio/Área": "Tecnología & Celulares", "Categoría": "Smartphones", "Costo": 18000.0, "Precio": 25000.0, "Stock": 5, "Variante": "Negro / Libre", "Ubicación": "Vitrina Principal", "Vencimiento": "N/A"},
            {"Artículo": "Saco de Arroz 125lb", "Negocio/Área": "Minimarket & Colmado", "Categoría": "Granos", "Costo": 2200.0, "Precio": 2800.0, "Stock": 15, "Variante": "Premium", "Ubicación": "Almacén de Fondo", "Vencimiento": "2026-12-31"},
            {"Artículo": "Amoxicilina 500mg", "Negocio/Área": "Farmacia & Cosméticos", "Categoría": "Antibióticos", "Costo": 100.0, "Precio": 250.0, "Stock": 50, "Variante": "Caja x30", "Ubicación": "Estante A", "Vencimiento": "2026-08-20"}
        ])
    st.session_state.db_inv = df_i

if 'db_ven' not in st.session_state:
    st.session_state.db_ven = cargar_datos(FICHERO_VEN, ["Fecha", "Artículo", "Negocio/Área", "Cantidad", "Costo_Total", "Venta_Total", "Ganancia_Neta", "Método"])

if 'db_fia' not in st.session_state:
    st.session_state.db_fia = cargar_datos(FICHERO_FIA, ["Fecha", "Cliente", "Concepto", "Monto", "Estado"])

# =========================================================================
# 2. PANEL LATERAL: CONTROL DE ENTRADA DE MERCANCÍA PARA CUALQUIER RUBRO
# =========================================================================
st.sidebar.header("⚙️ Entrada de Mercancía Universal")
st.sidebar.write("Agrega inventario a cualquier sección del negocio:")

with st.sidebar.form("form_universal", clear_on_submit=True):
    area_destino = st.selectbox(
        "¿A qué área va este producto?",
        ["Boutique (Ropa/Calzado)", "Tecnología & Celulares", "Minimarket & Colmado", "Farmacia & Cosméticos", "Almacén Central / Depósito"]
    )
    
    # Textos de ayuda dinámicos según el área seleccionada
    ayuda = {
        "Boutique (Ropa/Calzado)": {"cat": "Blusas, Zapatos, Jeans", "var": "Talla M / Color Azul"},
        "Tecnología & Celulares": {"cat": "Smartphones, Cargadores", "var": "128GB / Color Negro"},
        "Minimarket & Colmado": {"cat": "Granos, Bebidas, Enlatados", "var": "Saco 125lb, Litro"},
        "Farmacia & Cosméticos": {"cat": "Analgésicos, Cremas", "var": "500mg, Frasco 100ml"},
        "Almacén Central / Depósito": {"cat": "Cajas Máster, Pallets", "var": "Lote Completo"}
    }[area_destino]
    
    in_nombre = st.text_input("Nombre del Artículo:")
    in_cat = st.text_input(f"Categoría ({ayuda['cat']}):", value="General")
    in_var = st.text_input(f"Variante/Detalle ({ayuda['var']}):", value="N/A")
    in_ubica = st.text_input("Ubicación Física (Ej: Estante B, Vitrina, Rack 3):", value="Mostrador")
    
    col_p = st.columns(2)
    in_costo = col_p.number_input("Costo Fábrica ($):", min_value=0.0, step=10.0)
    in_precio = col_p.number_input("Precio Venta ($):", min_value=0.0, step=10.0)
    
    in_stock = st.number_input("Cantidad que ingresa:", min_value=1, step=1)
    
    # Campo de vencimiento inteligente (solo si es comida o medicina)
    in_vence = "N/A"
    if area_destino in ["Minimarket & Colmado", "Farmacia & Cosméticos"]:
        if st.checkbox("¿Tiene fecha de vencimiento?"):
            in_vence = str(st.date_input("Vencimiento:", value=datetime.now().date() + timedelta(days=120)))
            
    if st.form_submit_button("📥 Registrar en Inventario Global"):
        if in_nombre.strip():
            nueva_fila = pd.DataFrame([{
                "Artículo": in_nombre, "Negocio/Área": area_destino, "Categoría": in_cat,
                "Costo": in_costo, "Precio": in_precio, "Stock": in_stock, "Variante": in_var,
                "Ubicación": in_ubica, "Vencimiento": in_vence
            }])
            st.session_state.db_inv = pd.concat([st.session_state.db_inv, nueva_fila], ignore_index=True)
            guardar_datos(st.session_state.db_inv, FICHERO_INV)
            st.sidebar.success("¡Guardado en el sistema unificado!")
            st.rerun()

# =========================================================================
# 3. PESTAÑAS OPERATIVAS DEL ECOSISTEMA "TODO EN UNO"
# =========================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 Terminal de Ventas (Caja)", 
    "📓 Cuentas por Cobrar (Fiados)", 
    "📦 Stock por Negocio",
    "⏳ Alertas de Mermas",
    "📈 Contabilidad General"
])

# --- PESTAÑA 1: CAJA REGISTRADORA UNIFICADA ---
with tab1:
    st.subheader("🛒 Punto de Venta Universal (Factura cualquier artículo)")
    df_i = st.session_state.db_inv
    
    if not df_i.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            area_sel = st.selectbox("¿De qué área es la venta?", df_i["Negocio/Área"].unique())
            df_filtrado_area = df_i[df_i["Negocio/Área"] == area_sel]
            
            prod_sel = st.selectbox("Selecciona el Artículo:", df_filtrado_area["Artículo"].unique())
            df_vars = df_filtrado_area[df_filtrado_area["Artículo"] == prod_sel]
            var_sel = st.selectbox("Selecciona la Variante/Talla:", df_vars["Variante"].unique())
            
            datos_item = df_vars[df_vars["Variante"] == var_sel].iloc
            
        with col2:
            max_existencias = int(datos_item["Stock"]) if int(datos_item["Stock"]) > 0 else 1
            cant_vender = st.number_input("Cantidad a vender:", min_value=1, max_value=max_existencias, value=1)
            metodo_p = st.selectbox("Método de Pago:", ["Efectivo", "Tarjeta / Transferencia", "Fiado / Crédito", "Apartado"])
            
            cliente_deuda = ""
            if metodo_p in ["Fiado / Crédito", "Apartado"]:
                cliente_deuda = st.text_input("Nombre del Cliente (Deudor):")
                
        with col3:
            st.markdown(f"**Ubicación en Tienda:** `{datos_item['Ubicación']}`")
            st.markdown(f"**Precio Unitario:** ${datos_item['Precio']:,.2f}")
            total_operacion = cant_vender * datos_item['Precio']
            st.markdown(f"### Total a Cobrar: ${total_operacion:,.2f}")
            
            if datos_item["Stock"] <= 0:
                st.error("❌ No hay existencias en inventario.")
            elif datos_item["Stock"] <= 3:
                st.warning(f"⚠️ Stock Bajo: Solo quedan {datos_item['Stock']} unidades.")

        if st.button("🔴 Confirmar y Procesar Venta", use_container_width=True):
            if datos_item["Stock"] <= 0:
                st.error("Operación abortada: Artículo sin stock.")
            elif metodo_p in ["Fiado / Crédito", "Apartado"] and not cliente_deuda.strip():
                st.error("❌ Error: Coloca el nombre del cliente para registrar el fiado o apartado.")
            else:
                # 1. Descontar del inventario central
                for idx, fila in df_i.iterrows():
                    if fila["Artículo"] == prod_sel and fila["Variante"] == var_sel and fila["Negocio/Área"] == area_sel:
                        st.session_state.db_inv.at[idx, "Stock"] -= cant_vender
                guardar_datos(st.session_state.db_inv, FICHERO_INV)
                
                # 2. Guardar reporte de venta
                v_costo = cant_vender * datos_item["Costo"]
                nueva_v = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Artículo": prod_sel, "Negocio/Área": area_sel,
                    "Cantidad": cant_vender, "Costo_Total": v_costo, "Venta_Total": total_operacion,
                    "Ganancia_Neta": total_operacion - v_costo, "Método": metodo_p
                }])
                st.session_state.db_ven = pd.concat([st.session_state.db_ven, nueva_v], ignore_index=True)
                guardar_datos(st.session_state.db_ven, FICHERO_VEN)
                
                # 3. Mandar al libro de fiados si aplica
                if metodo_p in ["Fiado / Crédito", "Apartado"]:
                    nueva_d = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_deuda,
                        "Concepto": f"{cant_vender}x {prod_sel} ({var_sel}) - [{area_sel}]",
                        "Monto": total_operacion, "Estado": "Pendiente"
                    }])
                    st.session_state.db_fia = pd.concat([st.session_state.db_fia, nueva_d], ignore_index=True)
                    guardar_datos(st.session_state.db_fia, FICHERO_FIA)
                    
                st.success("✅ Venta procesada en el sistema central.")
                st.rerun()
    else:
        st.info("El inventario global está vacío.")

# --- PESTAÑA 2: CUENTAS POR COBRAR CENTRALIZADAS ---
with tab2:
    st.subheader("📓 Libro Mayor de Fiados y Apartados (Todos los negocios)")
    df_f = st.session_state.db_fia
    if not df_f.empty:
        st.error(f"⚠️ Dinero total en la calle: **${df_f[df_f['Estado']=='Pendiente']['Monto'].sum():,.2f}**")
        st.dataframe(df_f, use_container_width=True)
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        pendientes = df_f[df_f["Estado"] == "Pendiente"].index.tolist()
        if pendientes:
            idx_c = c1.selectbox("Selecciona la cuenta a cobrar:", pendientes, format_func=lambda x: f"{df_f.at[x, 'Cliente']} - ${df_f.at[x, 'Monto']} ({df_f.at[x, 'Concepto']})")
            if c2.button("✔️ Registrar Cobro / Liquidación", use_container_width=True):
                st.session_state.db_fia.at[idx_c, "Estado"] = "Saldado"
                guardar_datos(st.session_state.db_fia, FICHERO_FIA)
                st.success("¡Cuenta cobrada!"); st.rerun()
        else:
            st.success("🎉 ¡Todas las cuentas están cobradas!")
    else:
        st.success("No hay deudas registradas.")

# --- PESTAÑA 3: INVENTARIO POR NEGOCIO ---
with tab3:
    st.subheader("📦 Distribución Física del Inventario Global")
    df_i = st.session_state.db_inv
    if not df_i.empty:
        # Gráfico nativo para ver qué negocio tiene más stock
        chart_data = df_i.groupby("Negocio/Área")["Stock"].sum()
        st.bar_chart(chart_data)
        
        # Filtro de visualización
        filtro_area = st.selectbox("Filtrar tabla por área comercial:", ["Mostrar Todo"] + list(df_i["Negocio/Área"].unique()))
        if filtro_area == "Mostrar Todo":
            st.dataframe(df_i, use_container_width=True)
        else:
            st.dataframe(df_i[df_i["Negocio/Área"] == filtro_area], use_container_width=True)

# --- PESTAÑA 4: ALERTAS DE MERMAS (COMIDA Y MEDICINA) ---
with tab4:
    st.subheader("⏳ Control de Mermas por Caducidad (Minimarket y Farmacia)")
    df_i = st.session_state.db_inv
    if not df_i.empty:
        df_vence = df_i[df_i["Vencimiento"] != "N/A"].copy()
        if not df_vence.empty:
            df_vence["Vencimiento_DT"] = pd.to_datetime(df_vence["Vencimiento"], errors='coerce').dt.date
            limite = datetime.now().date() + timedelta(days=30)
            
            alertas = df_vence[df_vence["Vencimiento_DT"] <= limite]
            if not alertas.empty:
                st.error("❌ **¡Atención! Estos lotes vencen en menos de 30 días. Sácalos a liquidación:**")
                st.dataframe(alertas[["Artículo", "Negocio/Área", "Stock", "Vencimiento", "Ubicación"]], use_container_width=True)
            else:
                st.success("🎉 Cero pérdidas por caducidad en los próximos 30 días.")
        else:
            st.info("No hay productos con fecha de vencimiento configurados.")

# --- PESTAÑA 5: CONTABILIDAD GENERAL GENERALIZADA ---
with tab5:
    st.subheader("📊 Libro de Contabilidad y Márgenes de Todo el Grupo")
    df_v = st.session_state.db_ven
    if not df_v.empty:
        k1, k2, k3 = st.columns(3)
        k1.metric("Venta Bruta Combinada", f"${df_v['Venta_Total'].sum():,.2f}")
        k2.metric("Costo Inversión de Reposición", f"${df_v['Costo_Total'].sum():,.2f}")
        
        ganancia_combinada = df_v['Ganancia_Neta'].sum()
        ratio = (ganancia_combinada / df_v['Venta_Total'].sum() * 100) if df_v['Venta_Total'].sum() > 0 else 0
        k3.metric("Ganancia Neta Líquida Total", f"${ganancia_combinada:,.2f}", delta=f"{ratio:.1f}% Margen Global")
        
        st.markdown("---")
        st.write("📋 **Historial de Operaciones de Todo el Consorcio:**")
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("No se registran transacciones el día de hoy.")
