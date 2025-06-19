## AGE AND GENDER PREDICTION MODEL

This project uses OpenCV's **Deep Neural Network (DNN)** module to detect faces in real-time from webcam or video/image input and predict the age and gender of each detected face.

## Features
Real-time face detection using OpenCV DNN.

Age and gender prediction using pre-trained Caffe models.

Automatically detects whether a face is present and shows a message if not.

Supports webcam or video/image file input.

## Installation

Install dependencies:

pip install opencv-python

Download the required model files and place them in the project directory:

opencv_face_detector.pbtxt

opencv_face_detector_uint8.pb

age_deploy.prototxt

gender_deploy.prototxt

gender_net.caffemodel - https://drive.google.com/file/d/1GpBXhPNHpyL-RWaulUAu81YCvlkK2prm/view?usp=sharing

age_net.caffemodel - https://drive.google.com/file/d/1-NulrhEUi2MN3PPnLZ5cdzjYtUIpKZMg/view?usp=sharing

After downloading the repo, please use these commands:
npm install - (To Install frontend dependencies)
npm start - (To run the frontend)
python app.py - (To run the backend)

The model may not be 100% accurate; it gives an estimation based on facial features.

For best results, use clear and front-facing face images.
