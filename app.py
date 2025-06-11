from flask.sansio.app import App
 
from flask import Flask, Response
import cv2 as cv
import numpy as np

app = Flask(__name__)

# Load model files and labels
faceProto = "opencv_face_detector.pbtxt"
faceModel = "opencv_face_detector_uint8.pb"
ageProto = "age_deploy.prototxt"
ageModel = "age_net.caffemodel"
genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

# Load networks
faceNet = cv.dnn.readNet(faceModel, faceProto)
ageNet = cv.dnn.readNet(ageModel, ageProto)
genderNet = cv.dnn.readNet(genderModel, genderProto)

# Use CPU backend
for net in [faceNet, ageNet, genderNet]:
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

padding = 20
cap = cv.VideoCapture(0)  # webcam

def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight, frameWidth = frameOpencvDnn.shape[:2]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300),
                                [104, 117, 123], swapRB=False, crop=False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2),
                         (0, 255, 0), max(1, int(round(frameHeight / 150))), 8)
    return frameOpencvDnn, bboxes

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frameFace, bboxes = getFaceBox(faceNet, frame)

        if not bboxes:
            cv.putText(frame, "Face is not visible", (20, 50),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
        else:
            for bbox in bboxes:
                x1 = max(0, bbox[0] - padding)
                y1 = max(0, bbox[1] - padding)
                x2 = min(frame.shape[1] - 1, bbox[2] + padding)
                y2 = min(frame.shape[0] - 1, bbox[3] + padding)

                face = frame[y1:y2, x1:x2]

                blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False, crop=False)

                genderNet.setInput(blob)
                genderPreds = genderNet.forward()
                gender = genderList[genderPreds[0].argmax()]

                ageNet.setInput(blob)
                agePreds = ageNet.forward()
                age = ageList[agePreds[0].argmax()]

                label = f"{gender}, {age}"
                cv.putText(frameFace, label, (bbox[0], bbox[1] - 10),
                           cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)

        ret, buffer = cv.imencode('.jpg', frameFace)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return '''
    <h2>Real-time Age and Gender Detection</h2>
    <p>Click below to open the video stream:</p>
    <a href="/video_feed">Open Video Feed</a>
    '''

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
