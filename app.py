from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2 as cv
import numpy as np
import base64

app = Flask(__name__)
CORS(app)                                  

#Model files 
faceProto   = "opencv_face_detector.pbtxt"
faceModel   = "opencv_face_detector_uint8.pb"
ageProto    = "age_deploy.prototxt"
ageModel    = "age_net.caffemodel"
genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList    = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
              '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

faceNet   = cv.dnn.readNet(faceModel,   faceProto)
ageNet    = cv.dnn.readNet(ageModel,    ageProto)
genderNet = cv.dnn.readNet(genderModel, genderProto)

for net in (faceNet, ageNet, genderNet):          # CPU inference
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)


PADDING = 20          # pixels around the detected box
CONF_TH = 0.7         # back to the original, more accurate threshold


def getFaceBoxes(net, frame, th=CONF_TH):
    h, w = frame.shape[:2]
    blob = cv.dnn.blobFromImage(frame, 1.0, (300, 300),
                                [104, 117, 123], swapRB=False, crop=False)
    net.setInput(blob)
    detections = net.forward()
    boxes = []
    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]
        if conf > th:
            x1 = int(detections[0, 0, i, 3] * w)
            y1 = int(detections[0, 0, i, 4] * h)
            x2 = int(detections[0, 0, i, 5] * w)
            y2 = int(detections[0, 0, i, 6] * h)
            boxes.append([x1, y1, x2, y2])
    return boxes


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "Missing image field"}), 400

    try:
        #  1. decode base64 
        b64 = data["image"].split(",")[-1]
        img_bytes = base64.b64decode(b64)
        np_img = np.frombuffer(img_bytes, np.uint8)
        frame = cv.imdecode(np_img, cv.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Cannot decode image"}), 400

        # 2. face detection
        boxes = getFaceBoxes(faceNet, frame)
        predictions = []

        for (x1, y1, x2, y2) in boxes:
            # add padding but keep inside image bounds
            x1p = max(0, x1 - PADDING)
            y1p = max(0, y1 - PADDING)
            x2p = min(frame.shape[1] - 1, x2 + PADDING)
            y2p = min(frame.shape[0] - 1, y2 + PADDING)
            face = frame[y1p:y2p, x1p:x2p]

            blob = cv.dnn.blobFromImage(
                face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False
            )

            genderNet.setInput(blob)
            gender = genderList[genderNet.forward()[0].argmax()]

            ageNet.setInput(blob)
            age = ageList[ageNet.forward()[0].argmax()]

            predictions.append({
                "box": [x1, y1, x2, y2],
                "gender": gender,
                "age": age
            })

        return jsonify({"predictions": predictions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "API running. POST base64 image to /predict."


if __name__ == "__main__":
    app.run(debug=True)
