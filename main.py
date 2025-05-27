import cv2 as cv
import time
import argparse
import numpy as np 

def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight, frameWidth = frameOpencvDnn.shape[:2]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], swapRB=False, crop=False)
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


def main():
    parser = argparse.ArgumentParser(description='Age and Gender Recognition using OpenCV.')
    parser.add_argument('--input', help='Path to image or video file. Skip to use camera.')
    args = parser.parse_args()

    # Model files
    faceProto = "opencv_face_detector.pbtxt"
    faceModel = "opencv_face_detector_uint8.pb"
    ageProto = "age_deploy.prototxt"
    ageModel = "age_net.caffemodel"
    genderProto = "gender_deploy.prototxt"
    genderModel = "gender_net.caffemodel"

    # Labels and mean values
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    genderList = ['Male', 'Female']

    # Load networks
    faceNet = cv.dnn.readNet(faceModel, faceProto)
    ageNet = cv.dnn.readNet(ageModel, ageProto)
    genderNet = cv.dnn.readNet(genderModel, genderProto)

    # Set preferable backend and target (CPU here; change to CUDA if available)
    faceNet.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    faceNet.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
    ageNet.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    ageNet.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
    genderNet.setPreferableBackend(cv.dnn.DNN_BACKEND_DEFAULT)
    genderNet.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    cap = cv.VideoCapture(args.input if args.input else 0)
    padding = 20

    while cv.waitKey(1) < 0:
        t = time.time()
        hasFrame, frame = cap.read()
        if not hasFrame:
            break

        frameFace, bboxes = getFaceBox(faceNet, frame)
        if not bboxes:
            # Display "Face is not visible" if no faces detected
            cv.putText(frame, "Face is not visible", (20, 50),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            cv.imshow("Age Gender Demo", frame)
            continue

        for bbox in bboxes:
            x1 = max(0, bbox[0] - padding)
            y1 = max(0, bbox[1] - padding)
            x2 = min(frame.shape[1] - 1, bbox[2] + padding)
            y2 = min(frame.shape[0] - 1, bbox[3] + padding)

            face = frame[y1:y2, x1:x2]

            blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False, crop=False)

            # Predict gender
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]

            # Predict age
            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]

            label = f"{gender}, {age}"
            cv.putText(frameFace, label, (bbox[0], bbox[1] - 10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)

        cv.imshow("Age Gender Demo", frameFace)

        #  print processing time
        print(f"Processing time: {time.time() - t:.3f} sec")


if __name__ == "__main__":
    main()
