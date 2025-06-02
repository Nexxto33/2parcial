import asyncio
import websockets
import cv2
import base64

async def send_frames():
    uri = "ws://192.168.159.217:8765"  
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)  

        cv2.namedWindow('Cámara', cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("No se pudo capturar el frame")
                break

            cv2.imshow('Cámara', frame)

            _, buffer = cv2.imencode('.jpg', frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8') # convierte a un texto ASCII, decode('utf-8') cadena de texto 

            await websocket.send(jpg_as_text)

            response = await websocket.recv()
            print(f"Prediccion: {response}")
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Salir")
                break

            await asyncio.sleep(0)

        cap.release()
        cv2.destroyAllWindows()

asyncio.run(send_frames())
