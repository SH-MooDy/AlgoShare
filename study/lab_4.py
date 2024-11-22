from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
# Fill in start.
tcpSerSock.bind((sys.argv[1], 8888))  # IP 및 포트 바인딩
tcpSerSock.listen(5)                  # 최대 연결 수 설정
# Fill in end.

while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(1024).decode()  # Fill in start.		# Fill in end.
    print(message)

    # Extract the filename from the given message
    try:
        print(message.split()[1])
        filename = message.split()[1].partition("/")[2]
        print(filename)
        fileExist = "false"
        filetouse = "/" + filename
        print(filetouse)

        # Check whether the file exists in the cache
        try:
            f = open(filetouse[1:], "r")
            outputdata = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n".encode())
            # Fill in start.
            for line in outputdata:
                tcpCliSock.send(line.encode())
            # Fill in end.
            print('Read from cache')

        except IOError:
            if fileExist == "false":
                # Create a socket on the proxyserver
                c = socket(AF_INET, SOCK_STREAM)  # Fill in start.		# Fill in end.
                hostn = filename.replace("www.", "", 1)
                print(hostn)
                try:
                    # Connect to the socket to port 80
                    # Fill in start.
                    c.connect((hostn, 80))
                    # Fill in end.

                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = c.makefile('r', 0)
                    fileobj.write("GET / HTTP/1.0\r\nHost: {}\r\n\r\n".format(hostn))
                    fileobj.flush()

                    # Read the response into buffer
                    # Fill in start.
                    buff = fileobj.readlines()
                    # Fill in end.

                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                    tmpFile = open("./" + filename, "wb")
                    # Fill in start.
                    for line in buff:
                        tmpFile.write(line.encode())
                        tcpCliSock.send(line.encode())
                    # Fill in end.

                except Exception as e:
                    print("Illegal request", e)
            else:
                # HTTP response message for file not found
                # Fill in start.
                tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
                tcpCliSock.send("Content-Type:text/html\r\n".encode())
                tcpCliSock.send("\r\n".encode())
                tcpCliSock.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())
                # Fill in end.

        tcpCliSock.close()
    except IndexError:
        print("Invalid request received")
