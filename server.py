import os
import socket
from datetime import datetime


class SocketServer:
    def __init__(self):
        self.bufsize = 1024

        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()

        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def run(self, ip, port):
        """서버 실행"""

        # 소켓 생성
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.sock.bind((ip, port))
        self.sock.listen(10)

        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:

                # 클라이언트의 요청 대기
                clnt_sock, req_addr = self.sock.accept()

                clnt_sock.settimeout(5.0)

                print("Request message...\r\n")

                request = b""

                while True:
                    try:
                        data = clnt_sock.recv(self.bufsize)

                        if not data:
                            break

                        request += data

                    except socket.timeout:
                        break

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d-%H-%M-%S"
                )

                filename = (
                    self.DIR_PATH +
                    "/" +
                    timestamp +
                    ".bin"
                )

                with open(filename, "wb") as file:
                    file.write(request)
                
                header = request.split(
                    b"\r\n\r\n",
                    1
                )[0]

                boundary = None

                for line in header.split(b"\r\n"):

                    if b"boundary=" in line:

                        boundary = line.split(
                            b"boundary="
                        )[1].strip()

                        break

                if boundary is not None:

                    boundary = b"--" + boundary
                    parts = request.split(boundary)

                    for part in parts:

                        if b'name="image"' in part:

                            image_data = part.split(
                                b"\r\n\r\n",
                                1
                            )[1]

                            if image_data.endswith(b"\r\n"):
                                image_data = image_data[:-2]

                            with open("image.jpg", "wb") as file:
                                file.write(image_data)


                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)

                # 클라이언트 소켓 닫기
                clnt_sock.close()


        except KeyboardInterrupt:

            print("\r\nStop the server...")


        # 서버 소켓 닫기
        self.sock.close()


if __name__ == "__main__":

    server = SocketServer()

    server.run("127.0.0.1", 8000)