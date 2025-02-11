import cv2
import mediapipe as mp

# Initialize MediaPipe Object Detection.
mp_object_detection = mp.solutions.object_detection
object_detection = mp_object_detection.ObjectDetection(
    model_path="efficientdet_lite2.tflite",  # Path to your custom model if you have one
    min_detection_confidence=0.5
)

# Initialize the drawing utility for annotating the image.
mp_drawing = mp.solutions.drawing_utils

# Open a video file or capture device.
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB.
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and detect objects.
    results = object_detection.process(rgb_frame)

    # Draw the object detection annotations on the image.
    if results.detections:
        for detection in results.detections:
            mp_drawing.draw_detection(frame, detection)

    # Display the resulting frame.
    cv2.imshow('Object Detection', frame)

    # Break the loop on 'q' key press.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any OpenCV windows.
cap.release()
cv2.destroyAllWindows()
