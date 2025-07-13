
import streamlit as st
import os
import whisper
import subprocess
import shutil
from typing import Optional

# Set the title of the web application
st.title("YouTube Video Transcription App")

# Create a text input field for the YouTube URL
youtube_url = st.text_input("Enter YouTube URL:")

# Placeholder for displaying the transcription result and progress
transcription_output = st.empty()

def transcribe_youtube_video(url: str, output_dir: str = "downloads") -> Optional[str]:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio_filename = "downloaded_audio.mp3"
    audio_path = os.path.join(output_dir, audio_filename)

    try:
        st.info("Downloading audio...")
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", audio_path,
            "--no-warnings",
            "--quiet",
            url
        ], check=True)
        st.info("Audio downloaded. Transcribing...")
    except subprocess.CalledProcessError as e:
        st.error(f"Audio download failed: {e}")
        return None
    except FileNotFoundError:
        st.error("yt-dlp command not found. Is yt-dlp installed and in your PATH?")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during download: {e}")
        return None

    transcription = None
    model_to_use = "medium"
    if os.path.exists(audio_path):
        try:
            model = whisper.load_model(model_to_use)
            result = model.transcribe(audio_path)
            transcription = result["text"]
            st.info("Transcription complete.")
        except ImportError:
            st.error("whisper-openai model not installed or import failed.")
        except Exception as e:
            st.error(f"Transcription failed: {e}")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
    else:
        st.error(f"Downloaded audio file not found at {audio_path}.")

    return transcription

if st.button("Transcribe"):
    if youtube_url:
        transcription_output.empty()
        try:
            with st.spinner("Processing..."):
                 transcribed_text = transcribe_youtube_video(youtube_url)
            if transcribed_text:
                st.subheader("Transcription:")
                st.write(transcribed_text)
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
    else:
        st.warning("https://www.youtube.com/shorts/IiCAZbx8_zA")
