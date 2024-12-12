#!/usr/bin/env python3

import json
import time
import sys
import datetime
import paho.mqtt.client as mqtt
from seeed_dht import DHT
from gpiozero import MotionSensor

# Configuración de MQTT
MQTT_BROKER = "" #IP to the broker
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/movimiento"
MQTT_CLIENT_ID = "raspi07_client"

# Inicialización del cliente MQTT
mqtt_client = mqtt.Client(MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

# I2C Setup
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# Addresses for RGB and Text Display
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# Set backlight color (R, G, B)
def setRGB(r, g, b):
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 1, 0)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 0x08, 0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 4, r)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 3, g)
    bus.write_byte_data(DISPLAY_RGB_ADDR, 2, b)

# Send command to display
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x80, cmd)

# Set display text
def setText(text):
    textCommand(0x01)  # Clear display
    time.sleep(0.05)
    textCommand(0x08 | 0x04)  # Display on, no cursor
    textCommand(0x28)  # 2 lines
    time.sleep(0.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)  # Move to the second line
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR, 0x40, ord(c))

# Function to generate recommendations based on temperature and humidity
def obtener_recomendacion(temperatura, humedad):
    if temperatura < 15:
        return "Hace frío, ve a una cafetería."
    elif temperatura > 25:
        if humedad < 60:
            return "Hace calor y seco, ideal para un paseo."
        else:
            return "Hace calor y húmedo, busca un lugar fresco."
    elif 15 <= temperatura <= 25:
        return "Clima templado, buena para actividades al aire libre."
    else:
        return "Clima variado, busca algo cómodo."

def main():
    # Grove - Sensor de temperatura y humedad conectado al puerto D5
    sensor = DHT('11', 16)

    # Sensor de movimiento PIR conectado al GPIO 5
    pir = MotionSensor(5)
    no_motion_start = time.time()  # Registro del tiempo cuando no hay movimiento

    # Variable para controlar si ya se ha enviado un aviso por movimiento
    movement_alert_sent = False

    # Variable para controlar cuando fue la última vez que se imprimió la temperatura
    last_temp_time = 0

    while True:
        # Detecta movimiento
        if pir.motion_detected:
            if not movement_alert_sent:
                print("¡Movimiento detectado!")
                setRGB(255, 255, 0)  # Verde al detectar movimiento
                movement_alert_sent = True  # Marca que se ha enviado el aviso

                # Obtener la hora actual y enviarla a través de MQTT
                payload = json.dumps({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "event": "motion_detected",
                    "value": 1  # algún valor numérico para representar el evento
                })
                mqtt_client.publish("sensor/movimiento", payload)
                print(f"Mensaje enviado: {payload}")
        else:
            # Si no hay movimiento, restablece la variable de aviso
            if movement_alert_sent:
                print("Movimiento terminado.")
                movement_alert_sent = False  # Restablece para que se pueda enviar un aviso cuando haya nuevo movimiento
                no_motion_start = time.time()  # Reinicia el temporizador de no movimiento

            # Calcula el tiempo transcurrido sin movimiento
            no_motion_duration = time.time() - no_motion_start
            if no_motion_duration >= 10:
                # Verifica si han pasado al menos 10 segundos desde la última impresión
                if time.time() - last_temp_time >= 10:
                    # Lee la temperatura y humedad del sensor DHT
                    humi, temp = sensor.read()
                    if humi is not None and temp is not None:
                        print('Temperatura: {}C, Humedad: {}%'.format(temp, humi))

                        # Muestra en el LCD
                        setText('Temp: {0:.1f}C\nHumi: {1:.1f}%'.format(temp, humi))

                        # Genera y muestra recomendación
                        recomendacion = obtener_recomendacion(temp, humi)
                        print("Recomendación:", recomendacion)

                        # Cambia el color del LCD dependiendo de la temperatura
                        if temp < 15:
                            if humi < 60:
                                setRGB(0,191,255) #Azul claro
                            else:
                                setRGB(0,255,255) #Cian
                        elif temp > 25:
                            if humi < 60:
                                setRGB(255,165,0) #Naranja
                            else:
                                setRGB(255, 0, 0)  # Rojo
                        else:
                            if humi < 60:
                                setRGB(144,238,144) #Verde claro
                            else:
                                setRGB(0, 255, 0)  # Verde

                        # Actualiza el tiempo de la última impresión
                        last_temp_time = time.time()

                    else:
                        print("Error al leer el sensor de temperatura y humedad.")

        time.sleep(1)  # Breve pausa para evitar un bucle excesivamente rápido

if __name__ == '__main__':
    main()
