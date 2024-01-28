from datetime import datetime
from pathlib import Path
import logging
import socket
import json


console_logger = logging.getLogger("custom_logger")
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)
console_logger.addHandler(console_handler)
console_logger.propagate = False


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


UDP_IP = "127.0.0.1"
UDP_PORT = 5000
BUFFER_SIZE = 1024
BASE_DIR = Path()


class UDP_IP_Server:
    """
    Runs the UDP_IP server.

    :param ip: IP address to bind the server (default is "127.0.0.1").
    :param port: Port to bind the server (default is 5000).
    """

    def run_server_socket_udp_ips(self, ip: str = UDP_IP, port: int = UDP_PORT) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = (ip, port)
        sock.bind(server)
        console_logger.info(f"Starting socket UDP_IP server: on {UDP_IP}:{UDP_PORT}")
        try:
            while True:
                data, address = sock.recvfrom(BUFFER_SIZE)
                console_logger.info(f"Received data: {data} from: {address}")
                data = data.decode("utf-8")
                data_dict = json.loads(data)
                self.data_json_save(data_dict)

        except KeyboardInterrupt:
            file_logger.error(
                f"Server at {UDP_IP}:{UDP_PORT} is shutting down due to a keyboard interrupt."
            )
        except Exception as e:
            file_logger.error(f"An unexpected error occurred: {e}")
        finally:
            sock.close()

    def data_json_save(self, data_list: list) -> None:
        """
        Saves received data as JSON in a file.

        :param data_dict: Dictionary containing data to be saved.
        """
        try:
            data_path = Path("storage/data.json")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temp_list = []
            temp_list.append({current_time: data_list})
            if data_path.exists() and data_path.stat().st_size > 0:
                with open(data_path, "r", encoding="utf-8") as fh:
                    existing_data = json.load(fh)
                    existing_data.append({current_time: data_list})
                    print(existing_data)
                with open(data_path, "w", encoding="utf-8") as fh:
                    json.dump(
                        existing_data, fh, indent=4, ensure_ascii=False, default=str
                    )

            else:
                with open(data_path, "w", encoding="utf-8") as fh:
                    json.dump(temp_list, fh, indent=4, ensure_ascii=False, default=str)
            console_logger.info(f"Data saved to {data_path}")
        except Exception as e:
            file_logger.error(f"Error occurred while saving data: {e}")
