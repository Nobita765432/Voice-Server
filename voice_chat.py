import socket
import threading
import pyaudio
import time

# ==== CONFIGURATION ====
PORT = 5000  # Port to use for connections
BUFFER_SIZE = 1024  # Audio buffer size
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate
USERNAME = input("Enter your username: ")  # Ask for username

# Check if we are the first to run (i.e., act as the server)
def find_server():
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
    print("Running as SERVER")
else:
    print(f"Connecting to SERVER at {SERVER_IP}")

# ==== SOCKET SETUP ====
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, PORT))
server.listen(5)

clients = []

def handle_client(conn, addr):
    username = conn.recv(1024).decode()
    print(f"{username} joined the call!")

    clients.append((conn, username))

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
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

# Audio input/output
audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=BUFFER_SIZE)
stream_output = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=BUFFER_SIZE)

# Send audio
def send_audio():
    while True:
        data = stream_input.read(BUFFER_SIZE)
        client.sendall(data)

# Receive audio
def receive_audio():
    while True:
        data = client.recv(BUFFER_SIZE)
        if not data:
            break
        stream_output.write(data)

# Start sending and receiving audio
threading.Thread(target=send_audio, daemon=True).start()
threading.Thread(target=receive_audio, daemon=True).start()

# Keep running
print("Waiting for users...")
while True:
    time.sleep(1)
