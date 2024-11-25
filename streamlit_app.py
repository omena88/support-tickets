import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Tickets de Soporte", page_icon="🎫")
st.title("🎫 Tickets de Soporte")
st.write(
    """
    Esta aplicación muestra cómo puede construir una herramienta interna en Streamlit. 
    Aquí, estamos implementando un flujo de trabajo de tickets de soporte. El usuario puede 
    crear un ticket, editar tickets existentes y ver estadísticas.
    """
)

# Datos de prueba para clientes y usuarios
if "clientes" not in st.session_state:
    st.session_state.clientes = {
        "Empresa A": ["Usuario A1", "Usuario A2", "Usuario A3"],
        "Empresa B": ["Usuario B1", "Usuario B2"],
        "Empresa C": ["Usuario C1", "Usuario C2", "Usuario C3", "Usuario C4"],
    }

# Barra lateral para configuración
with st.sidebar:
    st.header("Configuración")
    
    # Gestión de clientes
    st.subheader("Gestionar Clientes")
    nuevo_cliente = st.text_input("Nuevo Cliente")
    if st.button("Agregar Cliente") and nuevo_cliente:
        if nuevo_cliente not in st.session_state.clientes:
            st.session_state.clientes[nuevo_cliente] = []
            st.success(f"Cliente {nuevo_cliente} agregado")
    
    # Gestión de usuarios
    st.subheader("Gestionar Usuarios")
    cliente_seleccionado = st.selectbox("Seleccionar Cliente", list(st.session_state.clientes.keys()))
    nuevo_usuario = st.text_input("Nuevo Usuario")
    if st.button("Agregar Usuario") and nuevo_usuario:
        if nuevo_usuario not in st.session_state.clientes[cliente_seleccionado]:
            st.session_state.clientes[cliente_seleccionado].append(nuevo_usuario)
            st.success(f"Usuario {nuevo_usuario} agregado a {cliente_seleccionado}")

# Crear DataFrame de ejemplo si no existe
if "df" not in st.session_state:
    # Descripciones de problemas de ejemplo
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
    ]

    # Generar DataFrame con 100 tickets
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Cliente": np.random.choice(list(st.session_state.clientes.keys()), size=100),
        "Usuario": [random.choice(sum(st.session_state.clientes.values(), [])) for _ in range(100)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Abierto", "En Proceso", "Cerrado"], size=100),
        "Priority": np.random.choice(["Alta", "Media", "Baja"], size=100),
        "Fecha": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Respuestas": [[] for _ in range(100)]
    }
    st.session_state.df = pd.DataFrame(data)

# Formulario para nuevo ticket
st.header("Agregar ticket")
with st.form("add_ticket_form"):
    cliente = st.selectbox("Cliente", list(st.session_state.clientes.keys()))
    usuario = st.selectbox("Usuario", st.session_state.clientes[cliente])
    descripcion = st.text_area("Describir el problema")
    prioridad = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
    submitted = st.form_submit_button("Enviar")

if submitted:
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Cliente": cliente,
                "Usuario": usuario,
                "Issue": descripcion,
                "Status": "Abierto",
                "Priority": prioridad,
                "Fecha": today,
                "Respuestas": []
            }
        ]
    )
    st.write("¡Ticket enviado! Detalles del ticket:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Sección de tickets existentes
st.header("Tickets existentes")
st.write(f"Número de tickets: `{len(st.session_state.df)}`")

st.info(
    "Haga clic en un ticket para editarlo o agregar respuestas. "
    "Puede ordenar la tabla haciendo clic en los encabezados de columna.",
    icon="✍️",
)

# Mostrar tabla de tickets
if st.session_state.df is not None:
    # Mostrar tickets en una tabla con columnas configurables
    selected_ticket = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Estado",
                help="Estado del ticket",
                options=["Abierto", "En Proceso", "Cerrado"],
                required=True,
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Prioridad",
                help="Prioridad",
                options=["Alta", "Media", "Baja"],
                required=True,
            ),
        },
        disabled=["ID", "Fecha", "Respuestas"],
    )

# Pop-up para editar ticket
selected_row = st.session_state.df["ID"].isin(selected_ticket["ID"])
if any(selected_row):
    ticket_index = selected_row.idxmax()
    with st.expander(f"Editar Ticket {st.session_state.df.loc[ticket_index, 'ID']}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Detalles del Ticket**")
            st.write(f"Cliente: {st.session_state.df.loc[ticket_index, 'Cliente']}")
            st.write(f"Usuario: {st.session_state.df.loc[ticket_index, 'Usuario']}")
            st.write(f"Estado: {st.session_state.df.loc[ticket_index, 'Status']}")
            st.write(f"Prioridad: {st.session_state.df.loc[ticket_index, 'Priority']}")
            
        with col2:
            st.write("**Agregar Respuesta**")
            nueva_respuesta = st.text_area("Nueva respuesta")
            if st.button("Agregar respuesta"):
                respuesta = {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "texto": nueva_respuesta
                }
                respuestas_actuales = st.session_state.df.loc[ticket_index, "Respuestas"]
                respuestas_actuales.append(respuesta)
                st.session_state.df.at[ticket_index, "Respuestas"] = respuestas_actuales
                st.success("Respuesta agregada")
                
        st.write("**Historial de Respuestas**")
        for respuesta in st.session_state.df.loc[ticket_index, "Respuestas"]:
            st.text(f"{respuesta['fecha']}: {respuesta['texto']}")

# Estadísticas
st.header("Estadísticas")

# Métricas
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Abierto"])
col1.metric(label="Tickets abiertos", value=num_open_tickets, delta=10)
col2.metric(label="Tiempo primera respuesta (horas)", value=5.2, delta=-1.5)
col3.metric(label="Tiempo promedio resolución (horas)", value=16, delta=2)

# Gráficos
st.write("##### Estado de tickets por mes")
status_plot = (
    alt.Chart(selected_ticket)
    .mark_bar()
    .encode(
        x="month(Fecha):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Prioridades de tickets actuales")
priority_plot = (
    alt.Chart(selected_ticket)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
