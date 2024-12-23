import os
import sys
import subprocess
import time
from flask import Flask, jsonify
from pyngrok import ngrok
import serial
import re

app = Flask(__name__)

def install_dependencies():
    """
    Installs required Python packages and ensures ngrok is installed.
    """
    try:
        print("Installing required Python packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "pyserial", "pyngrok"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def find_usb_scale():
    """
    Finds the USB scale device based on its descriptors or serial connection.
    Returns the device object if found, else None.
    """
    print("Searching for USB scale...")
    if os.name == 'nt':  # Windows
        for port in range(1, 256):
            try:
                ser = serial.Serial(f'COM{port}', baudrate=9600, timeout=1)
                if ser.is_open:
                    ser.write(b'CHECK')
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Found USB scale at COM{port}")
                    return ser
            except serial.SerialException:
                continue
    else:  # Linux or macOS
        for dev in os.listdir('/dev'):
            if dev.startswith('ttyUSB') or dev.startswith('ttyACM'):
                try:
                    serial_port = f'/dev/{dev}'
                    ser = serial.Serial(serial_port, baudrate=9600, timeout=1)
                    if ser.is_open:
                        ser.write(b'CHECK')
                        data = ser.readline().decode('utf-8').strip()
                        print(f"Found USB scale at /dev/{dev}")
                        return ser
                except serial.SerialException:
                    continue
    return None

def parse_scale_data(raw_data):
    """
    Parses raw data from the scale and extracts the weight and unit.
    """
    cleaned_data = re.sub(r'^[^\d]*', '', raw_data)
    cleaned_data = re.sub(r'[^0-9\.g]', '', cleaned_data)
    cleaned_data = cleaned_data.strip()

    match = re.match(r'([0-9]+(?:\.[0-9]+)?)\s*(g|kg|lb)?', cleaned_data)

    if match:
        weight = match.group(1)
        try:
            weight = float(weight)
        except ValueError:
            return None, None
        unit = match.group(2) if match.group(2) else 'g'
        return weight, unit
    return None, None

def read_usb_scale_data():
    """
    Connects to the USB scale and reads data.
    """
    scale = find_usb_scale()
    if scale is None:
        return {"error": "USB scale not found"}, 404

    try:
        data = scale.readline().decode('utf-8').strip()
        weight, unit = parse_scale_data(data)
        if weight is not None:
            return {"weight": weight, "unit": unit}, 200
        return {"error": "Failed to parse weight from scale data"}, 500
    except Exception as e:
        return {"error": f"Error reading scale: {str(e)}"}, 500

@app.route('/read-scale', methods=['GET'])
def read_scale():
    """
    Endpoint to read data from the USB scale.
    """
    result, status = read_usb_scale_data()
    return jsonify(result), status

def start_ngrok():
    """
    Starts an ngrok tunnel and retrieves the public URL.
    """
    try:
        print("Starting ngrok tunnel...")
        public_url = ngrok.connect(5000, bind_tls=True).public_url
        print(f"ngrok tunnel started: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        sys.exit(1)

def start_flask():
    """
    Starts the Flask app in a separate thread.
    """
    from threading import Thread

    def run():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

    flask_thread = Thread(target=run)
    flask_thread.start()

def setup_ngrok_authtoken():
    authtoken = "2qdKGqK5mpzTM8e90JQGUXGyK4B_4qB38vrTkGxSKqRTJDTNo"  # Replace with your ngrok authtoken
    try:
        ngrok.set_auth_token(authtoken)
        print("ngrok authtoken configured.")
    except Exception as e:
        print(f"Error setting up ngrok authtoken: {e}")

if __name__ == '__main__':
    print("Setting up environment...")
    install_dependencies()

    print("Starting Flask app...")
    start_flask()
    setup_ngrok_authtoken()

    public_url = start_ngrok()
    print(f"Your Flask app is now exposed to the internet at: {public_url}")
