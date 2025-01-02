import os
import moviepy as mp
import speech_recognition as sr
import requests
from flask import Flask, request, render_template
from pydub import AudioSegment

app = Flask(__name__)

# Set your API key and endpoint URL
api_key = 'AIzaSyC2kc6gxD_FjynGmZAo5L2xUUqoIIiKQw0'  # Replace with your actual API key
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'


# Function to extract audio from a video file
def extract_audio(video_path, audio_path):
    video = mp.editor.VideoFileClip(video_path)
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
                return parts[0].get('text', 'No text generated.')
        return 'No text generated.'
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"


# Main function to summarize the video
def summarize_video(video_path):
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)

    transcribed_text = transcribe_audio(audio_path)
    if "Could not" in transcribed_text:
        return transcribed_text  # Return error message if transcription fails

    prompt = f"'{transcribed_text}', consider this as a video transcript and give output as the summary in a way that it is spoken by a third person in short that can be read in under 30 to 40 secondes."
    output = generate_content(prompt)

    # Clean up temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return transcribed_text, output


# Route for uploading video
@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        video_file = request.files['video']
        if video_file:
            video_path = os.path.join('static', video_file.filename)
            video_file.save(video_path)
            result = summarize_video(video_path)
            return render_template('inde.html', result=result)

    return render_template('inde.html', result=None)


if __name__ == "__main__":
    app.run(debug=True)
