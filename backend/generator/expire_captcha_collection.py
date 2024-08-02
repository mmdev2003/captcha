import os
import time
from datetime import datetime, timedelta


txt_db_dir = 'txt_db'
ask_path = f'{txt_db_dir}/ask_life_time.txt'
captcha_image_path = f'{txt_db_dir}/captcha_image_life_time.txt'
captcha_path = f'{txt_db_dir}/captcha_life_time.txt'
numbers_path = f'{txt_db_dir}/numbers_life_time.txt'

if not os.path.exists(txt_db_dir):
    os.makedirs(txt_db_dir)
    
print('Запустились')
def check_expired(txt_path):
    try:
        with open(txt_path, 'r') as file:
            lines = file.readlines()
    except:
        return False
    new_lines = []
    for del_line in lines:
        split_line = del_line.split(' ')
        file_name = split_line[0]
        time_to_del = datetime.fromtimestamp(int(split_line[1])) + timedelta(seconds=90)
        if time_to_del.timestamp() - datetime.now().timestamp() < 0:
            try:
                os.remove(file_name)
                print(f'Удалили файл: {file_name}')
            except OSError as e:
                pass
        else:
            new_lines.append(del_line)
    with open(txt_path, 'w') as new_file:
        new_file.writelines(new_lines)

while True:
    check_expired(numbers_path)
    check_expired(captcha_path)
    check_expired(captcha_image_path)
    check_expired(ask_path)
    time.sleep(5)