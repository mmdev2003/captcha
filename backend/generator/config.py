import os

src_image_dir = 'src_image'
captcha_dir = 'captchas'

captcha_image_dir = f'{captcha_dir}/image'
captcha_bg_dir = f'{src_image_dir}/captcha_bg'
count_captcha_bg = len([f for f in os.listdir(captcha_bg_dir) if f.endswith('.jpg')])

ask_image_dir = f'{captcha_dir}/ask'
ask_bg_dir = f'{src_image_dir}/ask_bg'
count_ask_bg = len([f for f in os.listdir(ask_bg_dir) if f.endswith('.jpg')])

numbers_image_dir = f'{captcha_dir}/numbers'
numbers_bg_dir = f'{src_image_dir}/numbers_bg'
count_numbers_bg = len([f for f in os.listdir(ask_bg_dir) if f.endswith('.jpg')])

src_png = f'{src_image_dir}/src.png'
src_svg = f'{src_image_dir}/src.svg'

if not os.path.exists(captcha_dir):
    os.makedirs(captcha_dir)
    os.makedirs(numbers_image_dir)
    os.makedirs(ask_image_dir)
    os.makedirs(captcha_image_dir)

captcha_w, captcha_h = 250, 145
icon_sample_size = 3
color_sample_size = 2
min_icon_count = 8
max_icon_count = 12
min_icon_scale = 1.3
max_icon_scale = 1.7
icon_width = 15

numbers_w, numbers_h = 100, 100
numbers_font_size = 24

ask_w = 250
ask_font_size = 11