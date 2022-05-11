import base64
import roslibpy
from threading import Event
from flask import Flask, Response


app = Flask(__name__)

frame = None 
event = Event()

client = roslibpy.Ros(host="192.168.69.2", port=9090)
client.run()

@app.route("/")
def home():
    return "hello this is our page <h1>hello from flask</h1>"

@app.route("/video")
def show_video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def receive_image(msg):
    global frame
    base64_bytes = msg['data'].encode('ascii')
    frame = base64.b64decode(base64_bytes)
    event.set()

def get_frame():
    event.wait()
    event.clear()
    return frame

def gen():
    while True:
        frame = get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

subscriber = roslibpy.Topic(client, '/camera/color/image_raw/compressed', 'sensor_msgs/CompressedImage', queue_length=1, throttle_rate=600)
subscriber.subscribe(receive_image)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    except KeyboardInterrupt:
        client.terminate()