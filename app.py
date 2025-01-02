import os
from dataclasses import replace

import moviepy as mp
import speech_recognition as sr
import requests
from flask import Flask, request, render_template, jsonify
from pydub import AudioSegment

app = Flask(__name__)

# Set your API key and endpoint URL
api_key = 'AIzaSyC2kc6gxD_FjynGmZAo5L2xUUqoIIiKQw0'  # Replace with your actual API key
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'

import glob


def delete_images_from_directory(directory_path):
    # Define the valid image file extensions
    image_extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif')

    # Loop through all image extensions and delete the images
    for ext in image_extensions:
        # Create the search pattern for the specific extension
        image_files = glob.glob(os.path.join(directory_path, ext))

        # Delete each image file found
        for image in image_files:
            try:
                os.remove(image)
                print(f"Deleted: {image}")
            except Exception as e:
                print(f"Error deleting {image}: {e}")


# Function to extract audio from a video file
def extract_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)



# Function to transcribe audio to text using ASR
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_path)

    # Split the audio into 30-second chunks
    chunk_length_ms = 30000  # 30 seconds
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    full_transcription = ""

    for i, chunk in enumerate(chunks):
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")  # Export the chunk as a WAV file

        with sr.AudioFile(chunk_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
            full_transcription += text + " "
        except sr.UnknownValueError:
            print(f"Chunk {i}: Could not understand audio")
        except sr.RequestError as e:
            return f"Chunk {i}: Could not request results from Google Speech Recognition service; {e}"

        os.remove(chunk_path)  # Clean up the chunk file
        print(full_transcription.strip())
    return full_transcription.strip()


def generate_content(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {'contents': [{'parts': [{'text': prompt}]}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        generated_json = response.json()
        candidates = generated_json.get('candidates', [])
        if candidates:
            parts = candidates[0].get('content', {}).get('parts', [])
            if parts:
                text = parts[0].get('text', 'No text generated.')
                return text
        return 'No text generated.'
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"


# Main function to summarize the video
def summarize_video(video_path, num_paragraphs):
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    transcribed_text = transcribe_audio(audio_path)
    if transcribed_text=="":
        output= "Video Does Not Contains Audio"  # Return error message if transcription fails
        transcribed_text= "Video Does Not Contains Audio"  # Return error message if transcription fails
    else:
        prompt = f"'{transcribed_text}',give a summary in short and minimum words in {num_paragraphs} paragraph which is of 5 9 lines"
        output = generate_content(prompt)

    # Clean up temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)
    print(output)
    return output,transcribed_text

import cv2
import pytesseract
from skimage.metrics import structural_similarity as ssim
import numpy as np
import os

# Set up Tesseract path if necessary (on Windows systems)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def has_text(frame):
    """Check if a frame contains text using OCR."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_frame, config='--psm 6')  # Config for block text detection
    return len(text.strip()) > 0

def are_frames_different(frame1, frame2, threshold=0.9):
    """Compare two frames and determine if they are significantly different."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score < threshold

def extract_text_frames(video_path, output_dir, threshold=0.9, interval=5):
    """Extract unique frames with text from a video, checking every `interval` seconds."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = int(fps * interval)  # Number of frames to skip based on the interval

    prev_frame = None
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Process every `frame_skip` frame
        if frame_count % frame_skip == 0:
            # Check if the frame contains text
            if has_text(frame):
                if prev_frame is None or are_frames_different(frame, prev_frame, threshold):
                    # Save the frame if it's significantly different
                    frame_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
                    cv2.imwrite(frame_path, frame)
                    saved_count += 1
                    prev_frame = frame

    cap.release()
    print(f"Saved {saved_count} unique frames with text to '{output_dir}'.")

# Example usage



# Route for uploading video
@app.route('/', methods=['GET', 'POST'])
def upload_video():
    output_dir='static/output_images'
    delete_images_from_directory(output_dir)
    if request.method == 'POST':
        video_file = request.files['video']
        num_paragraphs = request.form.get('num_paragraphs', default=1, type=int)
        if video_file:
            video_path = os.path.join('static', video_file.filename)
            video_file.save(video_path)
            result ,transcribed_text= summarize_video(video_path, num_paragraphs)
            extract_text_frames(video_path, output_dir, interval=5)
            return render_template('index.html', result=result,transcribed_text=transcribed_text,output_dir=output_dir)

    return render_template('index.html', result=None)


@app.route('/process', methods=['POST'])
def process_video():
    output_dir = 'static/output_images'
    if request.method == 'POST':
        video_file = request.files.get('video')
        num_paragraphs = request.form.get('num_paragraphs', default=1, type=int)

        if video_file:
            video_path = os.path.join('static', video_file.filename)
            video_file.save(video_path)
            result, transcribed_text = summarize_video(video_path, num_paragraphs)
            extract_text_frames(video_path, output_dir, interval=5)
            image_files = [f'{output_dir}/{file}' for file in os.listdir(output_dir) if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
            return jsonify({
                'result': result,
                'transcribed_text': transcribed_text,
                'img_dir':image_files
            })

    return jsonify({'error': 'No file uploaded'}), 400


if __name__ == "__main__":
    app.run(debug=True)
