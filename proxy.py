# -*- coding: utf-8 -*-

import os, sys, _thread, socket
from dechunk import dechunk
import gzip, re

BACKLOG = 50 # how many pending connections queue will hold
MAX_DATA_RECY = 4096 # byte
DEBUG = False


def main():
    if(len(sys.argv) < 2):
        print("usage: proxy <port>")
        return sys.stdout
    
    host = ''
    port = int(sys.argv[1])
    print("host: ", host)
    print("port: ", port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        s.listen(BACKLOG)
    except OSError as e:
        if s:
            s.close()
        print("socket err", e)
        sys.exit(1)
    print("listening...") 
    while 1:
        conn, client_addr = s.accept()
        if(conn):
            print("accepted!")
        _thread.start_new_thread(proxy_thread, (conn, client_addr))

    s.close()


def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECY)
    first_line = request.decode().split('\n')[0]
    
    url = first_line.split(' ')[1]

    if(DEBUG):
        print("line: ",request.decode())
        print("url: ", url)
    
    http_pos = url.find('://')
    
    if(http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos+3):]
    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)
        
    webserver = ""
    port = -1
    if(port_pos == -1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    print("connect: ", webserver, port)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)
        whole_data = b""
        while 1:
            data = s.recv(MAX_DATA_RECY)
            if(len(data) > 0):
                whole_data+=data
            else:
                break
        if(whole_data.split(b"\r\n")[0] != b"HTTP/1.1 200 OK"):
            conn.send(whole_data)
        else:
            if(whole_data.split(b"\r\n")[3] != b"Content-Type: text/html; charset=utf-8"):
                conn.send(whole_data)
            else:
                if(whole_data.find(b'gzip') != -1):
                    print(whole_data)
                    decompressed_data = gzip.decompress(dechunk(whole_data.split(b"gzip")[1]))
                    #print(decompressed_data)
                    exchanged_data = re.sub(pattern='[<]title[>].+[<][/]title[>]', repl='<title>donghyeon</title>', string=decompressed_data.decode())
                    compressed_data = whole_data.split(b"gzip")[0] + b'gzip\r\n\r\n' + hex(len(gzip.compress(exchanged_data.encode()))).split('x')[1].encode() + b'\r\n' + gzip.compress(exchanged_data.encode()) + b'\r\n0\r\n\r\n'
                    conn.send(compressed_data)
                else:
                    conn.send(whole_data)
        s.close()
        conn.close()
    except OSError as e:
        if s:
            s.close()
        if conn:
            conn.close()
        print("runtime error: ", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
