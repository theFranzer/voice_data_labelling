import streamlit as st
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from PIL import Image
import tempfile
import queue

# Set up directories
IMAGE_DIR = "images"
AUDIO_DIR = "audio_annotations"

# Ensure audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# Global variables for audio recording
audio_data = queue.Queue()
recording = False

def load_images(directory):
    """Load all images from a directory."""
    images = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            images.append(filename)
    return images

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    audio_data.put(indata.copy())

def save_audio(filename, data, samplerate=44100):
    """Save the recorded audio to a file."""
    sf.write(filename, data, samplerate)

# Streamlit app
st.title("Image Annotation App")

# Load images
images = load_images(IMAGE_DIR)
if not images:
    st.error("No images found in the specified directory.")
    st.stop()

# Image selection
selected_image = st.selectbox("Select an image to annotate:", images)

# Display selected image
image_path = os.path.join(IMAGE_DIR, selected_image)
st.image(Image.open(image_path), caption=selected_image)

# Audio recording
audio_filename = os.path.splitext(selected_image)[0] + ".wav"
audio_path = os.path.join(AUDIO_DIR, audio_filename)

# Use columns for button layout
col1, col2 = st.columns(2)

with col1:
    start_button = st.button("Start Recording")

with col2:
    stop_button = st.button("Stop Recording")

if start_button:
    recording = True
    audio_data = queue.Queue()
    st.warning("Recording... Press 'Stop Recording' when finished.")
    
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
        while recording:
            if stop_button:
                recording = False
                break
            st.empty()  # This allows the app to update and check the stop button

if stop_button and not audio_data.empty():
    recording = False
    st.info("Processing and saving the audio...")
    
    # Combine all audio data
    audio = np.concatenate([audio_data.get() for _ in range(audio_data.qsize())])
    
    # Save the audio
    save_audio(audio_path, audio)
    st.success(f"Audio saved as {audio_filename}")

# Play back the recorded audio if it exists
if os.path.exists(audio_path):
    st.audio(audio_path)