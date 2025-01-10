import cv2

# Check OpenCV version
print("OpenCV version:", cv2.__version__)

# Verify if face module is available
if hasattr(cv2, 'face'):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("LBPH Face Recognizer created successfully")
else:
    print("cv2.face module is not available")
