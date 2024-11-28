import datetime
import random
from typing import Dict, List

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Sistema de Tickets de Soporte",
                   page_icon="🎫", layout="wide")

# Inyectar CSS personalizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
    }

    .mensaje-agente {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }

    .mensaje-usuario {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }

    .ticket-header {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .stButton > button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicialización del estado
if "tickets_df" not in st.session_state:
    # Datos de ejemplo
    problemas_ejemplo = [
        "Error de conexión a la red",
        "Aplicación se cierra inesperadamente",
        "Impresora no responde",
        "Problemas con el correo electrónico",
        "Fallo en respaldo de datos",
        "Problemas de autenticación",
        "Bajo rendimiento del sitio web",
        "Vulnerabilidad de seguridad detectada",
        "Fallo de hardware en servidor",
        "Problemas de acceso a archivos compartidos"
    ]

    # Estructura para mensajes
    class Mensaje:
        def __init__(self, contenido: str, autor: str, timestamp: datetime.datetime, tipo: str):
            self.contenido = contenido
            self.autor = autor
            self.timestamp = timestamp
            self.tipo = tipo  # 'usuario' o 'agente'

    # Inicializar datos
    st.session_state.empresas = {
        "Empresa A": ["Usuario A1", "Usuario A2"],
        "Empresa B": ["Usuario B1", "Usuario B2"],
        "Empresa C": ["Usuario C1"]
    }

    st.session_state.agentes = [
        "Agente 1",
        "Agente 2",
        "Agente 3"
    ]

    # Generar tickets de ejemplo
    tickets_data = []
    for i in range(100):
        empresa = random.choice(list(st.session_state.empresas.keys()))
        usuario = random.choice(st.session_state.empresas[empresa])
        agente = random.choice(st.session_state.agentes)
        fecha = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
        
        # Crear mensajes de ejemplo
        mensajes = []
        num_mensajes = random.randint(1, 4)
        for j in range(num_mensajes):
            if j % 2 == 0:
                mensajes.append(Mensaje(
                    f"Mensaje de usuario {j+1}",
                    usuario,
                    fecha + datetime.timedelta(hours=j),
                    "usuario"
                ))
            else:
                mensajes.append(Mensaje(
                    f"Respuesta del agente {j+1}",
                    agente,
                    fecha + datetime.timedelta(hours=j),
                    "agente"
                ))

        tickets_data.append({
            "id": f"TICKET-{1000 + i}",
            "problema": random.choice(problemas_ejemplo),
            "estado": random.choice(["Abierto", "En Progreso", "Cerrado"]),
            "prioridad": random.choice(["Alta", "Media", "Baja"]),
            "fecha_creacion": fecha,
            "empresa": empresa,
            "usuario": usuario,
            "agente": agente,
            "mensajes": mensajes
        })

    st.session_state.tickets_df = pd.DataFrame(tickets_data)

def dashboard():
    st.header("Dashboard de Tickets")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    tickets_abiertos = len(st.session_state.tickets_df[st.session_state.tickets_df.estado == "Abierto"])
    tiempo_respuesta = 5.2  # Ejemplo
    tiempo_resolucion = 16  # Ejemplo
    
    col1.metric("Tickets Abiertos", tickets_abiertos, "10%")
    col2.metric("Tiempo Primera Respuesta (horas)", tiempo_respuesta, "-1.5")
    col3.metric("Tiempo Promedio Resolución (horas)", tiempo_resolucion, "2")

    # Explicación de métricas
    with st.expander("ℹ️ Explicación de Métricas"):
        st.write("""
        - **Tickets Abiertos**: Número total de tickets que aún no han sido resueltos
        - **Tiempo Primera Respuesta**: Tiempo promedio que toma dar la primera respuesta a un ticket
        - **Tiempo Promedio Resolución**: Tiempo promedio que toma resolver completamente un ticket
        """)

    # Gráficos
    st.subheader("Análisis de Tickets")
    
    # Estado de tickets por mes
    tickets_mes = (
        alt.Chart(st.session_state.tickets_df)
        .mark_bar()
        .encode(
            x=alt.X("monthdate(fecha_creacion):O", title="Mes"),
            y=alt.Y("count():Q", title="Número de Tickets"),
            color=alt.Color("estado:N", title="Estado")
        )
    )
    st.altair_chart(tickets_mes, use_container_width=True)

    # Distribución por prioridad y agente
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Distribución por Prioridad")
        prioridad_chart = (
            alt.Chart(st.session_state.tickets_df)
            .mark_arc()
            .encode(
                theta="count()",
                color="prioridad:N"
            )
        )
        st.altair_chart(prioridad_chart, use_container_width=True)

    with col2:
        st.write("### Tickets por Agente")
        agente_chart = (
            alt.Chart(st.session_state.tickets_df)
            .mark_bar()
            .encode(
                y=alt.Y("agente:N", title="Agente"),
                x=alt.X("count():Q", title="Tickets Asignados")
            )
        )
        st.altair_chart(agente_chart, use_container_width=True)

def nuevo_ticket():
    st.header("Crear Nuevo Ticket")
    
    with st.form("nuevo_ticket"):
        empresa = st.selectbox("Empresa", list(st.session_state.empresas.keys()))
        usuario = st.selectbox("Usuario", st.session_state.empresas[empresa])
        agente = st.selectbox("Asignar Agente", st.session_state.agentes)
        problema = st.text_area("Descripción del Problema")
        prioridad = st.select_slider("Prioridad", ["Baja", "Media", "Alta"])
        
        submitted = st.form_submit_button("Crear Ticket")
        
        if submitted:
            if not problema:
                st.error("Por favor, describe el problema")
                return

            nuevo_ticket = {
                "id": f"TICKET-{len(st.session_state.tickets_df) + 1001}",
                "problema": problema,
                "estado": "Abierto",
                "prioridad": prioridad,
                "fecha_creacion": datetime.datetime.now(),
                "empresa": empresa,
                "usuario": usuario,
                "agente": agente,
                "mensajes": [Mensaje(
                    problema,
                    usuario,
                    datetime.datetime.now(),
                    "usuario"
                )]
            }
            
            st.session_state.tickets_df = pd.concat([
                pd.DataFrame([nuevo_ticket]),
                st.session_state.tickets_df
            ]).reset_index(drop=True)
            
            st.success("Ticket creado exitosamente")

def gestionar_usuarios():
    st.header("Gestión de Usuarios y Empresas")
    
    # Agregar nueva empresa
    with st.expander("Agregar Nueva Empresa"):
        with st.form("nueva_empresa"):
            nombre_empresa = st.text_input("Nombre de la Empresa")
            usuarios = st.text_area("Usuarios (uno por línea)")
            submitted = st.form_submit_button("Agregar Empresa")
            
            if submitted and nombre_empresa:
                if nombre_empresa in st.session_state.empresas:
                    st.error("Esta empresa ya existe")
                    return
                    
                usuarios_lista = [u.strip() for u in usuarios.split("\n") if u.strip()]
                if not usuarios_lista:
                    st.error("Debe agregar al menos un usuario")
                    return
                    
                st.session_state.empresas[nombre_empresa] = usuarios_lista
                st.success(f"Empresa {nombre_empresa} agregada con {len(usuarios_lista)} usuarios")

    # Mostrar y gestionar empresas existentes
    st.subheader("Empresas y Usuarios Actuales")
    for empresa, usuarios in st.session_state.empresas.items():
        with st.expander(f"{empresa} ({len(usuarios)} usuarios)"):
            st.write("Usuarios:")
            for usuario in usuarios:
                col1, col2 = st.columns([3, 1])
                col1.write(f"- {usuario}")
                if col2.button("Eliminar", key=f"del_user_{empresa}_{usuario}"):
                    if len(usuarios) > 1:  # Evitar eliminar el último usuario
                        st.session_state.empresas[empresa].remove(usuario)
                        st.success(f"Usuario {usuario} eliminado de {empresa}")
                        st.experimental_rerun()
                    else:
                        st.error("No se puede eliminar el último usuario de una empresa")
            
            # Agregar usuario a empresa existente
            with st.form(f"agregar_usuario_{empresa}"):
                nuevo_usuario = st.text_input("Nuevo Usuario")
                submitted = st.form_submit_button("Agregar Usuario")
                
                if submitted and nuevo_usuario:
                    if nuevo_usuario in usuarios:
                        st.error("Este usuario ya existe en la empresa")
                    else:
                        st.session_state.empresas[empresa].append(nuevo_usuario)
                        st.success(f"Usuario {nuevo_usuario} agregado a {empresa}")
                        st.experimental_rerun()

def tickets_existentes():
    st.header("Tickets Existentes")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_estado = st.multiselect(
            "Estado",
            ["Abierto", "En Progreso", "Cerrado"],
            default=["Abierto", "En Progreso"]
        )
    with col2:
        filtro_empresa = st.multiselect(
            "Empresa",
            list(st.session_state.empresas.keys())
        )
    with col3:
        filtro_prioridad = st.multiselect(
            "Prioridad",
            ["Alta", "Media", "Baja"]
        )

    # Aplicar filtros
    df_filtrado = st.session_state.tickets_df.copy()
    if filtro_estado:
        df_filtrado = df_filtrado[df_filtrado.estado.isin(filtro_estado)]
    if filtro_empresa:
        df_filtrado = df_filtrado[df_filtrado.empresa.isin(filtro_empresa)]
    if filtro_prioridad:
        df_filtrado = df_filtrado[df_filtrado.prioridad.isin(filtro_prioridad)]

    # Mostrar tickets
    for _, ticket in df_filtrado.iterrows():
        with st.expander(f"#{ticket.id} - {ticket.problema[:50]}..."):
            # Información del ticket
            st.markdown(f"""
            <div class="ticket-header">
                <table width="100%">
                    <tr>
                        <td><strong>Estado:</strong> {ticket.estado}</td>
                        <td><strong>Prioridad:</strong> {ticket.prioridad}</td>
                        <td><strong>Fecha:</strong> {ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</td>
                    </tr>
                    <tr>
                        <td><strong>Empresa:</strong> {ticket.empresa}</td>
                        <td><strong>Usuario:</strong> {ticket.usuario}</td>
                        <td><strong>Agente:</strong> {ticket.agente}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Edición de ticket
            col1, col2, col3 = st.columns(3)
            nuevo_estado = col1.selectbox("Estado", ["Abierto", "En Progreso", "Cerrado"], 
                                        index=["Abierto", "En Progreso", "Cerrado"].index(ticket.estado),
                                        key=f"estado_{ticket.id}")
            nuevo_agente = col2.selectbox("Agente", st.session_state.agentes,
                                        index=st.session_state.agentes.index(ticket.agente),
                                        key=f"agente_{ticket.id}")
            nueva_prioridad = col3.selectbox("Prioridad", ["Alta", "Media", "Baja"],
                                           index=["Alta", "Media", "Baja"].index(ticket.prioridad),
                                           key=f"prioridad_{ticket.id}")
            
            # Actualizar ticket si hay cambios
            if (nuevo_estado != ticket.estado or 
                nuevo_agente != ticket.agente or 
                nueva_prioridad != ticket.prioridad):
                idx = st.session_state.tickets_df[st.session_state.tickets_df.id == ticket.id].index[0]
                st.session_state.tickets_df.at[idx, 'estado'] = nuevo_estado
                st.session_state.tickets_df.at[idx, 'estado'] = nuevo_estado
                st.session_state.tickets_df.at[idx, 'agente'] = nuevo_agente
                st.session_state.tickets_df.at[idx, 'prioridad'] = nueva_prioridad
            
            # Mostrar mensajes
            st.write("---")
            st.write("**Historial de Mensajes:**")
            for msg in ticket.mensajes:
                if msg.tipo == "usuario":
                    st.markdown(f"""
                        <div class="mensaje-usuario">
                            <strong>{msg.autor}</strong> - {msg.timestamp.strftime('%d/%m/%Y %H:%M')}
                            <br>{msg.contenido}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="mensaje-agente">
                            <strong>{msg.autor}</strong> - {msg.timestamp.strftime('%d/%m/%Y %H:%M')}
                            <br>{msg.contenido}
                        </div>
                    """, unsafe_allow_html=True)
            
            # Agregar nuevo mensaje
            with st.form(f"nuevo_mensaje_{ticket.id}"):
                nuevo_mensaje = st.text_area("Nuevo Mensaje")
                col1, col2 = st.columns(2)
                with col1:
                    tipo_mensaje = st.radio("Tipo de Mensaje", ["Agente", "Usuario"], key=f"tipo_msg_{ticket.id}")
                with col2:
                    submitted = st.form_submit_button("Enviar Mensaje")
                
                if submitted and nuevo_mensaje:
                    autor = ticket.agente if tipo_mensaje == "Agente" else ticket.usuario
                    nuevo_msg = Mensaje(
                        nuevo_mensaje,
                        autor,
                        datetime.datetime.now(),
                        tipo_mensaje.lower()
                    )
                    idx = st.session_state.tickets_df[st.session_state.tickets_df.id == ticket.id].index[0]
                    st.session_state.tickets_df.at[idx, 'mensajes'].append(nuevo_msg)
                    st.success("Mensaje agregado")
                    st.experimental_rerun()

def gestionar_agentes():
    st.header("Gestión de Agentes")
    
    # Agregar nuevo agente
    with st.form("nuevo_agente"):
        nombre_agente = st.text_input("Nombre del Agente")
        email_agente = st.text_input("Email del Agente")
        departamento = st.selectbox("Departamento", [
            "Soporte Técnico",
            "Atención al Cliente",
            "Desarrollo",
            "Infraestructura"
        ])
        submitted = st.form_submit_button("Agregar Agente")
        
        if submitted:
            if not nombre_agente or not email_agente:
                st.error("Por favor complete todos los campos")
                return
                
            if nombre_agente in st.session_state.agentes:
                st.error("Este agente ya existe")
                return
                
            st.session_state.agentes.append(nombre_agente)
            st.success(f"Agente {nombre_agente} agregado exitosamente")

    # Mostrar y gestionar agentes existentes
    st.subheader("Agentes Actuales")
    if not st.session_state.agentes:
        st.info("No hay agentes registrados")
    else:
        for agente in st.session_state.agentes:
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 {agente}")
            if len(st.session_state.agentes) > 1:  # Evitar eliminar el último agente
                if col2.button("Eliminar", key=f"del_{agente}"):
                    st.session_state.agentes.remove(agente)
                    # Reasignar tickets del agente eliminado
                    idx = st.session_state.tickets_df[st.session_state.tickets_df.agente == agente].index
                    if len(idx) > 0:
                        nuevo_agente = random.choice([a for a in st.session_state.agentes if a != agente])
                        st.session_state.tickets_df.loc[idx, 'agente'] = nuevo_agente
                    st.success(f"Agente {agente} eliminado y tickets reasignados")
                    st.experimental_rerun()

# Menú lateral
st.sidebar.title("Navegación")
pagina = st.sidebar.radio(
    "Seleccione una página",
    ["Dashboard", "Nuevo Ticket", "Tickets Existentes", "Usuarios", "Agentes"]
)

# Mostrar página seleccionada
if pagina == "Dashboard":
    dashboard()
elif pagina == "Nuevo Ticket":
    nuevo_ticket()
elif pagina == "Tickets Existentes":
    tickets_existentes()
elif pagina == "Usuarios":
    gestionar_usuarios()
elif pagina == "Agentes":
    gestionar_agentes()

# Métricas en el sidebar (siempre visibles)
st.sidebar.markdown("---")
st.sidebar.subheader("Métricas Rápidas")
total_tickets = len(st.session_state.tickets_df)
tickets_abiertos = len(st.session_state.tickets_df[st.session_state.tickets_df.estado == "Abierto"])
tickets_progreso = len(st.session_state.tickets_df[st.session_state.tickets_df.estado == "En Progreso"])

st.sidebar.write(f"Total de Tickets: **{total_tickets}**")
st.sidebar.write(f"Tickets Abiertos: **{tickets_abiertos}**")
st.sidebar.write(f"Tickets en Progreso: **{tickets_progreso}**")

# Información del sistema
st.sidebar.markdown("---")
st.sidebar.info(
    """
    Sistema de Tickets de Soporte
    - Versión 1.0
    - © 2024
    """
)
