#!/usr/bin/python

try:
    import socket
    import ssl
    import sys
    import pprint
    
    import identifiers
    
except ImportError as i_exc:
    sys.exit("Error on import: {}".format(i_exc))


class FeedReqClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)  # set to blocking
        try:
            self.sock.connect((identifiers.HOST, identifiers.PORT))
        except OSError as conn_exc:
            sys.exit("Client-side connection error encountered: {}".format(conn_exc))

        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile="server_cert.pem"
            )
        print("Created client")
    
    def authenticate_server(self):
        try:
            self.secure = self.context.wrap_socket(self.sock, server_side=False, keyfile="client_private.pem", 
                                                   certfile="client_cert.pem", password=identifiers.PW)
        except ssl.SSLError as ssl_exc:
            print("Error wrapping client-side socket: {}".format(ssl_exc))
            raise
        
        cert = self.secure.getpeercert()
        print(pprint.pformat(self.secure.getpeercert()))
        # if not cert or ("CPOU_FeedCat_Client") not in cert["

    def cleanup(self):
        self.secure.close()
        self.sock.close()


if __name__ == "__main__":

    try: 
        c = FeedReqClient()
    except Exception as cr_e:
        sys.exit("Error creating request: {}".format(cr_e))

    try:
        c.authenticate_server()
        c.secure.write('hello')
        print(c.secure.read(1024))
    except Exception as com_e:
        print("Error communicating: {}".format(com_e))
    finally:
        c.cleanup()

    
        
