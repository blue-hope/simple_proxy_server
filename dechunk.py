def dechunk(data):
    # byte data input
    new_data_arr = data.split(b'\r\n')
    new_data_arr = new_data_arr[2:]
    new_data = b'\r\n'.join(new_data_arr)
    dechunk_data_arr = list()
    return_data = b""
    tmp_data = b""
    cnt = 0
    skip_loop_start = 999999999
    skip_loop_end = -1
    for j, i in enumerate(new_data):
        if j >= skip_loop_start and j < skip_loop_end:
            continue
        if(bytes([i]) != b'\r'):
            tmp_data += bytes([i])
        else:
            data_size = tmp_data.decode()
            tmp_data = b""
            dechunk_data_arr.append(new_data[j+2:j+int(data_size, 16)+2])
            skip_loop_start = j+1
            skip_loop_end = j+1 + int(data_size, 16)+2 
            return_data += dechunk_data_arr[cnt]
            cnt += 1
    return return_data