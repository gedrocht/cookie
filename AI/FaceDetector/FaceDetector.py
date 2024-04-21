import cv2
from deepface import DeepFace

# Start capturing video from the webcam
cap = cv2.VideoCapture(1)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        break

    # Analyzing the frame for facial expression
    try:
        result = DeepFace.analyze(frame, actions=['emotion'])
        emotion = str(result[0]['emotion']['neutral'])

        # Display the resulting frame with detected emotion
        cv2.putText(frame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    except Exception as e:
        print(e)

    cv2.imshow('Facial Expression Detection', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
