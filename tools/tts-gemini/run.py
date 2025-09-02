# Để chạy code này, bạn cần cài đặt các thư viện sau:
# pip install Flask google-genai
# Code by Gemini

from flask import Flask, request, jsonify, send_file
import base64
import mimetypes
import os
import re
import struct
from google import genai
from google.genai import types
import io
import random

app = Flask(__name__)

# Danh sách toàn bộ các giọng đọc được hỗ trợ
# Các giọng này có thể được điều chỉnh ngữ điệu thông qua `prompt_system`
VOICE_NAMES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede",
    "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba",
    "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar",
    "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
    "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat"
]

# Các hàm helper để chuyển đổi audio sang định dạng WAV
def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.
    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.
    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters.get("bits_per_sample", 16)
    sample_rate = parameters.get("rate", 24000)
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size
    )
    return header + audio_data

def parse_audio_mime_type(mime_type: str) -> dict:
    """Parses bits per sample and rate from an audio MIME type string.
    """
    bits_per_sample = 16
    rate = 24000

    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}


@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    """
    Handles POST request to generate TTS audio.
    Receives 'prompt_system' and 'text' in JSON body.
    Requires 'Authorization: Bearer <GEMINI_API_KEY>' in headers.
    """
    # Lấy khóa API từ headers
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized: Missing or invalid API key"}), 401
    
    api_key = auth_header.split(' ')[1]

    # Lấy dữ liệu từ body của request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Bad Request: 'text' field is required"}), 400
    
    text = data['text']
    prompt_system = data.get('prompt_system', '')

    try:
        # Khởi tạo client với API key từ request
        client = genai.Client(api_key=api_key)
        model = "gemini-2.5-flash-preview-tts"
        
        # Chọn ngẫu nhiên một giọng đọc từ danh sách
        selected_voice = random.choice(VOICE_NAMES)
        print(f"Sử dụng giọng đọc ngẫu nhiên: {selected_voice}")
        
        # Xây dựng nội dung yêu cầu
        full_text = text
        if prompt_system:
            full_text = prompt_system + full_text

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=full_text),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=[
                "audio",
            ],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=selected_voice
                    )
                )
            ),
        )

        audio_buffer = io.BytesIO()
        audio_mime_type = ""
        
        # Stream audio và gom các chunk lại
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                if inline_data and inline_data.data:
                    audio_buffer.write(inline_data.data)
                    if not audio_mime_type:
                        audio_mime_type = inline_data.mime_type

        # Chuyển đổi toàn bộ dữ liệu audio sang định dạng WAV
        raw_audio_data = audio_buffer.getvalue()
        wav_data = convert_to_wav(raw_audio_data, audio_mime_type)

        # Trả về file âm thanh
        return send_file(
            io.BytesIO(wav_data),
            mimetype="audio/wav",
            as_attachment=True,
            download_name="output.wav"
        )
        
    except Exception as e:
        # Xử lý các lỗi có thể xảy ra
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
