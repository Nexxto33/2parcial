import asyncio
import websockets
import cv2
import base64
import re
import serial
import time


ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
time.sleep(2)
print("Transmitiendo comandos a la Tiva C...")
async def send_frames():
    uri = "ws://192.168.159.217:8765"
    
    conteo_botellas = {"Coca-Cola": 0, "PEPSI": 0, "Sprite": 0}

    try:
        async with websockets.connect(uri) as websocket:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: No se pudo abrir la cámara.")
                return

            cv2.namedWindow('Cámara', cv2.WINDOW_NORMAL)
            inicio = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("No se pudo capturar el frame")
                    break

                cv2.imshow('Cámara', frame)

                _, buffer = cv2.imencode('.jpg', frame)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')

                await websocket.send(jpg_as_text)
                response = await websocket.recv()

                match = re.match(r"(.*)\s+\(([\d.]+)%\)", response)
                if match:
                    nombre = match.group(1).strip()
                    porcentaje = float(match.group(2))

                    print(f"Nombre: {nombre}")
                    print(f"Porcentaje: {porcentaje}%")

                    if porcentaje > 52:
                        if nombre == "Coca-Cola":
                            print("Envio Coca-Cola")
                            ser.write("A\n".encode('utf-8'))
                            conteo_botellas["Coca-Cola"] += 1
                        elif nombre == "Sprite":
                            print("Envio Sprite")
                            ser.write("C\n".encode('utf-8'))
                            conteo_botellas["Sprite"] += 1
                    else:                    
                        if nombre in ["Coca-Cola", "Sprite"]:
                                print("NADA")
                                ser.write("D\n".encode('utf-8'))
                    if nombre == "PEPSI":
                        print("Envio PEPSI")
                        ser.write("B\n".encode('utf-8'))
                        conteo_botellas["PEPSI"] += 1
                else:
                    print(f"Respuesta no válida: {response}")

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Salir manual")
                    break

                if time.time() - inicio > 60:
                    print("Detección finalizada")
                    break

                await asyncio.sleep(0)

            cap.release()
            cv2.destroyAllWindows()

            print("\nResultado final de conteo:")
            print(conteo_botellas)

    except Exception as e:
        print(f" Ocurrió un error: {e}")

if __name__ == "__main__":
    asyncio.run(send_frames())
