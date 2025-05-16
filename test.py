# Import required modules
import cv2 as cv
import time
import argparse
from collections import deque

def getFaceBox(net, frame, conf_threshold=0.8):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

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
            cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
    return frameOpencvDnn, bboxes

parser = argparse.ArgumentParser(description='Use this script to run age and gender recognition using OpenCV.')
parser.add_argument('--input', help='Path to input image or video file. Skip this argument to capture frames from a camera.')

args = parser.parse_args()

faceProto = "opencv_face_detector.pbtxt"
faceModel = "opencv_face_detector_uint8.pb"

ageProto = "age_deploy.prototxt"
ageModel = "age_net.caffemodel"

genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

# Load network
ageNet = cv.dnn.readNet(ageModel, ageProto)
genderNet = cv.dnn.readNet(genderModel, genderProto)
faceNet = cv.dnn.readNet(faceModel, faceProto)

# Open a video file or an image file or a camera stream
cap = cv.VideoCapture(args.input if args.input else 0)
padding = 20

# Smoothing history for predictions
gender_history = deque(maxlen=10)
age_history = deque(maxlen=10)

frame_count = 0
while True:
    # Read frame
    hasFrame, frame = cap.read()
    if not hasFrame:
        print("No frames grabbed! Exiting...")
        break

    frame_count += 1

    # Skip every 3rd frame for performance
    if frame_count % 3 != 0:
        continue

    frameFace, bboxes = getFaceBox(faceNet, frame)

    if bboxes:
        for bbox in bboxes:
            # Ensure the bounding box is within the frame's boundaries
            x1, y1, x2, y2 = bbox
            x1 = max(x1, 0)
            y1 = max(y1, 0)
            x2 = min(x2, frame.shape[1] - 1)
            y2 = min(y2, frame.shape[0] - 1)

            # Extract the face ROI
            face = frame[y1:y2, x1:x2]
            
            # Check if the face region is valid (not empty)
            if face.size == 0:
                continue  # Skip if face region is empty

            # Preprocess face
            face = cv.GaussianBlur(face, (3, 3), 0)  # Reduce noise

            # Predict gender
            blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            gender_history.append(gender)

            # Predict age
            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            age_history.append(age)

            # Smooth predictions
            gender = max(set(gender_history), key=gender_history.count)
            age = max(set(age_history), key=age_history.count)

            # Add label to frame
            label = f"{gender}, {age}"
            cv.putText(frameFace, label, (bbox[0], bbox[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv.LINE_AA)
    else:
        # Display a message when no face is detected
        message = "Please align your face in front of the camera."
        font = cv.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 0, 255)  # Red color
        thickness = 2
        text_size = cv.getTextSize(message, font, font_scale, thickness)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2
        cv.putText(frame, message, (text_x, text_y), font, font_scale, color, thickness, cv.LINE_AA)

    # Display the frame
    cv.imshow("Age Gender Demo", frameFace if bboxes else frame)

    # Exit if the user presses 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

print("Processing finished.")
cap.release()
cv.destroyAllWindows()
