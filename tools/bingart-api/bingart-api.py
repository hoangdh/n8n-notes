from flask import Flask, request, jsonify, render_template
from bingart import BingArt

# Replace your cookie
myCookie = ''

app = Flask(__name__)

@app.route('/bingart', methods=['GET'])
def generate_images():
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
