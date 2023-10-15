import socket
import sys
from PIL import Image
import tqdm
import os
import time
import uuid
# Check for the correct command-line argument
if len(sys.argv) != 2:
    print("Usage: python server.py <uploaded_image_path>")
    sys.exit(1)

# Get the path to the uploaded image from the command-line argument
uploaded_image_path = sys.argv[1]

# Constants for file transfer
SEPARATOR = "--"
BUFFER_SIZE = 4096

# Function to send a file over a socket
def send_file(s, imagefile):
    filesize = os.path.getsize(imagefile)
    s.send(f"{imagefile}{SEPARATOR}{filesize}".encode())

    # Initialize a progress bar
    progress = tqdm.tqdm(range(filesize), f"Sending {imagefile}", unit="B", unit_scale=True, unit_divisor=1024)

    # Read and send the file in chunks
    with open(imagefile, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))



# Set up the server socket and accept connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 9000))
server_socket.listen(2)

print("Server is listening for connections...")

# Accept connections from the first set of clients (Machine 1 and Machine 2)
client_socket1, addr1 = server_socket.accept()
print(f"Machine 1 connected from {addr1}")
client_socket2, addr2 = server_socket.accept()
print(f"Machine 2 connected from {addr2}")

start = time.time()

# Open the image using PIL (Pillow)
original_image = Image.open(uploaded_image_path)

# Get the dimensions of the original image
width, height = original_image.size
print(f"Image size: {width} x {height} pixels.")

# Split the image into two equal halves
half_width = width // 2

# Crop the first half
first_half = original_image.crop((0, 0, half_width, height))
second_half = original_image.crop((half_width, 0, width, height))

# Save the cropped halves to temporary files
first_half.save('temp_cropped_image1.jpg')
second_half.save('temp_cropped_image2.jpg')

# Send the cropped images to both clients
send_file(client_socket1, 'temp_cropped_image1.jpg')
send_file(client_socket2, 'temp_cropped_image2.jpg')
os.remove('temp_cropped_image1.jpg')
os.remove('temp_cropped_image2.jpg')
# Close sockets and remove temporary files
client_socket1.close()
client_socket2.close()
server_socket.close()

print("Cropped image sent to clients.")

# Set up a new server socket on a different port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('0.0.0.0', 9001))
server_socket.listen(1) 

print("Server is listening for connections on a new port...")

# Accept connections from the second set of clients
client_socket1, addr1 = server_socket.accept()
print(f"Machine 1 connected from {addr1}")


# Receive the images from the second set of clients
received_image1 = 'received/received_image1.jpg'  # Replace with the path where you want to save the first received image
received_image2 = 'received/received_image2.jpg'  # Replace with the path where you want to save the second received image



received = client_socket1.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPARATOR)
filename = os.path.basename(filename)
filesize = int(filesize)

    # Initialize a progress bar
progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # Receive and write the file in chunks
with open(received_image1, "wb") as f:
        while True:
            bytes_read = client_socket1.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))


server_socket2.bind(('0.0.0.0', 9002))
server_socket2.listen(1)
client_socket2, addr2 = server_socket2.accept()
print(f"Machine 2 connected from {addr2}")


received = client_socket2.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPARATOR)
filename = os.path.basename(filename)
filesize = int(filesize)

    # Initialize a progress bar
progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # Receive and write the file in chunks
with open(received_image2, "wb") as f:
        while True:
            bytes_read = client_socket2.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))



print("Time distribution: ")
print(time.time() - start)



# Notify clients that the images have been received
client_socket1.send(b'')
client_socket2.send(b'')

# Close the second set of sockets
client_socket1.close()
client_socket2.close()

# Close the second server socket
server_socket.close()
server_socket2.close()
print("Second set of images received from clients.")
