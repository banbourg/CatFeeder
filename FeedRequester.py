try:
    import socket
    import ssl
    import sys
    import pprint
    
    import identifiers
    
except ImportError as i_exc:
    sys.exit("Error on import: {}".format(i_exc))

if __name__ == "__main__":

    context = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile="server_cert.pem"
    )
    context.load_cert_chain("client_cert.pem", keyfile="client_private.pem", password=identifiers.PW)

    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=identifiers.HOSTNAME)
    conn.connect((identifiers.HOST, identifiers.PORT))
    # cert = conn.getpeercert()

    conn.send(b"feed")

    conn.close()
