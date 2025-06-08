import streamlit as st
import sqlite3
import pandas as pd
import datetime
from io import BytesIO

# Función para obtener la conexión a la base de datos SQLite
def get_connection():
    conn = sqlite3.connect('datos_consignacion.db', check_same_thread=False)
    return conn

# Función para crear las tablas si no existen
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links_contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_general TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            marca TEXT,
            descripcion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_auto TEXT,
            telefono TEXT UNIQUE,
            nombre TEXT,
            auto TEXT,
            precio REAL,
            id_link INTEGER,
            FOREIGN KEY (id_link) REFERENCES links_contactos(id)
        )
    ''')
    conn.commit()

# Inicializamos la conexión y creamos las tablas
conn = get_connection()
create_tables(conn)

# Configuración de la navegación en la barra lateral de Streamlit
st.sidebar.title("Navegación")
page = st.sidebar.selectbox("Selecciona una página", ["Crear Link Contactos", "Agregar Contactos", "Ver Contactos & Exportar"])

# Página: Crear Link Contactos
if page == "Crear Link Contactos":
    st.title("Crear Link Contactos")
    with st.form("crear_link_form"):
        link_general = st.text_input("Link General")
        fecha_creacion = st.date_input("Fecha de Creación", value=datetime.date.today())
        marca = st.text_input("Marca")
        descripcion = st.text_area("Descripción")
        submitted = st.form_submit_button("Crear Link")
    if submitted:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO links_contactos (link_general, fecha_creacion, marca, descripcion)
            VALUES (?, ?, ?, ?)
        ''', (link_general, fecha_creacion.strftime("%Y-%m-%d"), marca, descripcion))
        conn.commit()
        st.success("Link Contactos creado exitosamente.")

# Página: Agregar Contactos
elif page == "Agregar Contactos":
    st.title("Agregar Contactos")
    # Se obtiene la lista de links generales creados
    df_links = pd.read_sql_query("SELECT * FROM links_contactos", conn)
    if df_links.empty:
        st.warning("No existen links. Por favor, crea un Link Contactos primero.")
    else:
        # Selección del link general al que se agregará el contacto
        opcion = st.selectbox("Selecciona el Link Contactos", df_links["link_general"])
        # Se obtiene el id del link seleccionado
        link_id = df_links[df_links["link_general"] == opcion]["id"].values[0]
        
        with st.form("agregar_contacto_form"):
            link_auto = st.text_input("Link del Auto")
            telefono = st.text_input("Teléfono")
            nombre = st.text_input("Nombre")
            auto_modelo = st.text_input("Auto")
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            submitted_contacto = st.form_submit_button("Agregar Contacto")
        if submitted_contacto:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO contactos (link_auto, telefono, nombre, auto, precio, id_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (link_auto, telefono, nombre, auto_modelo, precio, link_id))
                conn.commit()
                st.success("Contacto agregado exitosamente.")
            except sqlite3.IntegrityError as e:
                st.error("El teléfono ya existe. Por favor, ingresa un número diferente.")

# Página: Ver Contactos & Exportar
elif page == "Ver Contactos & Exportar":
    st.title("Ver Contactos & Exportar")
    # Se obtienen los links generales registrados
    df_links = pd.read_sql_query("SELECT * FROM links_contactos", conn)
    if df_links.empty:
        st.warning("No existen links. Por favor, crea un Link Contactos primero.")
    else:
        # Selección del Link Contactos
        link_selected = st.selectbox("Selecciona el Link Contactos", df_links["link_general"])
        link_id = df_links[df_links["link_general"] == link_selected]["id"].values[0]
        
        st.subheader("Filtros de Búsqueda")
        filter_nombre = st.text_input("Filtrar por Nombre")
        filter_auto = st.text_input("Filtrar por Auto")
        filter_telefono = st.text_input("Filtrar por Teléfono")
        
        # Construcción de la consulta SQL con filtros
        query = "SELECT * FROM contactos WHERE id_link = ?"
        params = [link_id]
        if filter_nombre:
            query += " AND nombre LIKE ?"
            params.append(f"%{filter_nombre}%")
        if filter_auto:
            query += " AND auto LIKE ?"
            params.append(f"%{filter_auto}%")
        if filter_telefono:
            query += " AND telefono LIKE ?"
            params.append(f"%{filter_telefono}%")
        
        df_contactos = pd.read_sql_query(query, conn, params=params)
        
        st.subheader("Contactos Registrados")
        st.dataframe(df_contactos)
        
        # Exportación a Excel
        if not df_contactos.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_contactos.to_excel(writer, index=False, sheet_name='Contactos')
                writer.save()
            processed_data = output.getvalue()
            st.download_button(
                label="Descargar Excel",
                data=processed_data,
                file_name="contactos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
