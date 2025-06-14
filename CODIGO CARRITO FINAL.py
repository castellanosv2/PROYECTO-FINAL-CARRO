import cv2
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import time

# Pines del L298N
IN1 = 16
IN2 = 19
IN3 = 20
IN4 = 26

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Funciones de movimiento
def avanzar():
    GPIO.output(IN1, True)
    GPIO.output(IN2, False)
    GPIO.output(IN3, True)
    GPIO.output(IN4, False)

def detener():
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)

print("⏳ Espera 10 segundos para colocarlo en el suelo...")
time.sleep(10)

try:
    while True:
        # Captura de imagen rápida
        subprocess.run([
            "libcamera-still",
            "-o", "foto.jpg",
            "--width", "160", "--height", "120",
            "--shutter", "10000",  # Exposición baja
            "--nopreview", "-n"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Leer y convertir la imagen
        img = cv2.imread("foto.jpg")
        if img is None:
            continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Máscara de VERDE
        mask_green = cv2.inRange(hsv, (40, 50, 50), (90, 255, 255))
        green_pixels = cv2.countNonZero(mask_green)

        # Máscara de ROJO
        mask_red1 = cv2.inRange(hsv, (0, 50, 30), (10, 255, 255))
        mask_red2 = cv2.inRange(hsv, (160, 50, 30), (180, 255, 255))
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        red_pixels = cv2.countNonZero(mask_red)

        print(f"🟢 Verde: {green_pixels} | 🔴 Rojo: {red_pixels}")

        # Reglas de movimiento
        if red_pixels > 300:
            print("🛑 Rojo detectado → DETENIDO")
            detener()
        elif green_pixels > 250:
            print("✅ Verde detectado → AVANZANDO")
            avanzar()
        else:
            print("⏹ Nada claro → DETENIDO")
            detener()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("🛑 Interrumpido manualmente")
finally:
    detener()
    GPIO.cleanup()