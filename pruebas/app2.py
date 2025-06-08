import streamlit as st
import sqlite3
import pandas as pd
import datetime
from io import BytesIO

# CSS para mejorar la responsividad y el diseño
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: auto;
    }
    input, textarea {
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

# JavaScript para deshabilitar la sumisión con Enter (evita duplicar entradas)
disable_enter_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('keydown', function(e) {
      // Evita el envío al presionar Enter
      if (e.key === 'Enter') {
        e.preventDefault();
      }
    });
  });
});
</script>
"""

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
    st.markdown(disable_enter_js, unsafe_allow_html=True)  # Inyectamos JS para deshabilitar Enter
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
    st.markdown(disable_enter_js, unsafe_allow_html=True)  # Inyectamos JS para deshabilitar Enter
    
    # Se obtienen los links generales creados
    df_links = pd.read_sql_query("SELECT * FROM links_contactos", conn)
    if df_links.empty:
        st.warning("No existen links. Por favor, crea un Link Contactos primero.")
    else:
        # Crear una columna 'display' que combine link_general y marca
        df_links['display'] = df_links.apply(
            lambda row: f"{row['link_general']} - {row['marca']}" if row['marca'] and row['marca'].strip() != "" else f"{row['link_general']} - Sin marca",
            axis=1
        )
        opcion = st.selectbox("Selecciona el Link Contactos", df_links['display'])
        # Obtiene el id correspondiente al link seleccionado
        link_id = df_links[df_links['display'] == opcion]["id"].values[0]
        
        with st.form("agregar_contacto_form"):
            link_auto = st.text_input("Link del Auto")
            telefono = st.text_input("Teléfono")
            nombre = st.text_input("Nombre")
            auto_modelo = st.text_input("Auto")
            # Permitir copiar y pegar precios con comas (por ejemplo: 10,500,000)
            precio_str = st.text_input("Precio (ej: 10,500,000)")
            submitted_contacto = st.form_submit_button("Agregar Contacto (Ctrl + Space)")
        
        if submitted_contacto:
            # Convertir el precio eliminando comas y espacios
            try:
                precio_clean = precio_str.replace(",", "").strip()
                precio = float(precio_clean)
            except ValueError:
                st.error("Precio inválido. Asegúrate de ingresar un número, por ejemplo: 10,500,000")
                st.stop()
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO contactos (link_auto, telefono, nombre, auto, precio, id_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (link_auto, telefono, nombre, auto_modelo, precio, link_id))
                conn.commit()
                st.success("Contacto agregado exitosamente.")
            except sqlite3.IntegrityError:
                st.error("El teléfono ya existe. Por favor, ingresa un número diferente.")

# Página: Ver Contactos & Exportar
elif page == "Ver Contactos & Exportar":
    st.title("Ver Contactos & Exportar")
    df_links = pd.read_sql_query("SELECT * FROM links_contactos", conn)
    if df_links.empty:
        st.warning("No existen links. Por favor, crea un Link Contactos primero.")
    else:
        # Mostrar el link junto con la marca
        df_links['display'] = df_links.apply(
            lambda row: f"{row['link_general']} - {row['marca']}" if row['marca'] and row['marca'].strip() != "" else f"{row['link_general']} - Sin marca",
            axis=1
        )
        link_selected = st.selectbox("Selecciona el Link Contactos", df_links['display'])
        link_id = df_links[df_links['display'] == link_selected]["id"].values[0]
        
        st.subheader("Filtros de Búsqueda")
        filter_nombre = st.text_input("Filtrar por Nombre")
        filter_auto = st.text_input("Filtrar por Auto")
        filter_telefono = st.text_input("Filtrar por Teléfono")
        
        # Construir la consulta SQL con los filtros
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
