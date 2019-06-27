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
    first_line = request.split('n')[0]
    print("line: ", first_line)

if __name__ == '__main__':
    main()