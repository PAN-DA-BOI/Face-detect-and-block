import cv2
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import os
import mediapipe as mp
from pydub import AudioSegment
from pydub.playback import play

mp_fd = mp.solutions.face_detection

class MultiTabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Tab App")
        self.root.geometry("350x400")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.video_tab = ttk.Frame(self.notebook)
        self.audio_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.video_tab, text='Video Processor')
        self.notebook.add(self.audio_tab, text='Audio Manipulation')

        self.init_video_tab()
        self.init_audio_tab()

    def init_video_tab(self):
        self.fp = ""
        self.fop = ""
        self.bc = (0, 0, 0)
        self.bs = tk.IntVar(value=55)
        self.m = tk.StringVar(value="Box")

        self.ob = tk.Button(self.video_tab, text="Open Video File", command=self.of)
        self.ob.pack(pady=10)

        self.ofb = tk.Button(self.video_tab, text="Open Folder", command=self.ofd)
        self.ofb.pack(pady=10)

        self.ml = tk.Label(self.video_tab, text="Select Mode:")
        self.ml.pack(pady=5)

        self.mb = tk.Radiobutton(self.video_tab, text="Box", variable=self.m, value="Box")
        self.mb.pack(anchor=tk.W)

        self.mbl = tk.Radiobutton(self.video_tab, text="Blur", variable=self.m, value="Blur")
        self.mbl.pack(anchor=tk.W)

        self.bl = tk.Label(self.video_tab, text="Blur Strength (odd values only):")
        self.bl.pack(pady=5)

        self.be = tk.Entry(self.video_tab, textvariable=self.bs)
        self.be.pack(pady=5)

        self.sb = tk.Button(self.video_tab, text="Start Processing", command=self.sp)
        self.sb.pack(pady=10)

        self.pb = tk.Button(self.video_tab, text="Save Video", command=self.sv, state=tk.DISABLED)
        self.pb.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.oc)
        self.root.bind('<Return>', lambda event: self.sb.invoke() if self.fp or self.fop else None)

    def init_audio_tab(self):
        self.afp = ""

        self.aob = tk.Button(self.audio_tab, text="Open Audio File", command=self.ao)
        self.aob.pack(pady=10)

        self.pitch_label = tk.Label(self.audio_tab, text="Pitch Shift (semitones):")
        self.pitch_label.pack(pady=5)

        self.pitch_var = tk.IntVar(value=0)
        self.pitch_entry = tk.Entry(self.audio_tab, textvariable=self.pitch_var)
        self.pitch_entry.pack(pady=5)

        self.apply_button = tk.Button(self.audio_tab, text="Apply Voice Changer", command=self.avc)
        self.apply_button.pack(pady=10)

        self.play_button = tk.Button(self.audio_tab, text="Play Audio", command=self.pa, state=tk.DISABLED)
        self.play_button.pack(pady=10)

        self.save_button = tk.Button(self.audio_tab, text="Save Audio", command=self.sa, state=tk.DISABLED)
        self.save_button.pack(pady=10)

    def of(self):
        self.fp = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if self.fp:
            print(f"Selected file: {self.fp}")
            self.fop = ""

    def ofd(self):
        self.fop = filedialog.askdirectory()
        if self.fop:
            print(f"Selected folder: {self.fop}")
            self.fp = ""

    def sp(self):
        if not self.fp and not self.fop:
            messagebox.showwarning("Warning", "Please select a video file or folder first.")
            return

        if self.m.get() == "Box":
            self.cc()

        if self.fp:
            self.psv(self.fp)
        elif self.fop:
            self.pfv(self.fop)

        self.pb.config(state=tk.NORMAL)
        self.sb.config(state=tk.DISABLED)
        self.root.bind('<Return>', lambda event: self.pb.invoke())
        messagebox.showinfo("Info", "Video processing started. Press 'Save Video' to save the processed video(s).")

    def psv(self, fp):
        self.cap = cv2.VideoCapture(fp)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open the video.")
            return

        self.fw = int(self.cap.get(3))
        self.fh = int(self.cap.get(4))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))

    def pfv(self, fop):
        self.vf = [f for f in os.listdir(fop) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        if not self.vf:
            messagebox.showwarning("Warning", "No video files found in the selected folder.")
            return

        self.cvi = 0
        self.pnv()

    def pnv(self):
        if self.cvi < len(self.vf):
            vf = self.vf[self.cvi]
            fp = os.path.join(self.fop, vf)
            self.psv(fp)
            self.cvi += 1
        else:
            messagebox.showinfo("Info", "All videos in the folder have been processed.")
            self.pb.config(state=tk.DISABLED)
            self.sb.config(state=tk.NORMAL)
            self.root.bind('<Return>', lambda event: self.sb.invoke() if self.fp or self.fop else None)

    def cc(self):
        c = colorchooser.askcolor(title="Choose Box Color")
        if c[1]:
            self.bc = tuple(int(x) for x in c[0])
            print(f"Selected color: {self.bc}")

    def sv(self):
        if not hasattr(self, 'cap'):
            messagebox.showwarning("Warning", "Please start processing first.")
            return

        op = filedialog.asksaveasfilename(defaultextension="", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if not op:
            return

        out = cv2.VideoWriter(op, self.codec, self.fps, (self.fw, self.fh))

        with mp_fd.FaceDetection(model_selection=0, min_detection_confidence=0.5) as fd:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = fd.process(img)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                if res.detections:
                    for det in res.detections:
                        bb = det.location_data.relative_bounding_box
                        x, y = int(bb.xmin * img.shape[1]), int(bb.ymin * img.shape[0])
                        w, h = int(bb.width * img.shape[1]), int(bb.height * img.shape[0])

                        if self.m.get() == "Box":
                            cv2.rectangle(img, (x, y), (x+w, y+h), self.bc, -1)
                        elif self.m.get() == "Blur":
                            fr = img[y:y+h, x:x+w]
                            bf = cv2.GaussianBlur(fr, (self.bs.get(), self.bs.get()), 30)
                            img[y:y+h, x:x+w] = bf

                out.write(img)

        self.cap.release()
        out.release()
        print(f"Processed video saved as {op}")
        messagebox.showinfo("Info", f"Processed video saved as {op}")

        if self.fop:
            self.pnv()

    def oc(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

    def ao(self):
        self.afp = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if self.afp:
            print(f"Selected audio file: {self.afp}")
            self.play_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

    def avc(self):
        if not self.afp:
            messagebox.showwarning("Warning", "Please select an audio file first.")
            return

        audio = AudioSegment.from_file(self.afp)
        shift = self.pitch_var.get()

        # Apply pitch shift
        shifted_audio = audio.set_frame_rate(int(audio.frame_rate * (2 ** (shift / 12.0))))
        self.modified_audio = shifted_audio
        messagebox.showinfo("Info", "Voice changer applied.")

    def pa(self):
        if hasattr(self, 'modified_audio'):
            play(self.modified_audio)
        elif self.afp:
            audio = AudioSegment.from_file(self.afp)
            play(audio)

    def sa(self):
        if not hasattr(self, 'modified_audio'):
            messagebox.showwarning("Warning", "Please apply voice changer first.")
            return

        op = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Audio Files", "*.wav")])
        if not op:
            return

        self.modified_audio.export(op, format="wav")
        print(f"Modified audio saved as {op}")
        messagebox.showinfo("Info", f"Modified audio saved as {op}")

if __name__ == "__main__":
    rt = tk.Tk()
    app = MultiTabApp(rt)
    rt.mainloop()
