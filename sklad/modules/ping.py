#from modules.orders import queryDB
import socket


def ping(host, port=1433):
    try:
        socket.setdefaulttimeout(0.2)

        # AF_INET: address family (IPv4)
        # SOCK_STREAM: type for TCP (PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, port)

        # send connection request to the defined server
        s.connect(server_address)
        #s.close()
    except OSError as error:
        print(f"Error connecting to {host}:{port}: {error}")
        return False
    else:

        s.close()
        return True
