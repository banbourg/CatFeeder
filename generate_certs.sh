#!/bin/bash

echo -n "Would you like to create a certificate for the server or the client? [server/client]: "
read name
echo -n "Pick max cert. duration in years (max. 65): "
read years

days=$((years * 365))
echo "Certificate will be valid for ${days} days"

openssl genrsa -des3 -out ${name}_private.pem 2048

openssl rsa -in ${name}_private.pem -outform PEM -pubout -out ${name}_public.pem

openssl req -new -x509 -key ${name}_private.pem -out ${name}_cert.pem -days ${days}
