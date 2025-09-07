#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import sys
import threading

import openai
import requests


def process_and_send(input_file, output_file):
    """Extract audio, transcribe, and send via POST"""
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-q:a", "0",
        "-map", "a",
        output_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(output_file, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create( file=audio_file, model="whisper-1")
    text = transcript.text
    print("Transcription result:", text)
    return text
 

class SimplePOSTHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        input_file = "processing.mp4"
        output_file = "output.mp3"
        with open(input_file, "wb") as f:
            f.write(post_data)
        print(f"Saved POST data to {input_file}")
        text = process_and_send(input_file, output_file)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text)


def main():
    with open("openaikey.txt") as f:
        openai.api_key = f.read().strip()
    host, port = "localhost", 8052
    server = HTTPServer((host, port), SimplePOSTHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
