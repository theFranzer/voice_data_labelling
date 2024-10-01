import streamlit as st
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from PIL import Image

# Set up directories
IMAGE_DIR = "images"
AUDIO_DIR = "audio_annotations"

# Ensure audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

def load_images(directory):
    """Load all images from a directory."""
    images = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(filename)
    return images

def record_audio(duration, samplerate=44100):
    """Record audio for a specified duration."""
    recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1)
    sd.wait()
    return recording

def save_audio(filename, recording, samplerate=44100):
    """Save the recorded audio to a file."""
    sf.write(filename, recording, samplerate)

def main():
    st.title("Image Annotation App")

    # Load images
    images = load_images(IMAGE_DIR)
    if not images:
        st.error("No images found in the specified directory.")
        return

    # Image selection
    selected_image = st.selectbox("Select an image to annotate:", images)
    
    # Display selected image
    image_path = os.path.join(IMAGE_DIR, selected_image)
    st.image(Image.open(image_path), caption=selected_image)

    # Audio recording
    audio_filename = os.path.splitext(selected_image)[0] + ".wav"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)

    if st.button("Start Recording"):
        st.write("Recording... Speak now!")
        duration = 5  # Recording duration in seconds
        recording = record_audio(duration)
        
        if st.button("Stop Recording"):
            save_audio(audio_path, recording)
            st.success(f"Audio saved as {audio_filename}")

    # Play back the recorded audio if it exists
    if os.path.exists(audio_path):
        st.audio(audio_path)

if __name__ == "__main__":
    main()