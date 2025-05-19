In order to run the code, please download these 2 models beforehand.

## Download Model
[Click here to download the model]-https://drive.google.com/file/d/1-NulrhEUi2MN3PPnLZ5cdzjYtUIpKZMg/view?usp=sharing

## Download Model
[Click here to download the model]-https://drive.google.com/file/d/1GpBXhPNHpyL-RWaulUAu81YCvlkK2prm/view?usp=sharing

AGE AND GENDER PREDICTION MODEL

This project uses OpenCV's **Deep Neural Network (DNN)** module to detect faces in real-time from webcam or video/image input and predict the age and gender of each detected face.

Features
Real-time face detection using OpenCV DNN.

Age and gender prediction using pre-trained Caffe models.

Automatically detects whether a face is present and shows a message if not.

Supports webcam or video/image file input.

Demo
When a face is detected, the application displays:

Predicted gender (Male or Female)

Predicted age range (e.g., (25-32))

If no face is visible, the message "Face is not visible" is displayed.

Requirements
Python 3.6 or higher

OpenCV (with dnn module)

Installation
Clone this repository:

bash
Copy
Edit
git clone https://github.com/yourusername/age-gender-detection.git
cd age-gender-detection
Install dependencies:

nginx
Copy
Edit
pip install opencv-python
Download the required model files and place them in the project directory:

opencv_face_detector.pbtxt

opencv_face_detector_uint8.pb

age_deploy.prototxt

age_net.caffemodel

gender_deploy.prototxt

gender_net.caffemodel

Model files can be found from the OpenCV GitHub or model zoo.

Usage
To run with webcam:

nginx
Copy
Edit
python age_gender_demo.py
To run on a video or image file:

css
Copy
Edit
python age_gender_demo.py --input path/to/your/video_or_image
Notes
The model may not be 100% accurate; it gives an estimation based on facial features.

For best results, use clear and front-facing face images.
