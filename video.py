import cv2
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processor")

        self.file_path = ""
        self.box_color = (0, 0, 0)

        self.create_widgets()

    def create_widgets(self):
        self.open_button = tk.Button(self.root, text="Open Video File", command=self.open_file)
        self.open_button.pack(pady=10)

        self.color_button = tk.Button(self.root, text="Choose Box Color", command=self.choose_color)
        self.color_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Processing", command=self.start_processing)
        self.start_button.pack(pady=10)

        self.process_button = tk.Button(self.root, text="Save Video", command=self.save_video, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Return>', lambda event: self.start_button.invoke() if self.file_path else None)

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if self.file_path:
            print(f"Selected file: {self.file_path}")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Box Color")
        if color[1]:
            self.box_color = tuple(int(x) for x in color[0])
            print(f"Selected color: {self.box_color}")

    def start_processing(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a video file first.")
            return

        self.cap = cv2.VideoCapture(self.file_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open the video.")
            return

        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))

        self.process_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.root.bind('<Return>', lambda event: self.process_button.invoke())
        messagebox.showinfo("Info", "Video processing started. Press 'Save Video' to save the processed video.")

    def save_video(self):
        if not hasattr(self, 'cap'):
            messagebox.showwarning("Warning", "Please start processing first.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension="", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if not output_path:
            return

        out = cv2.VideoWriter(output_path, self.codec, self.fps, (self.frame_width, self.frame_height))

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.detections:
                    for detection in results.detections:
                        bounding_box = detection.location_data.relative_bounding_box
                        x, y = int(bounding_box.xmin * image.shape[1]), int(bounding_box.ymin * image.shape[0])
                        w, h = int(bounding_box.width * image.shape[1]), int(bounding_box.height * image.shape[0])
                        cv2.rectangle(image, (x, y), (x+w, y+h), self.box_color, -1)

                out.write(image)

        self.cap.release()
        out.release()
        print(f"Processed video saved as {output_path}")
        messagebox.showinfo("Info", f"Processed video saved as {output_path}")

        self.process_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.root.bind('<Return>', lambda event: self.start_button.invoke() if self.file_path else None)

    def on_closing(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()
