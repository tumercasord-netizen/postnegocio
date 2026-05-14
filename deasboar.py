import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE LA PÁGINA WEB NATIVA
st.set_page_config(page_title="Sistema Anti-Pérdidas Multinegocio", layout="wide", page_icon="🏪")

st.title("🏪 Sistema de Control Comercial Multi-Plantilla")
st.markdown("Registra tus operaciones diarias en tiempo real para eliminar robos, fiados olvidados y mermas.")

# --- MEMORIA VOLÁTIL DEL SERVIDOR (Base de Datos Viva en Sesión) ---
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = []
if 'db_fiados' not in st.session_state:
    st.session_state.db_fiados = []
if 'db_inventario' not in st.session_state:
    # Datos semilla iniciales
    st.session_state.db_inventario = [
        {"Artículo": "Arroz Premium 1lb", "Categoría": "Alimentos", "Costo": 25.0, "Precio": 35.0, "Stock": 100, "Variante_Talla": "N/A", "Vencimiento": datetime(2026, 8, 15).date()},
        {"Artículo": "Camisa Casual Manga Corta", "Categoría": "Ropa", "Costo": 400.0, "Precio": 850.0, "Stock": 12, "Variante_Talla": "M", "Vencimiento": None},
        {"Artículo": "Camisa Casual Manga Corta", "Categoría": "Ropa", "Costo": 400.0, "Precio": 850.0, "Stock": 2, "Variante_Talla": "XL", "Vencimiento": None},
        {"Artículo": "Amoxicilina 500mg", "Categoría": "Farmacia", "Costo": 150.0, "Precio": 300.0, "Stock": 40, "Variante_Talla": "N/A", "Vencimiento": datetime(2026, 5, 28).date()}
    ]

# 2. SELECTOR DE PLANTILLA DE NEGOCIO
st.sidebar.header("⚙️ Configuración del Comercio")
tipo_negocio = st.sidebar.selectbox(
    "Plantilla del Sistema:",
    ["Colmado / Bodega / Almacén", "Tienda de Ropa / Calzado", "Farmacia / Perfumería", "General / Otro"]
)

# Adecuación visual de etiquetas según el negocio seleccionado
terminos = {
    "Colmado / Bodega / Almacén": {"prod": "Producto/Vívere", "var": "Marca/Detalle", "cat": "Pasillo/Rubro", "mostrar_vencimiento": True},
    "Tienda de Ropa / Calzado": {"prod": "Prenda/Calzado", "var": "Talla/Color", "cat": "Colección/Género", "mostrar_vencimiento": False},
    "Farmacia / Perfumería": {"prod": "Medicamento/Fragancia", "var": "Laboratorio/Presentación", "cat": "Categoría", "mostrar_vencimiento": True},
    "General / Otro": {"prod": "Artículo/Servicio", "var": "Variante/Detalle", "cat": "Categoría", "mostrar_vencimiento": True}
}[tipo_negocio]

# --- MÓDULO DE ABASTECIMIENTO DIRECTO DESDE LA WEB ---
st.sidebar.markdown("---")
st.sidebar.subheader(f"➕ Abastecer {tipo_negocio}")
with st.sidebar.form("form_inventario", clear_on_submit=True):
    inv_nombre = st.text_input(f"Nombre del {terminos['prod']}:")
    inv_cat = st.text_input(f"{terminos['cat']}:")
    inv_var = st.text_input(f"Especificar {terminos['var']}:", value="N/A")
    inv_costo = st.number_input("Costo de Compra ($):", min_value=0.0, step=1.0)
    inv_precio = st.number_input("Precio de Venta ($):", min_value=0.0, step=1.0)
    inv_stock = st.number_input("Cantidad que Entra:", min_value=1, step=1)
    
    inv_vencimiento = None
    if terminos["mostrar_vencimiento"]:
        inv_vencimiento = st.date_input("Fecha de Vencimiento (Si aplica):", value=datetime.now().date() + timedelta(days=180))
        
    btn_guardar_inv = st.form_submit_button("📥 Guardar en Stock")
    if btn_guardar_inv and inv_nombre.strip():
        st.session_state.db_inventario.append({
            "Artículo": inv_nombre, "Categoría": inv_cat, "Costo": inv_costo,
            "Precio": inv_precio, "Stock": inv_stock, "Variante_Talla": inv_var, "Vencimiento": inv_vencimiento
        })
        st.sidebar.success("¡Mercancía añadida!")
        st.rerun()

# 3. PESTAÑAS OPERATIVAS (Módulos de Solución)
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 Caja Registradora (Vender)", 
    "📓 Libro de Fiados y Apartados", 
    "⏳ Alertas de Inventario y Vencimientos", 
    "📈 Dashboard Financiero (Ganancias)"
])

# ==========================================
# PESTAÑA 1: CAJA REGISTRADORA
# ==========================================
with tab1:
    st.subheader("🛒 Registrar Nueva Venta")
    df_inv_actual = pd.DataFrame(st.session_state.db_inventario)
    
    if not df_inv_actual.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            prod_seleccionado = st.selectbox(f"Selecciona el {terminos['prod']}:", df_inv_actual["Artículo"].unique())
            variantes_disp = df_inv_actual[df_inv_actual["Artículo"] == prod_seleccionado]
            variante_sel = st.selectbox(f"Variante ({terminos['var']}):", variantes_disp["Variante_Talla"].unique())
            
            # Filtrar el elemento correspondiente de manera segura
            datos_item = variantes_disp[variantes_disp["Variante_Talla"] == variante_sel].iloc[0]
            
        with col2:
            cantidad_vender = st.number_input("Cantidad a vender:", min_value=1, max_value=int(datos_item["Stock"]), value=1)
            metodo_pago = st.selectbox("Método de Pago:", ["Efectivo", "Tarjeta", "Fiado / Crédito", "Apartado"])
            
            cliente_deuda = "Anónimo"
            if metodo_pago in ["Fiado / Crédito", "Apartado"]:
                cliente_deuda = st.text_input("Nombre de la persona que te debe ($):", value="")
            
        with col3:
            st.markdown(f"**Precio Unitario:** ${datos_item['Precio']:,.2f}")
            total_operacion = cantidad_vender * datos_item['Precio']
            st.markdown(f"### Total a Cobrar: ${total_operacion:,.2f}")
            
            if datos_item["Stock"] <= 3:
                st.warning(f"¡Alerta de Stock Bajo! Solo quedan {datos_item['Stock']} unidades.")

        if st.button("🔴 Confirmar y Procesar Venta", use_container_width=True):
            if metodo_pago in ["Fiado / Crédito", "Apartado"] and not cliente_deuda.strip():
                st.error("❌ No puedes fiar o apartar sin colocar el nombre del cliente.")
            else:
                # 1. Registrar venta
                nueva_venta = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Artículo": prod_seleccionado,
                    "Variante": variante_sel,
                    "Cantidad": cantidad_vender,
                    "Costo_Total": cantidad_vender * datos_item["Costo"],
                    "Venta_Total": total_operacion,
                    "Ganancia_Neta": total_operacion - (cantidad_vender * datos_item["Costo"]),
                    "Método": metodo_pago
                }
                st.session_state.db_ventas.append(nueva_venta)
                
                # 2. Restar del inventario real
                for idx, item in enumerate(st.session_state.db_inventario):
                    if item["Artículo"] == prod_seleccionado and item["Variante_Talla"] == variante_sel:
                        st.session_state.db_inventario[idx]["Stock"] -= cantidad_vender
                
                # 3. Registrar cuenta por cobrar
                if metodo_pago in ["Fiado / Crédito", "Apartado"]:
                    st.session_state.db_fiados.append({
                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                        "Cliente": cliente_deuda,
                        "Concepto": f"{cantidad_vender}x {prod_seleccionado} ({variante_sel})",
                        "Monto": total_operacion,
                        "Estado": "Pendiente",
                        "Tipo": metodo_pago
                    })
                
                st.success("✅ Operación procesada de forma nativa.")
                st.rerun()
    else:
        st.info("No hay mercancía registrada. Agrégala en el panel izquierdo.")

# ==========================================
# PESTAÑA 2: LIBRO DE FIADOS Y APARTADOS
# ==========================================
with tab2:
    st.subheader("📓 Control de Cuentas por Cobrar y Apartados")
    if st.session_state.db_fiados:
        df_fiados = pd.DataFrame(st.session_state.db_fiados)
        monto_calle = df_fiados[df_fiados["Estado"] == "Pendiente"]["Monto"].sum()
        st.error(f"⚠️ Dinero total en riesgo en la calle: **${monto_calle:,.2f}**")
        st.dataframe(df_fiados, use_container_width=True)
        
        st.markdown("---")
        st.write("🔧 **Registrar Cobros:**")
        c1, c2 = st.columns(2)
        
        filtro_pendientes = [i for i, f in enumerate(st.session_state.db_fiados) if f["Estado"] == "Pendiente"]
        if filtro_pendientes:
            idx_cobrar = c1.selectbox("Deuda a liquidar:", filtro_pendientes, format_func=lambda x: f"{st.session_state.db_fiados[x]['Cliente']} - ${st.session_state.db_fiados[x]['Monto']} [{st.session_state.db_fiados[x]['Tipo']}]")
            if c2.button("Saldar Deuda Completamente", use_container_width=True):
                st.session_state.db_fiados[idx_cobrar]["Estado"] = "Saldado"
                st.success("¡Cobro guardado!")
                st.rerun()
        else:
            st.success("¡Cuentas al día!")
    else:
        st.success("🎉 ¡Nadie debe dinero en este turno!")

# ==========================================
# PESTAÑA 3: ALERTAS DE INVENTARIO Y VENCIMIENTOS
# ==========================================
with tab3:
    st.subheader("⏳ Módulo Antimerma de Productos y Tallas")
    df_inv = pd.DataFrame(st.session_state.db_inventario)
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.warning("📉 **Control de Stock Muerto (Sin movimiento):**")
        
        # GRÁFICO NATIVO DE STREAMLIT (No requiere instalar nada)
        df_chart = df_inv.groupby("Artículo")["Stock"].sum()
        st.bar_chart(df_chart)
        
    with col_inv2:
        st.error("📆 **Alertas de Vencimiento de Lotes:**")
        if terminos["mostrar_vencimiento"]:
            hoy = datetime.now().date()
            limite_alerta = hoy + timedelta(days=30)
            df_vencimiento = df_inv[df_inv["Vencimiento"].notnull()]
            df_criticos = df_vencimiento[df_vencimiento["Vencimiento"] <= limite_alerta]
            
            if not df_criticos.empty:
                st.write("❌ **Mercancía próxima a expirar (Menos de 30 días):**")
                for _, fila in df_criticos.iterrows():
                    st.write(f"⚠️ **{fila['Artículo']}** ({fila['Variante_Talla']}) - Stock: {fila['Stock']} unds - Vence: {fila['Vencimiento']}")
            else:
                st.success("No hay mermas por vencimiento este mes.")
        else:
            st.info("Este giro de negocio no deprecia por caducidad química.")

# ==========================================
# PESTAÑA 4: DASHBOARD FINANCIERO
# ==========================================
with tab4:
    st.subheader("📊 Análisis Neto de Ganancias")
    if st.session_state.db_ventas:
        df_ventas = pd.DataFrame(st.session_state.db_ventas)
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Venta Total en Caja", f"${df_ventas['Venta_Total'].sum():,.2f}")
        with kpi2:
            st.metric("Inversión de Proveedores", f"${df_ventas['Costo_Total'].sum():,.2f}")
        with kpi3:
            margen_p = (df_ventas['Ganancia_Neta'].sum() / df_ventas['Venta_Total'].sum()) * 100
            st.metric("Ganancia Real Líquida", f"${df_ventas['Ganancia_Neta'].sum():,.2f}", delta=f"{margen_p:.1f}% Margen")
            
        st.markdown("---")
        st.write("📋 **Historial de Operaciones del Turno Actual:**")
        st.dataframe(df_ventas[["Fecha", "Artículo", "Variante", "Cantidad", "Venta_Total", "Ganancia_Neta", "Método"]], use_container_width=True)
    else:
        st.info("Sin ventas registradas en este turno.")
