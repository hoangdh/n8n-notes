from flask import Flask, request, jsonify
import subprocess
import random
import requests

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.2420.65",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/123.0.6312.86 Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",  # Internet Explorer 11
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS_20170720; rv:11.0) like Gecko", # Internet Explorer 11 on Windows 7
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Version/10.0 Chrome/123.0.0.0 Safari/537.36", # Chrome with Version info
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) OPR/100.0.4815.30 Safari/537.36", # Opera
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; ARM; Trident/7.0; Touch; rv:11.0) like Gecko", # Internet Explorer on ARM Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/6.6.3327.59 Chrome/122.0.6261.128 Safari/537.36", # Vivaldi
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/7.0.1.1000 Chrome/99.0.4844.84 Safari/537.36" # Maxthon
]

def is_image_link(url):
    """Kiểm tra xem link có phải là ảnh bằng cách kiểm tra Content-Type."""
    try:
        response = requests.head(url, timeout=5)  # Sử dụng HEAD request để tiết kiệm băng thông
        response.raise_for_status()  # Báo lỗi cho các status code không thành công
        content_type = response.headers.get('Content-Type', '')
        return content_type.startswith('image/')
    except requests.exceptions.RequestException:
        return False

def extract_image_links(links):
    """Hàm xử lý để chỉ lấy các link ảnh từ danh sách links bằng cách kiểm tra Content-Type."""
    image_links = [link for link in links if is_image_link(link)]
    return image_links

@app.route('/download', methods=['GET'])
def download_media():
    link = request.args.get('link')
    if not link:
        return jsonify({"error": "Vui lòng cung cấp tham số 'link'."}), 400

    user_agent = random.choice(USER_AGENTS)
    command = [
        'gallery-dl',
        '--get-urls',
        '--user-agent',
        user_agent,
        link
    ]

    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        output_lines = process.stdout.strip().split('\n')
        image_links = extract_image_links(output_lines)
        return jsonify({"original_link": link, "image_links": image_links}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Lỗi khi chạy gallery-dl: {e}", "details": e.stderr}), 500
    except FileNotFoundError:
        return jsonify({"error": "Không tìm thấy lệnh gallery-dl. Đảm bảo rằng gallery-dl đã được cài đặt và có trong PATH."}), 500
    except Exception as e:
        return jsonify({"error": f"Lỗi không xác định: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
