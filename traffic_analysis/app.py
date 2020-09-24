import io
from flask import Flask, request, Response
from PIL import Image
app = Flask(__name__)


@app.route('/api', methods=['POST'])
def api_controller():
    if request.method != 'POST':
        return Response(status=403)
    file = request.files['img']
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes))
    img.save('./tmp_data/test', 'png')
    return Response(status=200)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
