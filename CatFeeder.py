#!/usr/bin/python

try:
    import ssl
    import socket   
    import pprint
    
    import RPi.GPIO as GPIO
    import time
    import sys
    
    import logging
    
    import identifiers

except ImportError as i_exc:
    sys.exit("Import error on {}".format(i_exc))

logging.basicConfig(filename="feed_requests.log",
                    format="%(asctime)s - %(name)s - %(levelname)-5s - %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


class CatFeedServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Do I need to set sock options?
        
        try:
            self.sock.bind((identifiers.HOST, identifiers.PORT))
        except self.sock.error as se:
            logger.error("Binding error: {}".format(se))
            raise
        
        self.sock.listen(2)
        logger.info("Created server. Listening on port {}".format(identifiers.PORT))

        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile="client_cert.pem"
            )
        logger.debug("Created context")

    def authenticate_client(self, client_sock):
        try:
            self.secure = self.context.wrap_socket(client_sock, server_side=True, keyfile="server_private.pem", 
                                                   certfile="server_cert.pem", password=identifiers.PW)
        except ssl.SSLError as ssl_e:
            logger.error("Error wrapping server-side client socket: {}".format(ssl_e))
            raise
        
        logger.info("Accepted incoming request from {}, with cypher {}".format(self.secure.getpeername(),
                                                                               self.secure.cipher()))
        
        cert = self.secure.getpeercert()
        print(pprint.pformat(self.secure.getpeercert()))
        # if not cert or ("CPOU_FeedCat_Client") not in cert["
   
    def cleanup(self):
        self.secure.close()
        self.sock.close()


def rotate():
    GPIO.setmode(GPIO.BCM)  # GPIO numbering
    GPIO.setup(18, GPIO.OUT)

    try:
        servo = GPIO.PWM(18, 50)  # channel, freq

        try:
            servo.start(7.5)  # duty cycle
            logger.info("Started")
            for i in range(0, 3):
                dc = 2.5 if (i % 2 == 0) else 7.5
                servo.ChangeDutyCycle(dc)
                time.sleep(3)
        except:
            logger.error("Error operating servo")
        finally:
            servo.stop()

    except Exception as s_exc:
        logger.error("Error instantiating servo instance: {}".format(s_exc))
        sys.exit(1)
    finally:
        GPIO.cleanup()
        logger.info("Stopped")


if __name__ == '__main__':
    try:
        s = CatFeedServer()
    except Exception as serv_exc:
        logger.error("Error creating server: {}".format(serv_exc))
        sys.exit(1)

    try:
        client, fromaddr = s.sock.accept()
        s.authenticate_client(client)
        data = s.secure.read(1024)
        s.secure.write(data)
    except Exception as conn_exc:
        logger.error("Error receiving connection: {}".format(conn_exc))
        sys.exit(1)
    finally:
        s.cleanup()
