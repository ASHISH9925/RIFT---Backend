
from websockets.sync.client import connect

def main():
    with connect("ws://localhost:8000/ws/") as websocket:
        message = websocket.recv()
        print(f"Received: {message}")

while 1:
    main()