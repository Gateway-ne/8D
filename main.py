import os
from pydub import AudioSegment
import numpy as np


def apply_8d_effect(input_file, output_file, rotation_speed=0.5):
    # Load audio
    song = AudioSegment.from_file(input_file, format="m4a")

    # Convert to raw samples
    samples = np.array(song.get_array_of_samples())
    channels = song.channels
    sample_rate = song.frame_rate

    # Reshape for stereo
    samples = samples.reshape((-1, channels))

    # Create panning effect
    duration = len(samples) / sample_rate
    t = np.linspace(0, duration, num=len(samples))
    pan = np.sin(2 * np.pi * rotation_speed * t)  # oscillates between -1 and 1

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
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all mp3 files in input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".m4a"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, f"{file_name}")
            print(f"Converting {file_name} -> {output_path}")
            apply_8d_effect(input_path, output_path, rotation_speed)


if __name__ == "__main__":
    # Ask user for input/output folders
    input_folder = input("Enter the path to your input folder: ").strip()
    output_folder = input("Enter the path to your output folder: ").strip()

    convert_folder(input_folder, output_folder, rotation_speed=0.5)
    print("✅ Conversion complete! All MP3s have been processed.")
