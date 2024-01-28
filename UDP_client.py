import logging
import socket
import json


UDP_IP = "127.0.0.1"
UDP_PORT = 5000


console_logger = logging.getLogger("console_logger")
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


class UDP_IP_Client:
    @classmethod
    def connection_client_udp_ip(
        cls, data: list, ip: str = UDP_IP, port: int = UDP_PORT
    ) -> None:
        """
        Sends data to the server on the protocol UDP.

        :param data: Dictionary with data for sending.
        :param ip: IP-address server (by default "127.0.0.1").
        :param port: Server port (by default 5000).
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server = (ip, port)
            send_data = json.dumps(data).encode("utf-8")
            sock.sendto(send_data, server)
            console_logger.info(
                f"Send data: {send_data} to server: {server}. Successfully!"
            )
        except Exception as e:
            file_logger.error(f"Error occurred while sending data: {e}")
        finally:
            sock.close()
