from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import pathlib
import socket
from threading import Thread
import urllib.parse


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("front-init/index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("front-init/message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("front-init/error.html", 404)

    def do_POST(self):
        socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        # with socket_send as s:
        socket_send.sendto(data_parse.encode(), ("127.0.0.1", 5000))
        print("Отправили данные")
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("127.0.0.1", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_udp_socket():
    file_name = pathlib.Path("front-init/storage/data.json")
    socket_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Стартовал сервер сокета")
    socket_recv.bind(("127.0.0.1", 5000))
    dict_to_json = {}
    try:
        while True:
            data = socket_recv.recv(1024).decode()
            print(f"Received data: {data}")
            print(type(data))
            data_dict = {
                key: value for key, value in [el.split("=") for el in data.split("&")]
            }
            print(data_dict)
            dict_to_json[str(datetime.now())] = data_dict
            with open(file_name, "a") as fh:
                json.dump(dict_to_json, fh)

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        socket_recv.close()


if __name__ == "__main__":
    thread_http_server = Thread(target=run_http_server)
    thread_http_server.start()
    thread_udp_socket = Thread(target=run_udp_socket)
    thread_udp_socket.start()
