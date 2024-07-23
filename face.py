import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection

# Load the image/video
cap = cv2.VideoCapture(0)  # 0 for webcam

with mp_face_detection.FaceDetection(
    model_selection=0,  # 0 for faster, 1 for more accurate
    min_detection_confidence=0.5) as face_detection:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Convert the BGR image to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image
        results = face_detection.process(image)

        # Convert the image back to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw the face detection annotations on the image
        if results.detections:
            for detection in results.detections:
                # Get the bounding box coordinates
                bounding_box = detection.location_data.relative_bounding_box
                x, y = int(bounding_box.xmin * image.shape[1]), int(bounding_box.ymin * image.shape[0])
                w, h = int(bounding_box.width * image.shape[1]), int(bounding_box.height * image.shape[0])

                # Draw a black square over the face
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 0), -1)
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 0), 18)

        # Display the image
        cv2.imshow('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%', image)
        if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
            break
cap.release()
cv2.destroyAllWindows()
