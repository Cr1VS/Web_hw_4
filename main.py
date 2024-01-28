from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from threading import Thread
from pathlib import Path
import urllib.parse
import mimetypes
import logging
import socket
import json


BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = "0.0.0.0"
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 5000


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        """Handle POST requests."""
        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size))

        # Send data to the socket server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()

        # Send a redirect response
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests."""
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            # Serve the main HTML file
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            # Serve a specific HTML file
            self.send_html_file("message.html")
        else:
            if Path().joinpath(pr_url.path[1:]).exists():
                # Serve static files
                self.send_static()
            else:
                # Serve an error page
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200) -> None:
        """Send an HTML file as the response."""
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self) -> None:
        """Send a static file as the response."""
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def seve_to_file(data) -> None:
    """Save data to a JSON file."""
    data_parse = urllib.parse.unquote_plus(data.decode())
    data_dict = {
        key: value for key, value in [el.split("=") for el in data_parse.split("&")]
    }
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temp_list = []
    data_path = Path("storage/data.json")
    if data_path.exists() and data_path.stat().st_size > 0:
        with open(data_path, "r") as fh:
            old_data = json.load(fh)

        data_save = old_data
        record = {
            current_time: {
                "Username": data_dict["username"],
                "Message": data_dict["message"],
            }
        }
        data_save.append(record)

        with open(data_path, "w", encoding="utf-8") as fh:
            json.dump(data_save, fh, indent=4, ensure_ascii=False, default=str)
    else:
        temp_list.append({current_time: data_dict})
        with open(data_path, "w", encoding="utf-8") as fh:
            json.dump(temp_list, fh, indent=4, ensure_ascii=False, default=str)


def run_socket_server(host, port) -> None:
    """Run the socket server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    console_logger.info(f"Starting socket server on {host}:{port}")
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            console_logger.info(f"Socket received {address}:{msg}")
            seve_to_file(msg)
    except KeyboardInterrupt:
        console_logger.info(f"Server on {host}:{port} stopped by user.")
    except Exception as e:
        file_logger.error(f"Unexpected error: {str(e)}")
    finally:
        server_socket.close()


def run_http_server(host, port) -> None:
    """Run the HTTP server."""
    address = (host, port)
    http_server = HTTPServer(address, HttpHandler)
    console_logger.info(f"Starting http server on {host}:{port}")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        console_logger.info(f"Server on {host}:{port} stopped by user.")
    except Exception as e:
        file_logger.error(f"Unexpected error: {str(e)}")
    finally:
        http_server.server_close()


if __name__ == "__main__":
    # Configure console logger
    console_logger = logging.getLogger("console_logger")
    console_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    console_logger.addHandler(console_handler)
    console_logger.propagate = False

    # Configure file logger
    file_logger = logging.getLogger("file_logger")
    file_logger.setLevel(logging.ERROR)
    file_handler = logging.FileHandler("Error.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        logging.Formatter(
            "%(levelname)s - %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    file_logger.addHandler(file_handler)
    file_logger.propagate = False

    # Start HTTP and socket servers in separate threads
    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()
