import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_modal import Modal  # Necesitarás instalar streamlit-modal: pip install streamlit-modal

# Configuración de la página
st.set_page_config(page_title="Tickets de Soporte", page_icon="🎫")
st.title("🎫 Tickets de Soporte")
st.write(
    """
    Esta aplicación muestra cómo puedes construir una herramienta interna en Streamlit. Aquí, estamos 
    implementando un flujo de trabajo de tickets de soporte. El usuario puede crear un ticket, editar 
    tickets existentes y ver algunas estadísticas.
    """
)

# Inicialización de los tickets
if "df" not in st.session_state:
    # Establecer semilla para reproducibilidad
    np.random.seed(42)

    # Descripciones de problemas ficticios
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]

    # Datos de prueba para clientes y usuarios
    clientes = {
        "Cliente A": ["Usuario A1", "Usuario A2"],
        "Cliente B": ["Usuario B1", "Usuario B2", "Usuario B3"],
        "Cliente C": ["Usuario C1"],
    }

    # Generar el dataframe con 100 filas/tickets.
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Cliente": np.random.choice(list(clientes.keys()), size=100),
        "Usuario": [
            random.choice(clientes[cliente]) for cliente in np.random.choice(list(clientes.keys()), size=100)
        ],
        "Respuesta": [""] * 100  # Columna para respuestas
    }
    df = pd.DataFrame(data)

    # Guardar el dataframe en session_state
    st.session_state.df = df

# Inicialización de clientes y usuarios en session_state
if "clientes" not in st.session_state:
    st.session_state.clientes = {
        "Cliente A": ["Usuario A1", "Usuario A2"],
        "Cliente B": ["Usuario B1", "Usuario B2", "Usuario B3"],
        "Cliente C": ["Usuario C1"],
    }

# Función para actualizar clientes y usuarios
def actualizar_clientes(nuevos_clientes):
    st.session_state.clientes = nuevos_clientes

# Barra lateral para configurar clientes y usuarios
st.sidebar.header("Configuración de Clientes y Usuarios")
with st.sidebar.expander("Gestionar Clientes y Usuarios"):
    # Mostrar clientes existentes
    clientes = st.session_state.clientes.copy()
    for cliente, usuarios in clientes.items():
        st.subheader(cliente)
        nuevos_usuarios = st.text_input(f"Agregar usuario a {cliente}", key=f"add_{cliente}")
        if st.button(f"Agregar a {cliente}", key=f"btn_{cliente}"):
            if nuevos_usuarios:
                st.session_state.clientes[cliente].append(nuevos_usuarios)
                st.success(f"Usuario '{nuevos_usuarios}' agregado a {cliente}")
    # Agregar nuevo cliente
    nuevo_cliente = st.text_input("Nombre del nuevo cliente", key="nuevo_cliente")
    nuevo_usuario = st.text_input("Usuario del nuevo cliente", key="nuevo_usuario")
    if st.button("Agregar Cliente", key="btn_nuevo_cliente"):
        if nuevo_cliente and nuevo_usuario:
            if nuevo_cliente in st.session_state.clientes:
                st.warning("El cliente ya existe.")
            else:
                st.session_state.clientes[nuevo_cliente] = [nuevo_usuario]
                st.success(f"Cliente '{nuevo_cliente}' con usuario '{nuevo_usuario}' agregado.")
        else:
            st.warning("Por favor, ingresa el nombre del cliente y el usuario.")

# Función para abrir el modal de edición
def abrir_modal_edicion(ticket_id):
    st.session_state.modal_open = True
    st.session_state.ticket_editar = ticket_id

# Inicializar modal
if "modal_open" not in st.session_state:
    st.session_state.modal_open = False
if "ticket_editar" not in st.session_state:
    st.session_state.ticket_editar = None

# Crear un modal para editar tickets
modal = Modal(key="edit_modal")

with modal.container():
    if st.session_state.modal_open and st.session_state.ticket_editar:
        ticket = st.session_state.df[st.session_state.df.ID == st.session_state.ticket_editar].iloc[0]
        st.header(f"Editar Ticket: {ticket['ID']}")
        with st.form("editar_ticket_form"):
            issue = st.text_area("Describir el problema", value=ticket["Issue"])
            status = st.selectbox("Estado", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(ticket["Status"]))
            priority = st.selectbox("Prioridad", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(ticket["Priority"]))
            cliente = st.selectbox("Cliente", list(st.session_state.clientes.keys()), index=list(st.session_state.clientes.keys()).index(ticket["Cliente"]))
            usuario = st.selectbox("Usuario", st.session_state.clientes[cliente], index=st.session_state.clientes[cliente].index(ticket["Usuario"]))
            respuesta = st.text_area("Respuesta", value=ticket["Respuesta"])
            submit_edicion = st.form_submit_button("Guardar Cambios")
            cancelar_edicion = st.form_submit_button("Cancelar")
        
        if submit_edicion:
            # Actualizar el ticket en el dataframe
            idx = st.session_state.df[st.session_state.df.ID == ticket["ID"]].index[0]
            st.session_state.df.at[idx, "Issue"] = issue
            st.session_state.df.at[idx, "Status"] = status
            st.session_state.df.at[idx, "Priority"] = priority
            st.session_state.df.at[idx, "Cliente"] = cliente
            st.session_state.df.at[idx, "Usuario"] = usuario
            st.session_state.df.at[idx, "Respuesta"] = respuesta
            st.success("Ticket actualizado correctamente.")
            st.session_state.modal_open = False
            st.session_state.ticket_editar = None
            modal.close()
        
        if cancelar_edicion:
            st.session_state.modal_open = False
            st.session_state.ticket_editar = None
            modal.close()

# Sección para añadir un nuevo ticket
st.header("Agregar un ticket")

with st.form("add_ticket_form"):
    issue = st.text_area("Describir el problema")
    cliente = st.selectbox("Cliente", list(st.session_state.clientes.keys()))
    usuario = st.selectbox("Usuario", st.session_state.clientes[cliente])
    priority = st.selectbox("Prioridad", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Enviar")

if submitted:
    # Crear un nuevo ticket y agregarlo al dataframe
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
                "Cliente": cliente,
                "Usuario": usuario,
                "Respuesta": "",
            }
        ]
    )

    # Mostrar mensaje de éxito y actualizar session_state.df
    st.success("¡Ticket enviado! Aquí están los detalles del ticket:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Sección para ver y editar tickets existentes
st.header("Tickets existentes")
st.write(f"Número de tickets: `{len(st.session_state.df)}`")

st.info(
    "Puedes editar los tickets haciendo clic en el botón de editar. Las estadísticas se actualizan automáticamente. También puedes ordenar la tabla haciendo clic en los encabezados de las columnas.",
    icon="✍️",
)

# Función para manejar la selección de filas
def seleccionar_ticket(row):
    abrir_modal_edicion(row["ID"])

# Mostrar la tabla de tickets con un botón de editar
def mostrar_tabla_tickets(df):
    df_display = df.copy()
    df_display["Acciones"] = df_display.apply(lambda row: f"<button onclick='streamlitSelectTicket(\"{row['ID']}\")'>Editar</button>", axis=1)
    return df_display

# Usar st.experimental_data_editor con selección de fila
edited_df = st.experimental_data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Estado",
            help="Estado del ticket",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Prioridad",
            help="Prioridad del ticket",
            options=["High", "Medium", "Low"],
            required=True,
        ),
        "Cliente": st.column_config.SelectboxColumn(
            "Cliente",
            help="Cliente asociado al ticket",
            options=list(st.session_state.clientes.keys()),
            required=True,
        ),
        "Usuario": st.column_config.SelectboxColumn(
            "Usuario",
            help="Usuario del cliente",
            options=lambda row: st.session_state.clientes[row["Cliente"]],
            required=True,
        ),
        "Respuesta": st.column_config.TextAreaColumn(
            "Respuesta",
            help="Respuesta al ticket",
            required=False,
        ),
    },
    # Deshabilitar edición de ciertas columnas
    disabled=["ID", "Date Submitted"],
)

# Actualizar el dataframe con los cambios editados
st.session_state.df = edited_df

# Sección de estadísticas
st.header("Estadísticas")

# Mostrar métricas lado a lado
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
num_in_progress = len(st.session_state.df[st.session_state.df.Status == "In Progress"])
num_closed = len(st.session_state.df[st.session_state.df.Status == "Closed"])
col1.metric(label="Tickets Abiertos", value=num_open_tickets, delta=10)
col2.metric(label="Tiempo de primera respuesta (horas)", value=5.2, delta=-1.5)
col3.metric(label="Tiempo promedio de resolución (horas)", value=16, delta=2)

# Gráficos con Altair
st.write("")
st.write("##### Estado de los tickets por mes")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x=alt.X("month(Date Submitted):O", title="Mes"),
        y=alt.Y("count():Q", title="Número de Tickets"),
        color=alt.Color("Status:N", title="Estado"),
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Prioridades actuales de los tickets")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta=alt.Theta(field="count()", type="quantitative"),
            color=alt.Color("Priority:N", title="Prioridad"))
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")

# JavaScript para manejar la selección de tickets y abrir el modal
st.markdown("""
    <script>
    function streamlitSelectTicket(ticket_id) {
        const event = new CustomEvent("select_ticket", { detail: ticket_id });
        window.dispatchEvent(event);
    }
    </script>
""", unsafe_allow_html=True)

# Manejar el evento de selección de ticket
def handle_ticket_selection():
    ticket_id = st.experimental_get_query_params().get("ticket_id", [None])[0]
    if ticket_id:
        abrir_modal_edicion(ticket_id)

handle_ticket_selection()
