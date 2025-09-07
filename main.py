#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
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
    print("Transcribing")
    with open(output_file, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create( file=audio_file, model="whisper-1")
    text = transcript.text
    print("Transcription result:", text)
    return text
 

class SimplePOSTHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        print("Reading", content_length)
        post_data = self.rfile.read(content_length)

        filename = "data/"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        input_file = filename+".mp4"
        output_file = filename+".mp3"
        text_file = filename+".txt"
        with open(input_file, "wb") as f:
            f.write(post_data)
        print(f"Saved POST data to {input_file}")
        text = process_and_send(input_file, output_file)
        with open(text_file, "w") as f:
            f.write(text)
        self.send_response(200)
        self._set_cors_headers()
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def _set_cors_headers(self):
        """Set CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours

    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests for CORS"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    

def main():
    with open("openaikey.txt") as f:
        openai.api_key = f.read().strip()
    host, port = "localhost", 8052
    server = HTTPServer((host, port), SimplePOSTHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    sys.exit(main())
