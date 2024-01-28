import rsa
from base64 import b64encode, b64decode

publicKey, privateKey = rsa.newkeys(512)

def encryption(message):
    message = rsa.encrypt(message.encode(), publicKey)
    message = b64encode(message).decode()
    return message

def decryption(message):
    message = b64decode(message.encode())
    message = rsa.decrypt(message, privateKey).decode()
    return message

