import os, sys, _thread, socket

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
    
    while 1:
        print("...socket listening")
        conn, client_addr = s.accept()
        _thread.start_new_thread(proxy_thread, (conn, client_addr))

    s.close()


def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECY)
    first_line = request.decode().split('n')[0]
    url = first_line.split(' ')[1]

    if(DEBUG):
        print("line: ", first_line)
        print("url: ", url)
    
    http_pos = url.find('://')
    if(http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos+3):]
    
    port_pos = temp.find(":")


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

        while 1:
            data = s.recv(MAX_DATA_RECY)

            if(len(data) > 0):
                conn.send(data)
            else:
                break
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
