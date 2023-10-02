from ultralytics import YOLO
# from PIL import Image
import cv2
# import matplotlib.pyplot as plt

final_model_detection = YOLO('./yolo.pt')
names = final_model_detection.names


def crop_cls_image(x1, y1, x2, y2,resized_frame):

  crop_size = 64
  
  # Calculate the center of the bounding box
  center_x = (x1 + x2) // 2
  center_y = (y1 + y2) // 2

  # Calculate the new cropping coordinates to ensure a 224x224 crop
  crop_x1 = max(center_x - crop_size // 2, 0)
  crop_x2 = min(crop_x1 + crop_size, resized_frame.shape[1])
  crop_y1 = max(center_y - crop_size // 2, 0)
  crop_y2 = min(crop_y1 + crop_size, resized_frame.shape[0])

  # Crop the region, including background if needed, to get a 224x224 image
  cropped_region = resized_frame[crop_y1:crop_y2, crop_x1:crop_x2]
  # cropped_region = resized_frame[y1:y2, x1:x2]

  # Resize the cropped region to 224x224
  cropped_image = cv2.resize(cropped_region, (crop_size, crop_size))

  return cropped_image

def detection(frame):

  resized_frame = cv2.resize(frame, (640, 640))
  results = final_model_detection(resized_frame,conf=0.5)


  for r in results:
    if r:
      bboxes = r.boxes.xyxy[0].cpu().numpy()
      x1, y1, x2, y2 = bboxes.astype(int)
      for c in r.boxes:
        conf =  round(float(c.conf),2)
        cls =  names[int(c.cls)]
        return (cls,conf, crop_cls_image(x1, y1, x2, y2,resized_frame),results)
    return None

