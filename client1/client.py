import socket
import os
import tqdm
from roboflow import Roboflow

# Constants for file transfer
SEPARATOR = "--"
BUFFER_SIZE = 4096

# Create a socket to connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server's IP address and port
client_socket.connect(('192.168.1.4', 9000))

# Receive information about the incoming file (filename and size)
received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPARATOR)
filename = os.path.basename(filename)
filesize = int(filesize)

# Initialize a progress bar to monitor the file reception
progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

# Open the file for writing and receive the file data in chunks
with open(filename, "wb") as f:
    while True:
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            break
        f.write(bytes_read)
        progress.update(len(bytes_read))

# Notify the server that the file has been received
client_socket.send(b'')

# Close the socket after file reception
client_socket.close()

# Initialize the Roboflow client with your API key
rf = Roboflow(api_key="MCDp0fm5uRvdcy6LvtHE")

# Access your Roboflow project and select a specific model version
project = rf.workspace().project("fish-epcqu")
model = project.version(3).model

# Define the path to the received image
received_image = 'temp_cropped_image1.jpg'

# Use the Roboflow model to make predictions on the image
# Set confidence and overlap thresholds (adjust as needed)
predictions = model.predict(received_image, confidence=40, overlap=30)

# Save the prediction results to an output image
predictions.save("predictions1.jpg")

# Define the path to the resulting image file
image_file = "predictions1.jpg"

# Create a new socket to connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server's IP address and a different port (9001)
client_socket.connect(('192.168.1.4', 9001))

# Get the size of the image file for transfer
filesize = os.path.getsize(image_file)

# Send the filename and filesize to the server
client_socket.send(f"{image_file}{SEPARATOR}{filesize}".encode())

# Initialize a progress bar for monitoring the file send process
progress = tqdm.tqdm(range(filesize), f"Sending {image_file}", unit="B", unit_scale=True, unit_divisor=1024)

# Send the image file data to the server in chunks
with open(image_file, "rb") as f:
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break
        client_socket.sendall(bytes_read)
        progress.update(len(bytes_read))

# Notify the server that the file has been sent
client_socket.send(b'')
os.remove('temp_cropped_image1.jpg')
os.remove('predictions1.jpg')
# Close the socket after file transmission
client_socket.close()
