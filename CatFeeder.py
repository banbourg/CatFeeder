#!/usr/bin/python

try:
    import sys
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

logging.basicConfig(# filename="feed_requests.log",
                    format="%(asctime)s - %(name)s - %(levelname)-5s - %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


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
        except Exception as servo_e:
            logger.error("Error operating servo: {}".format(servo_e))
        finally:
            servo.stop()

    except Exception as s_exc:
        logger.error("Error instantiating servo instance: {}".format(s_exc))
        sys.exit(1)
    finally:
        GPIO.cleanup()
        logger.info("Stopped")


def handle(a_connstream):
    data = a_connstream.recv(1024)
    while data:
        print(data)
        data = a_connstream.recv(1024)

    if data == b"feed":
        # rotate()
        print("woop")


if __name__ == '__main__':

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile="server_cert.pem", keyfile="server_private.pem", password=identifiers.PW)
    context.load_verify_locations(cafile="client_cert.pem")
    
    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.bind((identifiers.PI_IP, identifiers.PORT))
    bindsocket.listen(5)
    logger.info("Created server socket, listening on port {}".format(identifiers.PORT))

    while True:
        newsocket, fromaddr = bindsocket.accept()
        logger.info("Received incoming connection from {}".format(fromaddr))
        connstream = context.wrap_socket(newsocket, server_side=True)
        
        cert = connstream.getpeercert()
        try:
            ssl.match_hostname(cert, identifiers.CLIENTNAME)
            handle(connstream)
        except ssl.CertificateError as cert_err:
            logger.error(cert_err)
        finally:
            connstream.close()
