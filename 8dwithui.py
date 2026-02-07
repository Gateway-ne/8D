import os
import numpy as np
from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, messagebox

def apply_8d_effect(input_file, output_file, rotation_speed=0.5):
    # Load audio
    song = AudioSegment.from_file(input_file, format="mp3")

    # Convert to raw samples
    samples = np.array(song.get_array_of_samples())
    channels = song.channels
    sample_rate = song.frame_rate

    # Reshape for stereo
    samples = samples.reshape((-1, channels))

    # Create panning effect
    duration = len(samples) / sample_rate
    t = np.linspace(0, duration, num=len(samples))
    pan = np.sin(2 * np.pi * rotation_speed * t)

    left = (1 - pan) / 2
    right = (1 + pan) / 2

    samples[:, 0] = (samples[:, 0] * left).astype(np.int16)
    samples[:, 1] = (samples[:, 1] * right).astype(np.int16)

    # Rebuild audio
    new_song = AudioSegment(
        samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=song.sample_width,
        channels=channels
    )

    # Export
    new_song.export(output_file, format="mp3")

def convert_folder(input_folder, output_folder, rotation_speed=0.5):
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".mp3"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, f"{file_name}")
            print(f"Converting {file_name} -> {output_path}")
            apply_8d_effect(input_path, output_path, rotation_speed)

def start_conversion():
    input_folder = input_path.get()
    output_folder = output_path.get()
    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output folders.")
        return
    try:
        convert_folder(input_folder, output_folder, rotation_speed=0.5)
        messagebox.showinfo("Success", "✅ Conversion complete! All MP3s have been processed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_path.set(folder)

def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)

# Tkinter UI
root = tk.Tk()
root.title("8D Audio Converter")

input_path = tk.StringVar()
output_path = tk.StringVar()

tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_path, width=40).grid(row=0, column=1, padx=10)
tk.Button(root, text="Browse", command=browse_input).grid(row=0, column=2, padx=10)

tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=output_path, width=40).grid(row=1, column=1, padx=10)
tk.Button(root, text="Browse", command=browse_output).grid(row=1, column=2, padx=10)

tk.Button(root, text="Convert", command=start_conversion, bg="green", fg="white").grid(row=2, column=1, pady=20)

root.mainloop()
