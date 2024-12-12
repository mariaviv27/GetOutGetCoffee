import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
import json

# Configuración de la base de datos MySQL
db_config = {    # Cambia esto si MySQL está en otro servidor
    'user': 'root',     # Usuario de MySQL
    'password': 'root', # Contraseña de MySQL
    'database': 'movimiento' # Base de datos donde guardarás los datos
}

# Función para conectar a MySQL
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Conectado a MySQL")
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# Función para insertar datos en MySQL
def insert_into_mysql(connection, sensor_id, timestamp, value):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO datos_sensor (sensor_id, timestamp, valor) VALUES (%s, %s, %s)"
        cursor.execute(query, (sensor_id, timestamp, value))
        connection.commit()
        print(f"Datos insertados: Sensor ID: {sensor_id}, Tiempo: {timestamp}, Valor: {value}")
    except Error as e:
        print(f"Error insertando datos: {e}")

# Callback para procesar los mensajes MQTT
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        timestamp = payload.get("timestamp")  # Suponiendo que el payload tiene este campo
        sensor_id = payload.get("sensor_id")  # Suponiendo que el payload tiene este campo
        value = payload.get("value")  # Suponiendo que el payload tiene este campo

        # Conectar a MySQL y guardar los datos
        connection = connect_to_mysql()
        if connection:
            insert_into_mysql(connection, sensor_id, timestamp, value)
            connection.close()
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

# Configuración del cliente MQTT
mqtt_broker = "10.172.117.171"  # Dirección del broker MQTT
mqtt_port = 1883
mqtt_topic = "sensor/movimiento"  # Tópico del sensor

# Crear el cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

# Conectar al broker MQTT
mqtt_client.connect(mqtt_broker, mqtt_port, 60)

# Suscribirse al tópico
mqtt_client.subscribe(mqtt_topic)

# Iniciar el loop del cliente MQTT
mqtt_client.loop_forever()
