import random
from PIL import Image
import config
import cairosvg
import cv2
from params_pool import color_pool
import time

def check_collision(new_x, new_y, existing_coordinates, icon_size):
    for icon in existing_coordinates:
        if abs(new_x - icon[0]) < icon_size and abs(new_y - icon[1]) < icon_size:
            return True
    return False

        
def add_bg(bg, save_dir, captcha_uid, crop_w, crop_h, count_blur, width_blur, numbers=None):
    png = cairosvg.svg2png(url=config.src_svg, write_to=config.src_png)
    
    png = Image.open(config.src_png)
    bg = Image.open(bg)
    bg = random_crop_image(bg, crop_w, crop_h)

    canvas = Image.new("RGB", bg.size, (255, 255, 255))
    canvas.paste(bg, (0, 0))
    canvas.paste(png, (0, 0), png)
    if numbers:
        image_path = f'{save_dir}/{numbers}_{captcha_uid}.png'
    else:
        image_path = f'{save_dir}/{captcha_uid}.png'
    canvas.save(image_path)
    add_blur(image_path, count_blur, width_blur, crop_w, crop_h)
    
def random_crop_image(image, crop_w, crop_h):
    width, height = image.size
    
    x1 = random.randint(0, width - crop_w)
    y1 = random.randint(0, height - crop_h)
    x2 = x1 + crop_w
    y2 = y1 + crop_h
    image = image.crop((x1, y1, x2, y2))
    return image
    
def add_blur(image_path, num_stripes, stripe_thickness, w, h):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    blurred_image = image.copy()

    for _ in range(num_stripes):
        x_start = random.randint(0, w - stripe_thickness)
        y_start = random.randint(0, h - stripe_thickness)
        x_end = x_start + stripe_thickness
        y_end = y_start + stripe_thickness
        roi = blurred_image[y_start:y_end, x_start:x_end]
        blurred_roi = cv2.GaussianBlur(roi, (1,1), 1)
        blurred_image[y_start:y_end, x_start:x_end] = blurred_roi
        cv2.imwrite(image_path, blurred_image)

def get_new_coordinates(existing_coordinates, scale, icon_width):
    max_x = int((config.captcha_w - icon_width) / scale)
    max_y = int((config.captcha_h - icon_width) / scale)
    min_x = int(icon_width)
    min_y = int(icon_width)
    new_x = random.randint(min_x, max_x)
    new_y = random.randint(min_y, max_y)
    count_try = 0
    while check_collision(new_x, new_y, existing_coordinates, icon_width): 
        count_try += 1
        new_x = random.randint(min_x, max_x)
        new_y = random.randint(min_y, max_y)
        if count_try > 5000:
            return 0,0
    return new_x, new_y
