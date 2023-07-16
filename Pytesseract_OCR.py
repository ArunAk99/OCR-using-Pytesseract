import cv2
import pytesseract
from tkinter import Tk, Button, filedialog
import json

# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize variables
bboxes = []
output_texts = []

# Create a function to handle mouse events
def draw_bbox(event, x, y, flags, param):
    global bboxes
    image = param["image"]  # Get the image from the parameter dictionary
    if event == cv2.EVENT_LBUTTONDOWN:
        bboxes.append([(x, y)])
    elif event == cv2.EVENT_LBUTTONUP:
        bboxes[-1].append((x, y))
        cv2.rectangle(image, bboxes[-1][0], bboxes[-1][1], (0, 255, 0), 2)
        cv2.imshow("Image", image)

# Create a function to handle image upload and processing
def upload_and_process_image():
    global bboxes, output_texts

    # Open a file dialog for image selection
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        # Read the image
        image = cv2.imread(file_path)
        clone = image.copy()
        bboxes = []
        output_texts = []

        # Create a window and bind the function to the window
        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", draw_bbox, {"image": image})  # Pass the image as a parameter

        # Display the image
        cv2.imshow("Image", image)

        # Wait for the user to draw the bounding boxes
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("r"):
                image = clone.copy()
                bboxes = []
                cv2.imshow("Image", image)
            elif key == ord("c"):
                break

        # Perform OCR on the bounding box images
        for i, bbox in enumerate(bboxes):
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            cropped_image = clone[y1:y2, x1:x2]

            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(cropped_image)

            # Store the extracted text
            output_texts.append(text)

            # Draw a rectangle around the text region
            cv2.rectangle(image, bbox[0], bbox[1], (0, 255, 0), 2)

            # Display the image with text regions highlighted
            cv2.imshow("Image", image)
            cv2.waitKey(0)

        # Save the text outputs to a text file
        save_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if save_path:
            with open(save_path, "a") as file:  # Append to the file instead of overwriting
                file.write(f"Image: {file_path}\n")  # Write the image name
                for i, text in enumerate(output_texts):
                    file.write(f"Text {i + 1}: {text}\n")
                file.write("\n")  # Add a separator between images
            print("Text outputs saved successfully.")

        # Save the text outputs to a JSON file
        json_save_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile="results.json")
        if json_save_path:
            results = {
                "image": file_path,
                "text": output_texts
            }
            with open(json_save_path, "a") as json_file:
                json.dump(results, json_file)
            print("JSON results saved successfully.")

# Create the main UI window
window = Tk()

# Create an "Upload and Process Image" button
upload_button = Button(window, text="Upload and Process Image", command=upload_and_process_image)
upload_button.pack()

# Run the UI window
window.mainloop()
