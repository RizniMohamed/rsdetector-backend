import cv2
import numpy as np
import pandas as pd
from skimage import exposure
from tensorflow.keras.models import load_model
from tensorflow.keras.metrics import Recall, Precision
from ultralytics import YOLO

# Constants
YOLO_MODEL_PATH = './yolo.pt'
RECOGNITION_MODEL_PATH = "./cnn/14800"
SIGN_DATA_PATH = "./sign_data.csv"
LABELS = ['0', '1', '10', '2', '3', '4', '5', '6', '7', '8', '9']

def f1_score(y_true, y_pred):
    """Calculate F1 score."""
    
    if all(v == 0 for v in y_true) and all(v == 0 for v in y_pred):
        return 1.0
    
    precision_obj = Precision()
    recall_obj = Recall()
    precision_val = precision_obj(y_true, y_pred).numpy()
    recall_val = recall_obj(y_true, y_pred).numpy()
    return 2 * ((precision_val * recall_val) / (precision_val + recall_val + 1e-5))
  
# Load models
final_model_detection = YOLO(YOLO_MODEL_PATH)
final_model_recognition = load_model(RECOGNITION_MODEL_PATH, custom_objects={'f1_score': f1_score})
names = final_model_detection.names

def crop_cls_image(x1, y1, x2, y2, resized_frame):
    """Crop and resize the image based on bounding box coordinates."""
    crop_size = 150
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    crop_x1, crop_x2 = max(center_x - crop_size // 2, 0), min(center_x + crop_size // 2, resized_frame.shape[1])
    crop_y1, crop_y2 = max(center_y - crop_size // 2, 0), min(center_y + crop_size // 2, resized_frame.shape[0])
    cropped_region = resized_frame[crop_y1:crop_y2, crop_x1:crop_x2]
    return cv2.resize(cropped_region, (crop_size, crop_size))

def recognition(crop_img):
    """Recognize the cropped image."""
    print(RECOGNITION_MODEL_PATH)
    crop_resize = cv2.resize(crop_img, (64, 64))
    crop_resize_rgb = cv2.cvtColor(crop_resize, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    img_array = np.expand_dims(crop_resize_rgb, axis=0) / 255.0
    predictions = final_model_recognition.predict(img_array)
    class_index = np.argmax(predictions)
    return LABELS[class_index]

def get_text(label):
    """Retrieve text information for a given label."""
    sign_info = pd.read_csv(SIGN_DATA_PATH)
    return sign_info[sign_info.id == int(label)].values[0][2]

def detection(frame):
    """Detect and recognize objects in the frame."""
    clahe_img = exposure.equalize_adapthist(frame, clip_limit=0.1)
    clahe_img_uint8 = (clahe_img * 255).astype('uint8')
    resized_frame, resized_o_frame = cv2.resize(clahe_img_uint8, (640, 640)), cv2.resize(frame, (640, 640))
    results = final_model_detection(resized_frame, conf=0.5)

    label_texts = []
    for r in results:
        if r:
            for b in r.boxes:
                x1, y1, x2, y2 = b.xyxy.cpu().numpy().astype(int)
                cropped_image = crop_cls_image(x1, y1, x2, y2, resized_o_frame)
                clahe_img = exposure.equalize_adapthist(cropped_image, clip_limit=0.03)
                cv2.imwrite(f'./temp/{b.cls} {b.conf}.jpg', cropped_image)
                label = recognition((clahe_img * 255).astype('uint8'))
                label_texts.append(get_text(label))
            return " and ".join(label_texts)
    return None
