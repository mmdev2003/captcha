import io
import os
import json
import uuid
import time
import random
import base64
from datetime import datetime

import cv2
import svgwrite
import cairosvg
from PIL import Image, ImageDraw
    
import utils
import config
from params_pool import icon_pool, color_pool, ask_pool

def add_icon(captcha_svg, icon_d, color, scale, new_x, new_y):
    icon = captcha_svg.path(icon_d, stroke=color, fill="none", stroke_width=2)
        
    icon.scale(scale)
    icon.translate(new_x, new_y)
    icon.rotate(random.randint(0, 360))
    captcha_svg.add(icon)

def get_answer(icons_sum, ask_operator, pair_icon_for_ask):
    
    if ask_operator == '+':
        answer = icons_sum[pair_icon_for_ask[0]] + icons_sum[pair_icon_for_ask[1]]
        
    elif ask_operator == '-':
        answer = icons_sum[pair_icon_for_ask[0]] - icons_sum[pair_icon_for_ask[1]] 
        
    elif ask_operator == '*':
        answer = icons_sum[pair_icon_for_ask[0]] * icons_sum[pair_icon_for_ask[1]]
    return answer

def get_ask(pair_icon_for_ask, icon_choice, color_choice, ask_type):
    first_icon_name = pair_icon_for_ask[0].split('_')[1]
    first_icon_color = pair_icon_for_ask[0].split('_')[0]
    first_icon_name_ru = list(filter(lambda icon: icon['name'] == first_icon_name, icon_choice))[0]['ru']
    first_icon_color_ru = list(filter(lambda icon: icon['color'] == first_icon_color, color_choice))[0]['ru']
    
    second_icon_name = pair_icon_for_ask[1].split('_')[1]
    second_icon_color = pair_icon_for_ask[1].split('_')[0]
    second_icon_name_ru = list(filter(lambda icon: icon['name'] == second_icon_name, icon_choice))[0]['ru']
    second_icon_color_ru = list(filter(lambda icon: icon['color'] == second_icon_color, color_choice))[0]['ru']
    ask = [ask_type, f'{first_icon_color_ru} {first_icon_name_ru} и', f'{second_icon_color_ru} {second_icon_name_ru}']
    return ask
    
        
def create_numbers_image(captcha_uid):
    w, h = config.numbers_w, config.numbers_h
    numbers_svg = svgwrite.Drawing(config.src_svg, profile='tiny', size=(f'{w}px', f'{h}px'))
    numbers = random.randint(10, 1000)
    
    for i, digit in enumerate(f'{numbers}'):
        rotation = random.randint(-15, 15)
        x = config.numbers_font_size * i + 20
        y = (config.numbers_h / 2) + (config.numbers_font_size / 2)
        numbers_svg.add(numbers_svg.text(f'{digit}', insert=(x, y), font_size=f"{config.numbers_font_size + random.randint(-5, 8)}px", fill='black', transform=f"rotate({rotation}, {x}, {y})"))
    numbers_svg.save()
    bg = f'{config.numbers_bg_dir}/{random.randint(1, config.count_numbers_bg)}.jpg'
    utils.add_bg(bg, config.numbers_image_dir, captcha_uid, w, h, 10, 30, numbers=numbers)
    return numbers
    
    
def create_ask_image(ask, captcha_uid):
    margin = config.ask_font_size
    w, h = config.ask_w, (config.ask_font_size + 5) * len(ask)+1
    ask_svg = svgwrite.Drawing(config.src_svg, profile='full', size=(f'{w}px', f'{h}px'))
    for line in ask:
        for i, letter in enumerate(line):
            x = config.ask_font_size * (i-0.3) + 5
            y = margin
            rotation = random.randint(-8, 8)
            text = ask_svg.text(letter, insert=(x, y), font_size=f"{config.ask_font_size + random.randint(-2, 2)}px", fill='white', transform=f"rotate({rotation}, {x}, {y})")
            ask_svg.add(text)
        margin += config.ask_font_size + 3
    ask_svg.save()
    bg = f'{config.ask_bg_dir}/{random.randint(1, config.count_ask_bg)}.jpg'
    utils.add_bg(bg, config.ask_image_dir, captcha_uid, w, h, 10, 30)
    
def create_captcha(captcha_uid):
    w, h = config.captcha_w, config.captcha_h
    captcha_svg = svgwrite.Drawing(filename=config.src_svg, size=(f'{w}px', f'{h}px'), profile='full')
    existing_coordinates = []
    existing_icons = []
    
    icon_choice = random.sample(icon_pool, config.icon_sample_size)
    color_choice = random.sample(color_pool, config.color_sample_size)
    
    ask = random.choice(ask_pool)
    ask_operator = ask['operator']
    ask_type = ask['type']
    
    for _ in range(random.randint(config.min_icon_count, config.max_icon_count)):
        color = random.choice(color_choice)['color']
        scale = random.uniform(config.min_icon_scale, config.max_icon_scale)
        
        icon = random.choice(icon_choice)
        icon_d = icon['d']
        icon_name = icon['name']
        icon_width = config.icon_width * scale
        
        new_x, new_y = utils.get_new_coordinates(existing_coordinates, scale, icon_width)
        if not new_x:
            return 0, 0
            
        add_icon(captcha_svg, icon_d, color, scale, new_x, new_y)
        
        existing_icons.append(f'{color}_{icon_name}')
        existing_coordinates.append((new_x, new_y))
    icons_sum = {column: existing_icons.count(column) for column in existing_icons}
    pair_icon_for_ask = random.sample(list(icons_sum), 2)
    
    answer = get_answer(icons_sum, ask_operator, pair_icon_for_ask)
    ask = get_ask(pair_icon_for_ask, icon_choice, color_choice, ask_type)
    captcha_svg.save()
    bg = f'{config.captcha_bg_dir}/{random.randint(1, config.count_captcha_bg)}.jpg'
    utils.add_bg(bg, config.captcha_image_dir, captcha_uid, w, h, 10, 30)
    return ask, answer


while True:
    try:
        captcha_uid = str(uuid.uuid4()).replace('-', '')
        ask, answer = create_captcha(captcha_uid)
        if not ask:
            continue
        print(answer)
        create_numbers_image(captcha_uid)
        create_ask_image(ask, captcha_uid)
        captha_params = {
           'captcha_uid': captcha_uid,
        }
    
        with open(f'{config.captcha_dir}/{answer}_{captcha_uid}.json', 'w') as file:
            json.dump(captha_params, file)
        print('Готово')
    except Exception:
        continue