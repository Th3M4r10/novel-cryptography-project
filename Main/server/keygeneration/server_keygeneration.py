#!/usr/bin/env python3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.number import *
import hashlib
import base64
import os


def get_pubkey(pubk):
	# Get public key from database
	public_key = base64.b64decode(pubk)
	public_key = RSA.import_key(public_key)
	return public_key

def get_mac(mac):
	return mac


def vid_generation(video_path):
	vc0_chunk = open(video_path,"rb")
	vc0_16bytes = vc0_chunk.read(16)
	return bytes_to_long(vc0_16bytes)

def ecc_key_1_generation(rmac,vid): # Used in the encryption VC0
	
	data = long_to_bytes(vid) + bytes.fromhex(rmac.replace(':','').replace("-",""))
	h = hashlib.sha256(data).digest()
	x_key = h[:16]
	#convert the key to an int
	x = bytes_to_long(x_key)

	#x^3 + VID * x + rmac
	key1 = x**3 + vid * x + int(rmac.replace(':','').replace("-",""),16)
	key1 = str(key1).encode() # cant convert it to int as it require 50 bytes
	key1 = hashlib.sha256(key1).digest()
	return key1
def ecc_key_i_generation(rmac,key): # Used in the encryption VC1

	data = key + bytes.fromhex(rmac.replace(':','').replace("-",""))
	h = hashlib.sha256(data).digest()
	x_key = h[:16]
	#convert the key to an int
	x = bytes_to_long(x_key)

	#x^3 + (Key_i-1) * x + rmac
	key = x**3 + bytes_to_long(key) * x + int(rmac.replace(':','').replace("-",""),16)
	key = str(key).encode()
	keyi = hashlib.sha256(key).digest()
	return keyi