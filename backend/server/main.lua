local express = require("express")
local lfs = require("lfs")
local cjson = require("cjson")
local bp = require("body-parser")
local utils = require("utils")
local app = express()
numbers_try = {}
captcha_try = {}

local activate_captcha = utils.activate_captcha
local check_ban = utils.check_ban
local validate_uid = utils.validate_uid
local validate_answer = utils.validate_answer
local send_image = utils.send_image
local get_file_name = utils.get_file_name

local captcha_dir = '../captchas'
local captcha_image_dir = captcha_dir .. '/image'
local ask_image_dir = captcha_dir .. '/ask'
local numbers_image_dir = captcha_dir .. '/numbers'

app:use(bp.json({type = "application/json"}))
app:use(bp.urlencoded({type = "*/*"}))
app:use(utils.set_header)

app:get('/captcha/get_captcha/:ip', function(req, res)
    local ip = req.params.ip
    
    if check_ban(ip, res) then
        return
    end
    
    captcha_try[ip] = nil
    numbers_try[ip] = nil

    local captcha_json = get_random_file_name(captcha_dir, 'json')
    local file_path = captcha_dir .. "/" .. captcha_json
    local file = io.open(file_path, "r")
    local content = file:read("*a")
    file:close()
    local data = cjson.decode(content)
    activate_captcha("captcha_life_time.txt", file_path)
    
    res:status(200):send(data)
end)

app:get('/captcha/get_numbers_image/:uid/:ip', function(req, res)
    res:set("Content-Type", "image/png")
    
    local ip = req.params.ip
    local uid = req.params.uid
    
    
    if check_ban(ip, res) then
        return
    end
    
    if not validate_uid(uid, ip, res) then
        return
    end
    
    local file_path = get_file_name(numbers_image_dir, uid)
    
    activate_captcha("numbers_life_time.txt", file_path)
    
    send_image(file_path, numbers_image_dir, res)
end)


app:get('/captcha/get_ask_image/:uid/:numbers/:ip', function(req, res)
    res:set("Content-Type", "image/png")
    
    local ip = req.params.ip
    local uid = req.params.uid
    local numbers = req.params.numbers
    
    if check_ban(ip, res) then
        return
    end
    if not validate_uid(uid, ip, res) then
        return
    end
    if not validate_answer(uid, numbers, numbers_image_dir, '.png', res, true, ip) then
        res:status(404):send('Invalid')
        return
    end
    
    local file_path = get_file_name(ask_image_dir, uid)
    activate_captcha("ask_life_time.txt", file_path)
    
    send_image(file_path, ask_image_dir, res)
end)



app:get('/captcha/get_captcha_image/:uid/:numbers/:ip', function(req, res)
    res:set("Content-Type", "image/png")
    
    local ip = req.params.ip
    local uid = req.params.uid
    local numbers = req.params.numbers
    
    if check_ban(ip, res) then
        return
    end
    if not validate_uid(uid, ip, res) then
        return
    end
    if not validate_answer(uid, numbers, numbers_image_dir, '.png', res, true, ip) then
        res:status(404):send('Invalid')
        return
    end
    
    local file_path = get_file_name(captcha_image_dir, uid)
    activate_captcha("captcha_image_life_time.txt", file_path)
    
    send_image(file_path, captcha_image_dir, res)
end)


app:get('/captcha/validate_captcha/:uid/:answer/:ip', function(req, res)
    
    local ip = req.params.ip
    local answer = req.params.answer
    local uid = req.params.uid
    
    if check_ban(ip, res) then
        return
    end
    
    if not validate_uid(uid, ip, res) then
        return
    end
    
    if validate_answer(uid, answer, captcha_dir, '.json', res) then
        captcha_try[ip] = nil
        os.remove(captcha_dir .. '/' .. answer .. '_' .. uid .. '.json')
        os.remove(captcha_image_dir .. '/' .. uid .. '.png')
        os.remove(ask_image_dir .. '/' .. uid .. '.png')
        return
    else
        if inc_try_for_ip(captcha_try, ip, res) then
            res:status(404):send('Invalid')
        end
    end
end)

app:get('/captcha/validate_numbers/:uid/:numbers/:ip', function(req, res)
    
    local ip = req.params.ip
    local numbers = req.params.numbers
    local uid = req.params.uid
    
    if check_ban(ip, res) then
        return
    end
    
    if not validate_uid(uid, ip, res) then
        return
    end
    if validate_answer(uid, numbers, numbers_image_dir, '.png', res) then
        numbers_try[ip] = nil
        return
    else
        if inc_try_for_ip(numbers_try, ip, res) then
            res:status(404):send('Invalid')
        end
    end
end)

app:get('/captcha/ban/:ip', function(req, res)
    local ip = req.params.ip
    utils.ban(ip, res)
end)

app:listen(3000)