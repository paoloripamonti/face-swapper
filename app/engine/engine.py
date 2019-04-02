from app.engine.face_swap import face_swap
import base64
from PIL import Image
import cv2
from io import BytesIO
import numpy as np


def read_and_swap(img1, img2):
    """
    Read and swap img1 and img2 from ajax call
    :param img1: base64 img1
    :param img2: base64 img2
    :return: base64 image swapped
    """
    img1 = readb64(img1)
    img2 = readb64(img2)

    _, buffer = cv2.imencode('.jpg', face_swap(img1, img2))
    return base64.b64encode(buffer)


def readb64(base64_string):
    """
    Convert base64 string into image
    :param base64_string: base64 string
    :return: cv2 image
    """
    base64_img = str(base64_string.split("base64,")[-1])
    data = base64.b64decode(base64_img)
    pil_image = Image.open(BytesIO(data))
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
