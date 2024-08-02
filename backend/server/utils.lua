local txt_db_dir = "../txt_db"

function get_root_path()
    local current_path = debug.getinfo(1).source:sub(2)
    local current_path = current_path:match("(.*[\\/])")
    return string.sub(current_path, 1, #current_path - 1)
end

function get_random_file_name(dir_path, file_type)
    local file_pool = {}
    for file in lfs.dir(dir_path) do
        if file:match("%." .. file_type .. "$") then
            table.insert(file_pool, file)
        end
    end
    local random_index = math.random(1, #file_pool)
    return file_pool[random_index]
end

function get_uid()
    return math.random(1, 1000) * os.time()
end

function get_file_name(dir, substring)
    local pfile = io.popen('ls "'..dir..'"')
    for file_name in pfile:lines() do
        if file_name:find(substring) then
            return dir .. "/" .. file_name
        end
    end
    pfile:close()
end

function activate_captcha(txt_name, file_path)
    local file = io.open(txt_db_dir .. "/" .. txt_name, "a")
    file:write(file_path .. " " .. os.time() .. "\n")
    file:close()
end

function check_ban(ip, res)
    local file = io.open(txt_db_dir .. "/" .. "ban_list.txt", "r")
    if not file then
        local file = io.open(txt_db_dir .. "/" .. "ban_list.txt", "w")
        file:write(1000 .. "\n")
        file:close()
        return nil
    end
    local ip_list = {}
    for line in file:lines() do
        table.insert(ip_list, line)
    end
    file:close()
    for i, _ip in ipairs(ip_list) do
        if ip:match(_ip) then
            res:status(403):send('ban')
            return true
        end
    end
end

function ban(ip, res)
    local file = io.open(txt_db_dir .. "/" .. "ban_list.txt", "a")
    file:write(ip .. "\n")
    file:close()
    res:status(403):send('ban')
end 

function validate_answer(uid, answer, dir_path, file_type, res, agressive, ip)
    local file_pool = {}
    for file_name in lfs.dir(dir_path) do
        if string.find(file_name, uid) then
            local uid_start_index = string.find(file_name, "_")
            local file_uid = string.sub(file_name, uid_start_index + 1, #file_name - #file_type)
            local file_answer = string.sub(file_name, 1, uid_start_index - 1)
            if file_uid == uid and file_answer == answer then
                if agressive then
                    return true
                end
                res:status(200):send('Valid')
                return true
            end
        end
    end
    if agressive then
        ban(ip, res)
        return false
    end
    return false
end



function validate_uid(uid, ip, res)
    if #uid ~= 32 then
        ban(ip, res)
        return false
    end
    return true
end

function send_image(file_path, dir, res)
    local new_uid = get_uid()
    local new_file_path = dir .. "/" .. new_uid .. ".png"
    
    local suc, err = os.rename(file_path, new_file_path)
    res:status(200):sendFile(new_file_path)
    os.rename(new_file_path, file_path)
end

function set_header(req, res, next)
    res:set('Access-Control-Allow-Origin', '*')
    res:set('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    res:set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    next()
end

function inc_try_for_ip(dict_try, ip, res)
    if dict_try[ip] == 4 then
        ban(ip, res)
        return false
    end
    
    if dict_try[ip] then
        dict_try[ip] = dict_try[ip] + 1
    else
        dict_try[ip] = 1
    end
    return true

end

return {
    ban = ban,
    inc_try_for_ip = inc_try_for_ip,
    check_ban = check_ban,
    get_uid = get_uid,
    get_root_path = get_root_path,
    get_file_name = get_file_name,
    get_random_file_name = get_random_file_name,
    validate_uid = validate_uid,
    validate_answer = validate_answer,
    activate_captcha = activate_captcha,
    send_image = send_image,
    set_header = set_header
}