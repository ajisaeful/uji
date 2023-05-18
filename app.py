from flask import Flask, render_template, request, Response
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename
import os
import cv2
from image_detection import process_image
from video_detection import video_detection
from detection_webcam import detect_objects

app = Flask(__name__)
run_with_ngrok(app)

UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = 'static/results'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                img = cv2.imread(image_path)
                result_img = process_image(img)
                result_filename = 'result.jpg'
                result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
                cv2.imwrite(result_path, result_img)
                return render_template('index.html', image_path=image_path, result_path=result_filename)
        elif 'video' in request.files:
            video = request.files['video']
            if video and allowed_file(video.filename):
                filename = secure_filename(video.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video.save(video_path)
                result_video_filename = 'result.mp4'
                result_video_path = os.path.join(app.config['RESULTS_FOLDER'], result_video_filename)
                video_generator = video_detection(video_path)

                def generate():
                    for frame in video_generator:
                        ret, jpeg = cv2.imencode('.jpg', frame)
                        frame_bytes = jpeg.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

                return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        elif 'webcam' in request.form:
            result_video_filename = 'webcam_result.mp4'
            result_video_path = os.path.join(app.config['RESULTS_FOLDER'], result_video_filename)
            video_generator = video_detection(0)  # Menggunakan ID kamera 0 untuk webcam

            def generate():
                for frame in video_generator:
                    # Perform object detection on the frame
                    processed_frame = detect_objects(frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', processed_frame)[1].tobytes() + b'\r\n\r\n')

            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return render_template('index.html')


if __name__ == '__main__':
    app.run()
