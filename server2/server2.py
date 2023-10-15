import time
from roboflow import Roboflow

# Start measuring time
start = time.time()

# Initialize the Roboflow client with your API key
rf = Roboflow(api_key="MCDp0fm5uRvdcy6LvtHE")

# Access your Roboflow project and select a specific model version
project = rf.workspace().project("fish-epcqu")
model = project.version(3).model

# Define the path to the received image you want to process
received_image = 'G000050_L-avi-100253.png'

# Use the Roboflow model to make predictions on the image
# Set confidence and overlap thresholds (adjust as needed)
predictions = model.predict(received_image, confidence=40, overlap=30)

# Save the prediction results to an output image
predictions.save("predictions.png")

# Calculate and print the time taken for the sequential processing
print("Time for sequential processing: ")
print(time.time() - start)
