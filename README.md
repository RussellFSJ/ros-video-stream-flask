# ros_video_stream_flask
```
mkdir .venv
pipenv install
gunicorn -w 4 -t 0 -b 0.0.0.0:5000 wsgi:app
```

## Reference(s):
- https://roslibpy.readthedocs.io/en/latest/examples/05_subscribe_to_images.html
- https://github.com/miguelgrinberg/flask-video-streaming/blob/master/app.py
