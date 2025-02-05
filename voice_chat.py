import socket
import threading
import sounddevice as sd
import numpy as np
import time
import os  # Import os to get PC username

# ==== CONFIGURATION ====
PORT = 5000  # Port for connections
BUFFER_SIZE = 1024  # Audio buffer size
SAMPLE_RATE = 44100  # Audio sample rate
CHANNELS = 1  # Mono audio
USERNAME = os.getenv('USERNAME') or os.getenv('USER') or "UnknownUser"  # PC Username

# ==== SERVER DISCOVERY ====
def find_server():
    """Check if a server IP exists in a local file"""
    global SERVER_IP
    try:
        with open("server_ip.txt", "r") as file:
            SERVER_IP = file.read().strip()
            return SERVER_IP
    except FileNotFoundError:
        return None

# Create or find the server
SERVER_IP = find_server()
if SERVER_IP is None:
    # If no server exists, we become the server
    SERVER_IP = socket.gethostbyname(socket.gethostname())
    with open("server_ip.txt", "w") as file:
        file.write(SERVER_IP)
    print(f"Running as SERVER on {SERVER_IP}")
else:
    print(f"Connecting to SERVER at {SERVER_IP}")

# ==== SOCKET SETUP ====
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, PORT))
server.listen(5)

clients = []

def handle_client(conn, addr):
    """Handle individual client connections"""
    username = conn.recv(1024).decode()
    print(f"{username} joined the call!")

    clients.append((conn, username))

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            # Send received data to all clients except sender
            for client, _ in clients:
                if client != conn:
                    client.sendall(data)
        except:
            break

    print(f"{username} left the call.")
    clients.remove((conn, username))
    conn.close()

# Start listening for new connections
def start_server():
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

threading.Thread(target=start_server, daemon=True).start()

# ==== CLIENT SETUP ====
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
client.send(USERNAME.encode())

# ==== AUDIO STREAMING ====
def send_audio(indata, frames, time, status):
    """Send audio data to the server"""
    if status:
        print(status)
    client.sendall(indata.tobytes())

def receive_audio():
    """Receive and play audio from the server"""
    while True:
        data = client.recv(BUFFER_SIZE)
        if not data:
            break
        audio_data = np.frombuffer(data, dtype=np.int16)
        sd.play(audio_data, SAMPLE_RATE)

# Start audio input stream
input_stream = sd.InputStream(callback=send_audio, channels=CHANNELS, samplerate=SAMPLE_RATE)
input_stream.start()

# Start receiving audio
threading.Thread(target=receive_audio, daemon=True).start()

# Keep running
print("Waiting for users...")
while True:
    time.sleep(1)
