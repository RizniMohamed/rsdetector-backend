import numpy as np
from skimage import exposure
from tensorflow.keras.models import load_model
from tensorflow.keras.metrics import Recall, Precision
from ultralytics import YOLO
from database import get_text,store_processing_results
from io import BytesIO
from PIL import Image

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
    crop_x1, crop_x2 = max(center_x - crop_size // 2, 0), min(center_x + crop_size // 2, resized_frame.size[0])
    crop_y1, crop_y2 = max(center_y - crop_size // 2, 0), min(center_y + crop_size // 2, resized_frame.size[1])
    cropped_region = resized_frame.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    return cropped_region.resize((crop_size, crop_size))

def recognition(crop_img):
    """Recognize the cropped image."""
    crop_img_pil = Image.fromarray(crop_img)
    crop_resize = crop_img_pil.resize((64, 64))
    crop_resize_rgb = crop_resize.convert('RGB')
    img_array = np.array(crop_resize_rgb) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = final_model_recognition.predict(img_array)
    class_index = np.argmax(predictions)
    confidence_score = predictions[0][class_index]
    return LABELS[class_index],confidence_score

def detection(frame,img_id):
    """Detect and recognize objects in the frame."""
    clahe_img = exposure.equalize_adapthist(np.array(frame), clip_limit=0.1)
    clahe_img_uint8 = (clahe_img * 255).astype('uint8')
    resized_frame, resized_o_frame = Image.fromarray(clahe_img_uint8).resize((640, 640)), frame.resize((640, 640))
    results = final_model_detection(np.array(resized_frame)[..., ::-1], conf=0.5) ## send as BGR for detection

    label_texts = []
    for r in results:
        if r:
            for b in r.boxes:
                x1, y1, x2, y2 = b.xyxy.cpu().numpy().astype(int)[0]
                cropped_image = crop_cls_image(x1, y1, x2, y2, resized_o_frame)
                cropped_image_array = np.array(cropped_image)
                clahe_img = exposure.equalize_adapthist(cropped_image_array, clip_limit=0.03)
                
                # Save cropped image to temp folder
                cropped_image.save(f'./temp/{b.cls} {b.conf}.jpg')
                
                label, confidence_score = recognition((clahe_img * 255).astype('uint8'))
                label_texts.append(get_text(label))
                
                # Convert the cropped image to bytes for storing in the database
                temp_file = BytesIO()
                cropped_image.save(temp_file, format='JPEG')
                cropped_image_bytes = temp_file.getvalue()
                
                store_processing_results(img_id,{
                    'detected_label': get_text(int(b.cls)),
                    'recognized_label': get_text(label),
                    'detection_confidence_score': float(b.conf),
                    'recognition_confidence_score': float(confidence_score),
                    'cropped_image': cropped_image_bytes
                })
                
            return " and ".join(label_texts)
    return None
