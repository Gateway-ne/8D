import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

SUPPORTED_FORMATS = (".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a")

def apply_8d_effect(input_file, output_file, rotation_speed=0.5):
    song = AudioSegment.from_file(input_file)
    samples = np.array(song.get_array_of_samples())
    channels = song.channels
    sample_rate = song.frame_rate

    if channels < 2:
        print(f"⚠️ Skipping {input_file}: not stereo")
        return None

    samples = samples.reshape((-1, channels))
    duration = len(samples) / sample_rate
    t = np.linspace(0, duration, num=len(samples))
    pan = np.sin(2 * np.pi * rotation_speed * t)

    left = (1 - pan) / 2
    right = (1 + pan) / 2

    samples[:, 0] = (samples[:, 0] * left).astype(np.int16)
    samples[:, 1] = (samples[:, 1] * right).astype(np.int16)

    new_song = AudioSegment(
        samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=song.sample_width,
        channels=channels
    )

    base_name = os.path.splitext(os.path.basename(output_file))[0]
    output_mp3 = os.path.join(os.path.dirname(output_file), f"{base_name}_8d.mp3")
    new_song.export(output_mp3, format="mp3")
    return output_mp3

@app.route("/", methods=["GET", "POST"])
def index():
    converted_files = []
    if request.method == "POST":
        input_folder = request.form.get("input_folder").strip()
        output_folder = request.form.get("output_folder").strip()
        rotation_speed = float(request.form.get("rotation_speed", 0.5))

        if not os.path.isdir(input_folder):
            flash("❌ Input folder does not exist.")
            return redirect(url_for("index"))

        os.makedirs(output_folder, exist_ok=True)

        for file_name in os.listdir(input_folder):
            if file_name.lower().endswith(SUPPORTED_FORMATS):
                input_path = os.path.join(input_folder, file_name)
                output_path = os.path.join(output_folder, file_name)
                try:
                    result = apply_8d_effect(input_path, output_path, rotation_speed)
                    if result:
                        converted_files.append(os.path.basename(result))
                except Exception as e:
                    flash(f"❌ Skipping {file_name}: {e}")

        flash(f"✅ Conversion complete! {len(converted_files)} files processed.")
        return render_template("index.html", converted_files=converted_files)

    return render_template("index.html", converted_files=converted_files)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
