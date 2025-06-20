# DATOS_CONSIGNACION

**DATOS_CONSIGNACION** es una aplicación en Python para recolectar y organizar
contactos de venta de autos. Usa scraping con Requests y BeautifulSoup para
obtener datos y Streamlit como interfaz de gestión.

Estructura del proyecto:

- `src/` – código principal (`app.py`).
- `data/` – base SQLite e imágenes generadas.
- `docs/` – documentación general.
- `docs/examples/` – listados de código de ejemplo utilizados durante el desarrollo.

Los listados de código que antes estaban sueltos en `docs/` se agruparon ahora
en `docs/examples/`. Estos archivos contienen pruebas y macros usados como
referencia durante la creación de la aplicación.

Para ejecutar la aplicación:

```bash
streamlit run src/app.py
```

## 2. Objetivos del Proyecto

- **Ingreso y Almacenamiento de Datos:**  
  Registrar y agrupar datos de contactos asociados a un link general (URL base) en una base de datos SQLite.

- **Extracción Automática de Información:**  
  Utilizar scraping (con Requests y BeautifulSoup) para extraer automáticamente información clave de páginas de autos:
  - Imagen de contacto (decodificada desde datos en base64)
  - Detalles del vehículo (nombre, año, precio y descripción)
  - Número de WhatsApp (extracción mediante función específica)

- **Interfaz Interactiva y Gestión:**  
  Proveer un sistema interactivo para crear grupos de contactos, agregar y editar contactos, filtrar registros y exportar los datos a Excel.

- **Validación y Consistencia:**  
  Asegurar la integridad de los datos mediante validaciones (por ejemplo, evitando la duplicación de números de teléfono) y ofreciendo herramientas para actualizar o eliminar registros.

## 3. Funcionalidades Principales

### 3.1 Crear Link Contactos

- **Formulario de Creación:**  
  Permite ingresar los siguientes datos:
  - **Link General:** URL base que agrupa los contactos.
  - **Fecha de Creación:** Fecha (por defecto, la actual).
  - **Marca:** Marca relacionada al grupo.
  - **Descripción:** Información adicional o notas sobre el grupo.

### 3.2 Agregar Contactos

- **Campos del Formulario:**  
  Una vez creado el link general, se pueden registrar contactos individuales con los siguientes campos:
  - **Link del Auto:** URL específica de la ficha del auto. Este campo, al ser ingresado, activa el scraping para extraer información.
  - **Teléfono:** Número de contacto (se valida que sea único).
  - **Nombre:** Nombre del contacto.
  - **Auto:** Modelo o nombre del vehículo, prellenado en parte con la información extraída.
  - **Precio:** Precio del vehículo, extraído y formateado (se procesa para eliminar comas, por ejemplo).
  - **Descripción del Contacto:** Detalles adicionales o descripción extraída de la página.

- **Extracción Automática de Datos:**  
  La función `scrape_vehicle_details(url)` realiza lo siguiente:
  - Envía una solicitud HTTP a la URL dada.
  - Extrae la imagen de contacto (usando datos base64).
  - Obtiene los detalles del vehículo, combinando año y nombre.
  - Busca y extrae el precio y una breve descripción.
  - Utiliza `extract_whatsapp_number(soup)` para obtener el número de WhatsApp (eliminando el prefijo "56" si se encuentra).  

- **Borrado de Campos:**  
  Se implementa un botón que, al ser presionado (ubicado antes del widget "Link del Auto"), limpia los valores de los campos del formulario y del propio link. Esto garantiza que, en la siguiente renderización, todos los campos se muestren vacíos.

### 3.3 Visualización, Búsqueda y Exportación

- **Visualización de Registros:**  
  Los datos se muestran en tablas interactivas (utilizando Pandas DataFrame) con opciones de filtrado por nombre, auto y teléfono.

- **Exportación a Excel:**  
  Los registros filtrados se pueden exportar a un archivo Excel mediante XlsxWriter y un botón de descarga.

### 3.4 Edición y Eliminación

- **Actualizar Registros:**  
  Se ofrece la posibilidad de editar tanto contactos como links. Mediante formularios se permite modificar los datos existentes y actualizar la base de datos.

- **Eliminar Contactos:**  
  También se brinda la opción de eliminar registros de la tabla `contactos`.

## 4. Arquitectura del Código

### 4.1 Tecnologías y Herramientas Utilizadas

- **Streamlit:**  
  Framework para construir la interfaz interactiva y gestionar la navegación (páginas: Crear Link, Agregar Contactos, Ver Contactos & Exportar, Editar).

- **SQLite:**  
  Base de datos ligera utilizada para almacenar los datos en dos tablas principales.

- **Pandas:**  
  Manipulación y exportación de datos.

- **Requests y BeautifulSoup:**  
  Técnicas de scraping para extraer información de páginas web.

- **Re y Base64:**  
  Utilizados para la extracción de patrones (como el número de WhatsApp) y la decodificación de imágenes.

### 4.2 Estructura del Código

- **Configuración Inicial y Estilos:**  
  Se inyectan estilos CSS personalizados y se utiliza JavaScript para prevenir el envío de formularios mediante la tecla Enter.

- **Gestión de Base de Datos:**  
  - Función `get_connection()`: Retorna la conexión a la base de datos SQLite.  
  - Función `create_tables()`: Crea las tablas `links_contactos` y `contactos` si aún no existen.

- **Funciones de Scraping:**  
  - `extract_whatsapp_number(soup)`: Busca y extrae el número de WhatsApp de enlaces que siguen el patrón especificado.  
  - `scrape_vehicle_details(url)`: Realiza el scraping completo para obtener la imagen, detalles del vehículo y número de WhatsApp, y retorna la información en un diccionario.

- **Operaciones CRUD:**  
  - Inserción de registros en las tablas `links_contactos` y `contactos`.
  - Actualización de datos mediante funciones como `update_link_record()` y `update_contact()`.
  - Eliminación de contactos mediante `delete_contact()`.

- **Interfaz de Usuario y Navegación:**  
  La aplicación utiliza `st.sidebar` para cambiar entre las diferentes páginas y formularios, facilitando la creación, visualización y edición de datos.

## 5. Estructura de la Base de Datos

La base de datos SQLite está compuesta por dos tablas principales:

### 5.1 Tabla `links_contactos`

Esta tabla agrupa los contactos bajo un link general y contiene la siguiente información:

- **id:**  
  - **Tipo:** INTEGER  
  - **Restricción:** PRIMARY KEY AUTOINCREMENT  
  - **Descripción:** Identificador único del link.

- **link_general:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** URL base que agrupa un conjunto de contactos.

- **fecha_creacion:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Fecha en la que se crea el registro, generalmente la fecha actual.

- **marca:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Marca asociada al link de contactos.

- **descripcion:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Información adicional o descripción del grupo de contactos.

### 5.2 Tabla `contactos`

Esta tabla almacena la información específica de cada contacto y se relaciona con la tabla `links_contactos` mediante la clave foránea `id_link`.

- **id:**  
  - **Tipo:** INTEGER  
  - **Restricción:** PRIMARY KEY AUTOINCREMENT  
  - **Descripción:** Identificador único del contacto.

- **link_auto:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** URL específica de la ficha del auto.

- **telefono:**  
  - **Tipo:** TEXT  
  - **Restricción:** UNIQUE, NOT NULL  
  - **Descripción:** Número de teléfono del contacto. Se valida para evitar duplicados.

- **nombre:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Nombre del contacto.

- **auto:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Modelo o nombre del vehículo; se extrae y precompone en parte mediante el scraping.

- **precio:**  
  - **Tipo:** REAL  
  - **Restricción:** NOT NULL  
  - **Descripción:** Precio del vehículo, almacenado en formato numérico.

- **descripcion:**  
  - **Tipo:** TEXT  
  - **Restricción:** NOT NULL  
  - **Descripción:** Descripción o detalles adicionales del contacto.

- **id_link:**  
  - **Tipo:** INTEGER  
  - **Descripción:** Clave foránea que relaciona el contacto con un registro en `links_contactos`.

## 6. Dependencias y Requisitos

- **Librerías Principales:**  
  - Python (3.8 o superior)  
  - Streamlit  
  - SQLite3 (incluido en la librería estándar)  
  - Pandas  
  - Requests  
  - BeautifulSoup4  
  - XlsxWriter  
  - Re, Base64, datetime

- **Archivo de Requerimientos:**  
  Se recomienda mantener un `requirements.txt` actualizado para facilitar la instalación y el despliegue del proyecto.

## 7. Empaquetado y Despliegue

Para generar un ejecutable autónomo que funcione en cualquier PC sin necesidad de instalar manualmente las dependencias, se puede utilizar **PyInstaller** o **auto-py-to-exe**.

### Ejemplo de Comando con PyInstaller (en Windows):

```bash
pyinstaller --onefile --windowed --hidden-import=importlib_metadata --collect-all streamlit --collect-all bs4 --add-data "str.py;." run.py


Puntos a Considerar:

Utilizar la opción --onefile para generar un ejecutable único.

Incluir todos los módulos y recursos necesarios.

Asegurarse de que el sistema destino tenga instalados los componentes necesarios (por ejemplo, Microsoft Visual C++ Redistributable en Windows).

##8. Instrucciones de Uso
Ejecución de la Aplicación:

bash
Copiar
Navegación:

Crear Link Contactos:
Registra la URL base, fecha, marca y descripción para agrupar contactos.

Agregar Contactos:
Selecciona el link creado, ingresa el "Link del Auto" y deja que el sistema extraiga automáticamente los datos (teléfono, nombre, auto, precio y descripción) para luego poder editarlos o confirmarlos.

Ver Contactos & Exportar:
Filtra y visualiza los registros existentes y exporta los datos a un archivo Excel.

Editar:
Permite actualizar o eliminar contactos y links mediante formularios interactivos.

Mensajes:
Gestiona plantillas para enviar por WhatsApp. Los textos pueden incluir
marcadores como `{nombre}` o `{auto}` que se sustituyen automáticamente
con la información del contacto al generar los enlaces.

Borrar Campos: Se ha implementado un botón que, al ser presionado (ubicado antes del widget "Link del Auto"), limpia el contenido de ese campo y de los demás formularios asociados, facilitando el ingreso de nuevos datos sin conflictos con los valores almacenados en st.session_state.

##9. Mejoras Futuras
Optimización del Scraping:
Mejorar el manejo de errores y ampliar la extracción de datos para soportar diferentes estructuras de páginas web.

Mejora de la Interfaz:
Incorporar opciones adicionales para la edición y validación en tiempo real de los formularios.

Seguridad y Validación:
Reforzar las validaciones tanto a nivel de cliente como de servidor para evitar posibles inyecciones SQL y asegurar la integridad de los datos.

Internacionalización:
Ampliar el soporte de idiomas y formatos, permitiendo una mayor versatilidad en la aplicación.
