import base64
import roslibpy
from threading import Event
from flask import Flask, Response, render_template

HOST_IP = "192.168.69.2"

class ROSVideoStreamFlask:
    def __init__(self, host) :
        self.client = roslibpy.Ros(host=host, port=9090)
        self.client.run()

        self.camera_topics = self.get_camera_topics()

        self.create_stream(self.camera_topics)

    # get list of camera(s) from nodes
    def get_camera_list(self):
        camera_nodes = [node for node in self.client.get_nodes() if "camera" in node]
        camera_list = list(set([camera.split("/")[1] for camera in camera_nodes]))
        return camera_list

    # get list of camera topic(s)
    def get_camera_topics(self):
        camera_topics = [topic for topic in self.client.get_topics_for_type("sensor_msgs/CompressedImage") if "image_raw/compressed" in topic and "depth" not in topic.lower()]
        return camera_topics

    # create subscriber for every image topic
    def create_stream(self, camera_topics):
        for topic in camera_topics:
            topic_frame = topic + "_frame"
            topic_event = topic + "_event"
            topic_subscriber = topic + "_subscriber"

            setattr(self, topic_frame, None)
            setattr(self, topic_event, Event())
            setattr(self, topic_subscriber, roslibpy.Topic(self.client, topic, "sensor_msgs/CompressedImage", queue_length=1, throttle_rate=600))

            def stream_processing_callback(msg, frame=topic_frame, event=topic_event):
                self.image_processing_callback(msg, frame, event)
            
            getattr(self, topic_subscriber).subscribe(stream_processing_callback)

    # process image frame to be streamed to server
    def image_processing_callback(self, msg, frame, event):
        base64_bytes = msg["data"].encode("ascii")
        setattr(self, frame, base64.b64decode(base64_bytes))
        getattr(self, event).set()

    def get_frame(self, topic):
        getattr(self, topic + "_event").wait()
        getattr(self, topic + "_event").clear()

    def gen(self, topic):
        while True:
            self.get_frame(topic)
            yield (b"--frame\r\n"b"Content-Type: image/jpeg\r\n\r\n" + getattr(self, topic + "_frame") + b"\r\n")

if __name__ == "__main__":
    app = Flask(__name__)

    stream = ROSVideoStreamFlask(HOST_IP)

    @app.route("/")
    def home():
        return render_template("index.html", camera_list=stream.get_camera_list())

    @app.route("/<topic>")
    def show_video(topic):
        if topic != "favicon.ico":
            topic = "/" + topic.replace("-", "/")
            return Response(stream.gen(topic), mimetype="multipart/x-mixed-replace; boundary=frame")
        
    try:
        app.run(host="0.0.0.0", threaded=True, debug=True)
    except KeyboardInterrupt:
        stream.client.terminate()