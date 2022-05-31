from app import ROSVideoStreamFlask
from flask import Flask, Response, render_template, jsonify

app = Flask(__name__)

stream = ROSVideoStreamFlask()

@app.route("/")
def home():
    return render_template("index.html", camera_list=stream.get_camera_list())

@app.route("/.json")
def show_camera_urls():
    camera_urls = {camera:camera + "-color-image_raw-compressed" for camera in stream.get_camera_list()}
    response = jsonify(dict(sorted(camera_urls.items())))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/<topic>")
def show_video(topic):
    topic = "/" + topic.replace("-", "/")
    response = Response(stream.gen(topic), mimetype="multipart/x-mixed-replace; boundary=frame")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
    
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", threaded=True, debug=False)
    except KeyboardInterrupt:
        stream.client.terminate()
 