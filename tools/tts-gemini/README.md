### Cài đặt thư viện

```
pip install Flask google-genai
```

### Chạy ứng dụng

```
python3 run.py
```

### Tạo Audio 

```
curl --location --request POST 'http://127.0.0.1:5000/generate_tts' \
--header 'Authorization: Bearer GEMINI_API_KEY' \
--header 'Content-Type: application/json' \
--data-raw '{
    "prompt_system": "Hãy tạo giọng đọc chân thành, biết ơn: ",
    "text": "Cảm ơn bạn đã mò được vào tới đây! Chúng tôi chia sẻ miễn phí đoạn mã này cho các bạn sử dụng!"
}'
```
**CHÚ Ý**: Thay GEMINI_API_KEY hợp lệ lấy từ Google AI.
