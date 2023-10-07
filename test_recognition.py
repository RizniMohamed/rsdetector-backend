import pytest
import cv2
from model import recognition
from skimage import exposure

path = "test_cropped_images/valid"

SAMPLE_IMAGES = [
    
    # PASSED - STOP
    ("./"+path+"/0/1.jpg", '0'),
    ("./"+path+"/0/2.jpg", '0'),
    ("./"+path+"/0/3.jpg", '0'),
    ("./"+path+"/0/4.jpg", '0'),
    ("./"+path+"/0/5.jpg", '0'),
    
    #PASSED - PRDESTRIAN CROSSING
    ("./"+path+"/1/1.jpg", '1'),
    ("./"+path+"/1/2.jpg", '1'),
    ("./"+path+"/1/3.jpg", '1'),
    ("./"+path+"/1/4.jpg", '1'),
    ("./"+path+"/1/5.jpg", '1'),
    
    # PASSED - PRDESTRIAN CROSSING AHEAD FAILD
    ("./"+path+"/2/1.jpg", '2'),
    ("./"+path+"/2/2.jpg", '2'),
    ("./"+path+"/2/3.jpg", '2'),
    ("./"+path+"/2/4.jpg", '2'),
    ("./"+path+"/2/5.jpg", '2'),
    
    # PASSED - SPEED LIMIT 60 
    ("./"+path+"/3/1.jpg", '3'),
    ("./"+path+"/3/2.jpg", '3'),
    ("./"+path+"/3/3.jpg", '3'),
    ("./"+path+"/3/4.jpg", '3'),
    ("./"+path+"/3/5.jpg", '3'),
    
    # PASSED - BUS 
    ("./"+path+"/4/1.jpg", '4'),
    ("./"+path+"/4/2.jpg", '4'),
    ("./"+path+"/4/3.jpg", '4'),
    ("./"+path+"/4/4.jpg", '4'),
    ("./"+path+"/4/5.jpg", '4'),
    
    # PASSED - CHILDRED CROSSING
    ("./"+path+"/5/1.jpg", '5'),
    ("./"+path+"/5/2.jpg", '5'),
    ("./"+path+"/5/3.jpg", '5'),
    ("./"+path+"/5/4.jpg", '5'),
    ("./"+path+"/5/5.jpg", '5'),
    
    # PASSED - NO PARKING
    ("./"+path+"/6/1.jpg", '6'),
    ("./"+path+"/6/2.jpg", '6'),
    ("./"+path+"/6/3.jpg", '6'),
    ("./"+path+"/6/4.jpg", '6'),
    ("./"+path+"/6/5.jpg", '6'),
    
    # PASSED - TURN RIGHT 
    ("./"+path+"/7/1.jpg", '7'),
    ("./"+path+"/7/2.jpg", '7'),
    ("./"+path+"/7/3.jpg", '7'),
    ("./"+path+"/7/4.jpg", '7'),
    ("./"+path+"/7/5.jpg", '7'),
    
    # PASSED - LEFT SUB ROAD JOIN 
    ("./"+path+"/8/1.jpg", '8'),
    ("./"+path+"/8/2.jpg", '8'),
    ("./"+path+"/8/3.jpg", '8'),
    ("./"+path+"/8/4.jpg", '8'),
    ("./"+path+"/8/5.jpg", '8'),
    
    # PASSED - RIGHT SUB ROAD JOIN
    ("./"+path+"/9/1.jpg", '9'),
    ("./"+path+"/9/2.jpg", '9'),
    ("./"+path+"/9/3.jpg", '9'),
    ("./"+path+"/9/4.jpg", '9'),
    ("./"+path+"/9/5.jpg", '9'),
    
    # PASSED - SIGNAL LIGHT
    ("./"+path+"/10/1.jpg", '10'),
    ("./"+path+"/10/2.jpg", '10'),
    ("./"+path+"/10/3.jpg", '10'),
    ("./"+path+"/10/4.jpg", '10'),
    ("./"+path+"/10/5.jpg", '10'),

]

@pytest.mark.parametrize("image_path, expected_label", SAMPLE_IMAGES)
def test_recognition(image_path, expected_label):
    cropped_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    # clahe_img = exposure.equalize_adapthist(cropped_image, clip_limit=0.00)
    cls, conf = recognition(cropped_image)
    assert cls == expected_label
    # assert recognition((clahe_img * 255).astype('uint8')) == expected_label
