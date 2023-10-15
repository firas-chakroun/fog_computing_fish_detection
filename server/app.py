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
    if request.method == 'POST':
        # Check if a file was submitted in the POST request
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Check if the file is empty
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # Save the uploaded image to the "uploads" folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            # Create a new folder for the received images (if it doesn't exist)
            os.makedirs(RECEIVED_FOLDER, exist_ok=True)

            
            # Delete any existing files in the "received" folder
            
            for filename in os.listdir(RECEIVED_FOLDER):
                if filename.endswith('.jpg'):
                    filename = os.path.join(RECEIVED_FOLDER, filename)
                    os.remove(filename)

            # Run the server script as a subprocess
            subprocess.run(["python", "server.py", filename])

            

            
            received_images = []
            for filename in os.listdir(RECEIVED_FOLDER):
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

