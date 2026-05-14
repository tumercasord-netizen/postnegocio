import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 1. CONFIGURACIÓN DE LA PÁGINA WEB NATIVA (CERO INSTALACIONES)
st.set_page_config(page_title="ERP Multi-Negocio Pro", layout="wide", page_icon="🏬")

st.title("🏬 Sistema ERP Operativo Universal")
st.markdown("Gestión en vivo para Tiendas Multirrubro, Almacenes de Cadena, Farmacias y Colmados.")

# --- SISTEMA DE ALMACENAMIENTO LOCAL EN EL SERVIDOR ---
FICHERO_INV = "inventario_universal.csv"
FICHERO_VEN = "ventas_universal.csv"
FICHERO_FIA = "fiados_universal.csv"

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

def cargar_datos(archivo, columnas_defecto):
    if os.path.exists(archivo):
        try:
            return pd.read_csv(archivo)
        except:
            return pd.DataFrame(columns=columnas_defecto)
    else:
        return pd.DataFrame(columns=columnas_defecto)

# Inicializar estados de la base de datos
if 'datos_inv' not in st.session_state:
    df_inicial = cargar_datos(FICHERO_INV, ["Artículo", "Categoría", "SubRubro", "Costo", "Precio", "Stock", "Ubicacion", "Variante", "Vencimiento"])
    if df_inicial.empty:
        # Datos iniciales mezclados para demostrar que acepta de todo en el primer arranque
        df_inicial = pd.DataFrame([
            {"Artículo": "Jeans Slim Fit", "Categoría": "Boutique / Ropa", "SubRubro": "Pantalones", "Costo": 500.0, "Precio": 1200.0, "Stock": 20, "Ubicacion": "Exhibición Tienda", "Variante": "Talla M / Azul", "Vencimiento": "N/A"},
            {"Artículo": "iPhone 13 128GB", "Categoría": "Tecnología / Celulares", "SubRubro": "Smartphones", "Costo": 20000.0, "Precio": 28000.0, "Stock": 5, "Ubicacion": "Almacén Central (Rack B)", "Variante": "Negro / Libre", "Vencimiento": "N/A"},
            {"Artículo": "Tenis Deportivos R1", "Categoría": "Calzado / Zapatos", "SubRubro": "Calzado Hombre", "Costo": 1200.0, "Precio": 2500.0, "Stock": 8, "Ubicacion": "Almacén Pasillo 1", "Variante": "Talla 42 / Negro", "Vencimiento": "N/A"},
            {"Artículo": "Saco de Arroz 125lb", "Categoría": "Colmado / Consumo", "SubRubro": "Granos", "Costo": 2200.0, "Precio": 2800.0, "Stock": 15, "Ubicacion": "Depósito Trasero", "Variante": "Premium", "Vencimiento": "2026-12-31"}
        ])
    st.session_state.datos_inv = df_inicial

if 'datos_ven' not in st.session_state:
    st.session_state.datos_ven = cargar_datos(FICHERO_VEN, ["Fecha", "Artículo", "Variante", "Cantidad", "Costo_Total", "Venta_Total", "Ganancia_Neta", "Método", "Ubicacion_Origen"])

if 'datos_fia' not in st.session_state:
    st.session_state.datos_fia = cargar_datos(FICHERO_FIA, ["Fecha", "Cliente", "Concepto", "Monto", "Estado", "Tipo"])

# 2. SELECTOR ESTRUCTURAL DE PLANTILLA
st.sidebar.header("⚙️ Configuración de Plantilla")
tipo_negocio = st.sidebar.selectbox(
    "Giro Operativo Primario:",
    ["Tienda Departamental (Ropa, Calzado, Celulares)", "Almacén de Distribución / Depósito de Tienda", "Colmado / Minimarket / Bodega", "Farmacia / Cosméticos"]
)

# Mapeo inteligente de términos, sub-rubros y ubicaciones según la naturaleza del negocio
config_giro = {
    "Tienda Departamental (Ropa, Calzado, Celulares)": {
        "prod": "Artículo/Modelo", "var": "Talla/Color/Capacidad", "cat_opciones": ["Boutique / Ropa", "Calzado / Zapatos", "Tecnología / Celulares", "Accesorios"],
        "ubicaciones": ["Exhibición Tienda", "Vitrina Principal", "Almacén de Tienda (Backroom)", "Depósito General"], "ver_vence": False
    },
    "Almacén de Distribución / Depósito de Tienda": {
        "prod": "Mercancía / Ítem / SKU", "var": "Lote / Formato Caja", "cat_opciones": ["Cajas Ropa / Textil", "Pallets Calzado", "Lotes Electrónica", "Mercancía en Tránsito"],
        "ubicaciones": ["Rack Sector A", "Rack Sector B", "Zona de Carga/Descarga", "Bóveda de Seguridad"], "ver_vence": False
    },
    "Colmado / Minimarket / Bodega": {
        "prod": "Producto / Vívere", "var": "Marca / Peso", "cat_opciones": ["Alimentos / Granos", "Bebidas / Nevera", "Limpieza", "Snacks"],
        "ubicaciones": ["Tramo Exhibición", "Nevera / Freezer", "Depósito Trasero / Almacén"], "ver_vence": True
    },
    "Farmacia / Cosméticos": {
        "prod": "Medicamento / Fragancia", "var": "Laboratorio / Miligramos", "cat_opciones": ["Analgésicos", "Antibióticos", "Cuidado Personal", "Perfumería Alta Gama"],
        "ubicaciones": ["Estantería A-Z", "Nevera Médica", "Mostrador", "Almacén de Fármacos"], "ver_vence": True
    }
}[tipo_negocio]

# --- FORMULARIO DE REPOSICIÓN Y ENTRADA DE STOCK UNIVERSAL ---
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Ingresar Nueva Mercancía")
with st.sidebar.form("form_inventario", clear_on_submit=True):
    inv_nombre = st.text_input(f"Nombre del {config_giro['prod']}:")
    inv_cat = st.selectbox("Departamento / Categoría:", config_giro["cat_opciones"])
    inv_sub = st.text_input("Sub-Rubro / Tipo (Ej: Pantalón, Vitrina, Smartphone, Sacos):", value="General")
    inv_var = st.text_input(f"Variante ({config_giro['var']}):", value="Estándar")
    inv_ubicacion = st.selectbox("¿Dónde se va a guardar?", config_giro["ubicaciones"])
    
    col_precios = st.columns(2)
    inv_costo = col_precios[0].number_input("Costo Fábrica ($):", min_value=0.0, step=10.0)
    inv_precio = col_precios[1].number_input("Precio Venta ($):", min_value=0.0, step=10.0)
    
    inv_stock = st.number_input("Cantidad de Unidades / Bultos:", min_value=1, step=1)
    
    inv_vencimiento = "N/A"
    if config_giro["ver_vence"]:
        vence_check = st.checkbox("¿Tiene fecha de vencimiento?")
        if vence_check:
            inv_vencimiento = str(st.date_input("Fecha de Caducidad:", value=datetime.now().date() + timedelta(days=90)))
            
    btn_guardar_inv = st.form_submit_button("📥 Registrar y Almacenar")
    if btn_guardar_inv and inv_nombre.strip():
        nueva_fila = pd.DataFrame([{
            "Artículo": inv_nombre, "Categoría": inv_cat, "SubRubro": inv_sub, "Costo": inv_costo, 
            "Precio": inv_precio, "Stock": inv_stock, "Ubicacion": inv_ubicacion, "Variante": inv_var, "Vencimiento": inv_vencimiento
        }])
        st.session_state.datos_inv = pd.concat([st.session_state.datos_inv, nueva_fila], ignore_index=True)
        guardar_datos(st.session_state.datos_inv, FICHERO_INV)
        st.sidebar.success("¡Registro guardado con éxito!")
        st.rerun()

# 3. PESTAÑAS OPERATIVAS DEL DASHBOARD
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Terminal de Ventas / Despacho", 
    "📓 Cuentas Corrientes (Fiados / Apartados)", 
    "📦 Inventarios y Almacenes de Tienda", 
    "📈 Auditoría de Rentabilidad Neta"
])

# ==========================================
# PESTAÑA 1: TERMINAL DE VENTAS / DESPACHO (Caja)
# ==========================================
with tab1:
    st.subheader(f"🛒 Consola de Facturación y Despacho - {tipo_negocio}")
    df_actual = st.session_state.datos_inv
    
    if not df_actual.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtrar productos disponibles por categorías del giro actual
            df_giro_actual = df_actual[df_actual["Categoría"].isin(config_giro["cat_opciones"])]
            if df_giro_actual.empty:
                st.info("No hay productos registrados para este departamento. Registra mercancía en la barra lateral.")
                st.stop()
                
            prod_sel = st.selectbox(f"Selecciona {config_giro['prod']}:", df_giro_actual["Artículo"].unique())
            var_disponibles = df_giro_actual[df_giro_actual["Artículo"] == prod_sel]
            var_sel = st.selectbox(f"Selecciona {config_giro['var']}:", var_disponibles["Variante"].unique())
            
            # Obtener datos de la variante específica
            datos_producto = var_disponibles[var_disponibles["Variante"] == var_sel].iloc[0]
            
        with col2:
            max_unidades = int(datos_producto["Stock"]) if int(datos_producto["Stock"]) > 0 else 1
            cantidad_vender = st.number_input("Cantidad a retirar/vender:", min_value=1, max_value=max_unidades, value=1)
            metodo_pago = st.selectbox("Condición de Entrega/Pago:", ["Efectivo / Contado", "Tarjeta / Transferencia", "Fiado / Cuenta Abierta", "Apartado de Mercancía"])
            
            cliente_deuda = ""
            if metodo_pago in ["Fiado / Cuenta Abierta", "Apartado de Mercancía"]:
                cliente_deuda = st.text_input("Nombre de la Persona / Cliente responsable:", value="")
                
        with col3:
            st.markdown(f"**Ubicación de Origen:** `{datos_producto['Ubicacion']}`")
            st.markdown(f"**Precio Unitario:** ${datos_producto['Precio']:,.2f}")
            total_facturado = cantidad_vender * datos_producto['Precio']
            st.markdown(f"### Monto Total: ${total_facturado:,.2f}")
            
            if datos_producto["Stock"] <= 0:
                st.error("❌ Sin existencias físicas en esta ubicación.")
            elif datos_producto["Stock"] <= 3:
                st.warning(f"⚠️ Alerta: Quedan solo {datos_producto['Stock']} unidades.")

        if st.button("🔴 Validar Transacción y Actualizar Stock", use_container_width=True):
            if datos_producto["Stock"] <= 0:
                st.error("No se puede despachar mercancía agotada.")
            elif metodo_pago in ["Fiado / Cuenta Abierta", "Apartado de Mercancía"] and not cliente_deuda.strip():
                st.error("❌ Error: Es obligatorio asignar un cliente para deudas o apartados.")
            else:
                # 1. Registrar venta/salida
                v_costo = cantidad_vender * datos_producto["Costo"]
                nueva_v = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "Artículo": prod_sel, "Variante": var_sel,
                    "Cantidad": cantidad_vender, "Costo_Total": v_costo, "Venta_Total": total_facturado,
                    "Ganancia_Neta": total_facturado - v_costo, "Método": metodo_pago, "Ubicacion_Origen": datos_producto["Ubicacion"]
                }])
                st.session_state.datos_ven = pd.concat([st.session_state.datos_ven, nueva_v], ignore_index=True)
                guardar_datos(st.session_state.datos_ven, FICHERO_VEN)
                
                # 2. Descontar stock de la ubicación correspondiente
                for idx, fila in df_actual.iterrows():
                    if fila["Artículo"] == prod_sel and fila["Variante"] == var_sel and fila["Ubicacion"] == datos_producto["Ubicacion"]:
                        st.session_state.datos_inv.at[idx, "Stock"] -= cantidad_vender
                guardar_datos(st.session_state.datos_inv, FICHERO_INV)
                
                # 3. Registrar en cuentas por cobrar si aplica
                if metodo_pago in ["Fiado / Cuenta Abierta", "Apartado de Mercancía"]:
                    nueva_d = pd.DataFrame([{
                        "Fecha": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_deuda,
                        "Concepto": f"{cantidad_vender}x {prod_sel} ({var_sel})", "Monto": total_facturado,
                        "Estado": "Pendiente", "Tipo": metodo_pago
                    }])
                    st.session_state.datos_fia = pd.concat([st.session_state.datos_fia, nueva_d], ignore_index=True)
                    guardar_datos(st.session_state.datos_fia, FICHERO_FIA)
                    
                st.success("✅ Stock descontado e historial actualizado.")
                st.rerun()
    else:
        st.info("Inventario vacío.")

# ==========================================
# PESTAÑA 2: CUENTAS CORRIENTES (Fiados/Apartados)
# ==========================================
with tab2:
    st.subheader("📓 Libro de Deudas y Registro de Apartados de Mercancía")
    df_f = st.session_state.datos_fia
    
    if not df_f.empty:
        monto_calle = df_f[df_f["Estado"] == "Pendiente"]["Monto"].sum()
        st.error(f"⚠️ Capital pendiente de cobro / liquidación: **${monto_calle:,.2f}**")
        st.dataframe(df_f, use_container_width=True)
        
        st.markdown("---")
        st.write("🔧 **Registrar Abonos o Liquidación Completa:**")
        c1, c2 = st.columns(2)
        
        indices_pendientes = df_f[df_f["Estado"] == "Pendiente"].index.tolist()
        if indices_pendientes:
            opcion_cobrar = c1.selectbox("Selecciona la cuenta:", indices_pendientes, format_func=lambda x: f"{df_f.at[x, 'Cliente']} - Monto: ${df_f.at[x, 'Monto']} ({df_f.at[x, 'Concepto']})")
            if c2.button("✔️ Registrar Saldo de Cuenta", use_container_width=True):
                st.session_state.datos_fia.at[opcion_cobrar, "Estado"] = "Saldado"
                guardar_datos(st.session_state.datos_fia, FICHERO_FIA)
                st.success("¡Cuenta actualizada y archivada!")
                st.rerun()
        else:
            st.success("¡Todas las cuentas comerciales están al día!")
    else:
        st.success("No hay registros de créditos o apartados en la base de datos.")

# ==========================================
# PESTAÑA 3: INVENTARIOS Y ALMACENES DE TIENDA
# ==========================================
with tab3:
    st.subheader("📦 Mapa de Ubicaciones, Almacenes y Stock")
    df_i = st.session_state.datos_inv
    
    if not df_i.empty:
        # Filtrar solo el inventario correspondiente al tipo de negocio seleccionado
        df_i_giro = df_i[df_i["Categoría"].isin(config_giro["cat_opciones"])]
        
        col_an1, col_an2 = st.columns([1, 2])
        with col_an1:
            st.info("🏢 **Volumen de Stock por Ubicación:**")
            # Gráfico de barras nativo (Cero dependencias externas)
            grafico_ubicaciones = df_i_giro.groupby("Ubicacion")["Stock"].sum()
            st.bar_chart(grafico_ubicaciones)
            
        with col_an2:
            st.warning("📋 **Auditoría Detallada del Almacén Seleccionado:**")
            st.dataframe(df_i_giro[["Artículo", "SubRubro", "Variante", "Stock", "Ubicacion", "Vencimiento"]], use_container_width=True)
            
            if config_giro["ver_vence"]:
                st.error("📆 **Lotes con Vencimiento Crítico (Menos de 30 días):**")
                df_con_fecha = df_i_giro[df_i_giro["Vencimiento"] != "N/A"].copy()
                df_con_fecha["Vencimiento_DT"] = pd.to_datetime(df_con_fecha["Vencimiento"], errors='coerce').dt.date
                alertas = df_con_fecha[df_con_fecha["Vencimiento_DT"] <= (datetime.now().date() + timedelta(days=30))]
                if not alertas.empty:
                    st.dataframe(alertas[["Artículo", "Variante", "Stock", "Vencimiento"]], use_container_width=True)
                else:
                    st.success("Cero alertas de vencimiento en este departamento.")
    else:
        st.info("Sin registros de existencias.")

# ==========================================
# PESTAÑA 4: AUDITORÍA DE RENTABILIDAD NETA
# ==========================================
with tab4:
    st.subheader("📊 Consola Contable de Márgenes y Caja Neta")
    df_v = st.session_state.datos_ven
    
    if not df_v.empty:
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Venta Bruta Total", f"${df_v['Venta_Total'].sum():,.2f}")
        with k2:
            st.metric("Costo Neto de Reposición", f"${df_v['Costo_Total'].sum():,.2f}", help="Dinero destinado exclusivamente a la recompra de mercancía.")
        with k3:
            ganancia_neta_real = df_v['Ganancia_Neta'].sum()
            ratio = (ganancia_neta_real / df_v['Venta_Total'].sum() * 100) if df_v['Venta_Total'].sum() > 0 else 0
            st.metric("Ganancia Neta Líquida", f"${ganancia_neta_real:,.2f}", delta=f"{ratio:.1f}% Margen de Utilidad")
            
        st.markdown("---")
        st.write("📋 **Historial Clínico de Despachos y Operaciones:**")
        st.dataframe(df_v[["Fecha", "Artículo", "Variante", "Cantidad", "Ubicacion_Origen", "Venta_Total", "Ganancia_Neta", "Método"]], use_container_width=True)
    else:
        st.info("No se registran transacciones en el sistema para este período.")
