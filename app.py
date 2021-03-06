

import io
import json

from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request, render_template


app = Flask(__name__)
image_class_index = json.load(open('image_class_index.json'))
model = models.densenet121(pretrained=True)
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return image_class_index[predicted_idx]


@app.route('/', methods = ['GET','POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            print("No file")
            return 'No File'
        file = request.files['file']
        img_bytes = file.read()
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        class_name = class_name.capitalize()
        return render_template('res.html',value = class_name)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

