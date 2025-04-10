from flask import Flask, request, send_from_directory, url_for, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import time
from bingart import BingArt
import math, random

app = Flask(__name__)

# Dữ liệu mẫu (ví dụ, danh sách sản phẩm)
sample_data = [{'id': i + 1,
                'name': f'ProductID {i + 1}',
                'description': f'Description ProductID {i + 1}',
                'price': math.floor(random.random() * 100) + 10} for i in range(100)]

@app.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', default=1, type=int) # Lấy số trang từ query parameter 'page', mặc định là trang 1
    limit = 10 # Số lượng mục trên mỗi trang
    start_index = (page - 1) * limit
    end_index = page * limit

    paginated_data = sample_data[start_index:end_index] # Lấy dữ liệu cho trang hiện tại
    total_pages = math.ceil(len(sample_data) / limit) # Tính tổng số trang

    response = {
        'page': page,
        'total_pages': total_pages,
        'total_items': len(sample_data),
        'items_per_page': limit,
        'data': paginated_data
    }

    return jsonify(response)

myCookie = "1uDBoQstbEphUO-tIJu1qqfchL4FqrMgbeHSRgkN6qL-3MnaqbcR3oEDc2bzhaqDCdIsilbDBngMSLBUUHkWE5ObP9YAtfENN6Ry3vlBBjpcKl_4NqqX-s_T572uRrGQSbPFDKtPA6vUsXbGrCJg9lwNtS9pJNHfwb3qLHqWlgF9qSyVGBPx0plPGG_taXvNO1-v_bailZgQ6Z80mO2I8hqDOI9WqZQF1luL9u78zfTc"

@app.route('/bingart', methods=['GET'])
def bingart_generate_images():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({"error": "Please provide a prompt via the GET parameter 'prompt'"}), 400

    # Replace 'myCooko' with your valid _U cookie value
    bing_art = BingArt(auth_cookie_U=myCookie)
    images = []
    try:
        results = bing_art.generate_images(prompt)
        for image in results['images']:
            imageUrl = image['url']
            images.append(imageUrl)
    except Exception as e:
        return jsonify({"error": f"An error occurred while generating images: {str(e)}", "prompt": prompt}), 500
    finally:
        bing_art.close_session()

    return jsonify({"images": list(set(images)), "prompt": prompt})

@app.route('/generate_image', methods=['POST'])
def generate_image():
    """API endpoint để tạo ảnh theo yêu cầu (phương thức POST)."""
    try:
        data = request.get_json()
        image_url = data['image_url']  # URL ảnh duy nhất
        caption = data['caption']

        # 1. Khởi tạo ảnh
        img = Image.new("RGB", (1024, 1024), "white")
        draw = ImageDraw.Draw(img)

        # 2. Vẽ border 1px cho toàn ảnh
        draw.rectangle([(0, 0), (1023, 1023)], outline="white", width=1)

        # 3. Chia thành 3 phần
        width_part = 1024
        height_part = 1024 // 3
        image_area_height = 2 * height_part # Chiều cao vùng chứa ảnh (2/3 trên)
        image_area_width = 1024 # Chiều rộng vùng chứa ảnh

        # 4. Chèn ảnh từ URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        # Tính toán kích thước mới để zoom vừa vặn và giữ tỉ lệ
        image_ratio = image.width / image.height # Tỉ lệ khung hình của ảnh gốc
        area_ratio = image_area_width / image_area_height # Tỉ lệ khung hình của vùng chứa

        if image_ratio > area_ratio: # Ảnh gốc rộng hơn vùng chứa (hoặc tỉ lệ tương đương)
            new_width = image_area_width
            new_height = int(new_width / image_ratio)
        else: # Ảnh gốc cao hơn vùng chứa (hoặc tỉ lệ tương đương)
            new_height = image_area_height
            new_width = int(new_height * image_ratio)

        image = image.resize((new_width, new_height))

        # Căn giữa ảnh sau khi resize
        x_offset = (image_area_width - new_width) // 2
        y_offset = (image_area_height - new_height) // 2
        img.paste(image, (x_offset, y_offset))


        # 5. Tạo phần nền đỏ và chèn caption
        red_part = Image.new("RGB", (1024, height_part), "red")
        img.paste(red_part, (0, 2 * height_part))

        # Chèn caption
        try:
            font = ImageFont.truetype("OpenSans-ExtraBold.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
            print("Font OpenSans-ExtraBold.ttf not found. Using default font.")

        bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (1024 - text_width) // 2
        y = 2 * height_part + (height_part - text_height) // 2
        draw.text((x, y), caption, font=font, fill="white", stroke_width=1, stroke_fill="black")

        # 6. Lưu ảnh vào file tạm
        output_path = "output_image.png"
        img.save(output_path)

        # 7. Tạo URL ảnh
        server_address = request.host_url.rstrip('/')
        image_url = f"{server_address}/images/{output_path}"

        return {"image_url": image_url}, 200

    except Exception as e:
        return {"error": str(e)}, 500

# Endpoint để phục vụ ảnh
@app.route('/images/<path:path>')
def serve_image(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='192.168.203.1', debug=True)
