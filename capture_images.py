import cv2
import os

def capture_images(person_name, num_images=5, save_dir="known_faces"):
    # Create a folder for the person
    person_path = os.path.join(save_dir, person_name)
    os.makedirs(person_path, exist_ok=True)

    cap = cv2.VideoCapture(0)  # Open webcam

    count = 0
    print(f"[INFO] Capturing {num_images} images of {person_name}...")
    print("[INFO] Look at the camera and press SPACE to capture, Q to quit.")

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Capture Images", frame)

        key = cv2.waitKey(1)

        if key == 32:  # SPACE key
            img_path = os.path.join(person_path, f"{count+1}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"[SAVED] {img_path}")
            count += 1

        elif key == ord("q"):  # Quit early
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[DONE] Image capture complete.")

if __name__ == "__main__":
    name = input("Enter the person's name: ").strip().lower()
    capture_images(name, num_images=5)
