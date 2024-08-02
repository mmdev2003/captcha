#!/bin/sh

apt update -y && apt upgrade -y && apt install -y curl libreadline-dev unzip build-essential wget libz-dev zlib1g-dev ffmpeg libsm6 libxext6

curl -L -R -O https://www.lua.org/ftp/lua-5.4.6.tar.gz
tar zxf lua-5.4.6.tar.gz
cd lua-5.4.6
make
make install
lua -v
cd /usr/src/app/

wget https://luarocks.org/releases/luarocks-3.11.0.tar.gz
tar zxpf luarocks-3.11.0.tar.gz
cd luarocks-3.11.0
./configure && make && make install
cd /usr/src/app

pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

luarocks install lua-express
luarocks install lua-express-middlewares

curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&\
apt-get install -y nodejs
npm install pm2 -g

cd backend
pm2 start generator/generator.py --interpreter=python3
cd server
pm2 start main.lua --interpreter=lua
pm2 log 1