from __future__ import print_function, division
import io
import argparse
import torch
from torchvision import transforms
from flask import Flask, request, Response
from PIL import Image
from pathlib import Path

app = Flask(__name__)
model = None
model.classifier[1] = torch.nn.Conv2d(
    512, 2, kernel_size=(1, 1), stride=(1, 1))
preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])
model.eval()


def transform_img(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    return preprocess(img).unsqueeze(0)


def predict(img_bytes):
    x = transform_img(img_bytes)
    y = model.forward(x)
    _, prediction = y.max(1)
    return prediction


@app.route('/api', methods=['POST'])
def api_controller():
    if request.method != 'POST':
        return Response(status=403)
    file = request.files['img']
    img_bytes = file.read()
    prediction = predict(img_bytes)
    return {'prediction': prediction.item()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the traffic analysis module with a \
                given time interval and model')
    parser.add_argument('interval', type=int, choices=[3, 5],
                        help='time interval being used')
    parser.add_argument('model_name', choices=['m_net', 's_net'],
                        help='time interval being used')
    args = parser.parse_args()
    if args.model_name == 'm_net':
        model = torch.hub.load('pytorch/vision:v0.5.0',
                               'mobilenet_v2', pretrained=False)
        model.classifier[1] = torch.nn.Linear(1280, 2)
    else:
        model = torch.hub.load('pytorch/vision:v0.5.0',
                               'squeezenet1_1', pretrained=False)
        model.classifier[1] = torch.nn.Conv2d(
            512, 2, kernel_size=(1, 1), stride=(1, 1))
    model_pth = Path.cwd() / 'models'
    model_pth = model_pth / '3_sec_interval' \
        if args.interval == 3 else '5_sec_interval'
    model_pth = model_pth / args.model_name / 'model.pt'
    model_state = torch.load(model_pth)
    model.load_state_dict(model_state)
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
