import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd
import os
import signal
import sys
from sqlalchemy import create_engine

# Configuración de la base de datos MySQL
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'movimiento'
}

# Crear motor SQLAlchemy
db_url = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
engine = create_engine(db_url)

# Carpeta para guardar el gráfico
output_folder = "graficos_guardados"
os.makedirs(output_folder, exist_ok=True)

# Función para obtener datos agrupados por día
def fetch_daily_counts():
    try:
        query = """
        SELECT DATE(timestamp) as dia, COUNT(*) as total
        FROM datos_sensor
        GROUP BY DATE(timestamp)
        ORDER BY dia;
        """
        df = pd.read_sql(query, engine)
        df['dia'] = pd.to_datetime(df['dia'])
        return df
    except Error as e:
        print(f"Error consultando la base de datos: {e}")
        return pd.DataFrame()

# Función para guardar el gráfico al cerrar
def save_last_graph():
    df = fetch_daily_counts()
    if not df.empty:
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df['dia'].dt.strftime('%Y-%m-%d'), df['total'], color='skyblue')
        for bar, label in zip(bars, df['total']):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() - 0.2,
                str(label),
                ha='center', va='bottom', fontsize=10, color='black'
            )
        plt.xlabel('Día')
        plt.ylabel('Cantidad de Salidas')
        plt.title('Salidas por Día')
        plt.xticks(rotation=45)
        plt.tight_layout()

        filepath = os.path.join(output_folder, "grafico_final.png")
        plt.savefig(filepath)
        print(f"Gráfico guardado en: {filepath}")
        plt.close()  # Cierra la figura para liberar memoria

# Configurar un manejador para guardar el gráfico al cerrar
def handle_exit(signal, frame):
    print("Cerrando el programa y guardando el gráfico...")
    save_last_graph()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # Terminar desde el sistema

# Función para actualizar el gráfico
def update(frame):
    plt.clf()
    df = fetch_daily_counts()
    if not df.empty:
        bars = plt.bar(df['dia'].dt.strftime('%Y-%m-%d'), df['total'], color='skyblue')
        for bar, label in zip(bars, df['total']):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() - 0.2,
                str(label),
                ha='center', va='bottom', fontsize=10, color='black'
            )
        plt.xlabel('Día')
        plt.ylabel('Cantidad de Salidas')
        plt.title('Salidas por Día')
        plt.xticks(rotation=45)
        plt.tight_layout()

# Configuración del gráfico con matplotlib.animation
fig = plt.figure()
ani = FuncAnimation(fig, update, interval=5000)

try:
    plt.show()
except Exception as e:
    print(f"Error al mostrar el gráfico: {e}")
finally:
    save_last_graph()
