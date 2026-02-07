import os
import numpy as np
from pydub import AudioSegment

# List of supported audio formats
SUPPORTED_FORMATS = (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a")

def apply_8d_effect(input_file, output_file, rotation_speed=0.5):
    # Load audio (pydub auto-detects format via FFmpeg)
    song = AudioSegment.from_file(input_file)

    # Convert to raw samples
    samples = np.array(song.get_array_of_samples())
    channels = song.channels
    sample_rate = song.frame_rate

    # Skip mono files (8D effect needs stereo)
    if channels < 2:
        print(f"⚠️ Skipping {input_file}: not stereo")
        return

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

    # Always export to MP3 (safe and widely supported)
    base_name = os.path.splitext(os.path.basename(output_file))[0]
    output_mp3 = os.path.join(os.path.dirname(output_file), f"{base_name}.mp3")
    new_song.export(output_mp3, format="mp3")
    print(f"✅ Exported {output_mp3}")

def convert_folder(input_folder, output_folder, rotation_speed=0.5):
    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(SUPPORTED_FORMATS):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            try:
                print(f"Converting {file_name} -> {output_folder}")
                apply_8d_effect(input_path, output_path, rotation_speed)
            except Exception as e:
                print(f"❌ Skipping {file_name}: {e}")

if __name__ == "__main__":
    input_folder = input("Enter the path to your input folder: ").strip().strip('"')
    output_folder = input("Enter the path to your output folder: ").strip().strip('"')

    convert_folder(input_folder, output_folder, rotation_speed=0.5)
    print("🎶 Conversion complete! All supported audio files have been processed into MP3.")
