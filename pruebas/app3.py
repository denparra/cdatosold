import os

def reset_database_file(db_filename):
    if os.path.exists(db_filename):
        os.remove(db_filename)
        print("Base de datos borrada.")
    else:
        print("No existe la base de datos para borrar.")

# En el inicio de tu código, antes de obtener la conexión:
db_filename = 'datos_consignacion.db'
reset_database_file(db_filename)
