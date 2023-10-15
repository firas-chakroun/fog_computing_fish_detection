from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RECEIVED_FOLDER = 'received'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    received_image_exists = os.path.exists(os.path.join(RECEIVED_FOLDER, "received_image1.jpg"))
    received_image_path = os.path.join(RECEIVED_FOLDER, "received_image1.jpg")


    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            # Save the uploaded image to the "uploads" folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            os.makedirs(RECEIVED_FOLDER, exist_ok=True)
            
            subprocess.run(["python", "server.py", filename])

            # Generate a unique filename for the received image
            unique_filename = str(uuid.uuid4()) + '.jpg'
            received_filename = os.path.join(RECEIVED_FOLDER, unique_filename)
            os.rename("received_image1.jpg", received_filename)

            
            received_images = []
            received_folder = 'received'
            for filename in os.listdir(received_folder):
                if filename.endswith('.jpg'):
                    received_images.append(filename)
            return render_template('resullt.html', received_images=received_images)


    return render_template('index.html')

    
# Route to serve received images
@app.route('/received/<filename>')
def serve_received_image(filename):
    return send_from_directory(RECEIVED_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

