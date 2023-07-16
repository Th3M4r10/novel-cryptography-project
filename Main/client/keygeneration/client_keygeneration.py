#!/usr/bin/env python3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.number import *
import hashlib
import os
import re

def get_prkey():
	private_key_file_path = input(r"Enter your private_key file absolute path : ")
	
	# if os.name == "nt": # for windows
	
	if not os.path.exists(private_key_file_path):
		print("File not found")
		exit(1)
	if (os.path.splitext(private_key_file_path)[1] != ".pem"):
		print("Private key extension should be '.pem'")
		exit(1)
	private_key_file = open(private_key_file_path,"rb")
	private_key = RSA.import_key(private_key_file.read())
	private_key_file.close()
	return private_key

def get_mac():
    mac_address = input("Enter MAC address (As you entered on Registration) -  ").strip()
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$"
    is_valid_mac = re.match(pattern, mac_address)

    if not is_valid_mac:
    	print("Invalid MAC, MAC format (xx:xx:xx:xx:xx:xx)")
    	exit(1)
    return mac_address

def vid_generation(vc0_16bytes):
	
	return bytes_to_long(vc0_16bytes)

def ecc_key_1_generation(rmac,vid): # Used in the encryption VC1
	
	data = long_to_bytes(vid) + bytes.fromhex(rmac.replace(':','').replace("-",""))
	h = hashlib.sha256(data).digest()
	x_key = h[:16]
	#convert the key to an int
	x = bytes_to_long(x_key)

	#x^3 + VID * x + rmac
	key1 = x**3 + vid * x + int(rmac.replace(':','').replace("-",""),16)
	key1 = str(key1).encode()
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