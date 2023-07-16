#!/usr/bin/env python3
from keygeneration.server_keygeneration import *
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import sqlite3
import os

#encrypting VC0 with RSA, Rpub.
def encrypt_vc0(vc0:bytes,kpub):
	evc0 = b""
	cipher = PKCS1_OAEP.new(kpub)

	# Encrypt the vc0 with the public key
	for i in range(0,len(vc0),200):
		input_data = vc0[i:i+200]
		encrypted_data = cipher.encrypt(input_data)
		evc0 += encrypted_data
	return evc0

def encrypt_vci(chunk:bytes,key:bytes,iv:bytes): # encrypt with AES-256 
	cipher = AES.new(key, AES.MODE_CBC, iv)
	encrypted_vci = cipher.encrypt(chunk)
	return encrypted_vci

def encrypt(chunks:bytes,AESkeys:list,iv,kpub):
	encrypted = b""
	vc0 = encrypt_vc0(chunks[:1024000],kpub) #first 1 mb
	encrypted += vc0

	kcount = 0
	for i in range(1024000,len(chunks),1024000):
		if i == 1024000: 
			chunk = chunks[i:i+1024000] #vc1 chunk
			encrypted += encrypt_vci(chunk,AESkeys[0],iv)
			kcount+=1
		else:
			chunk = chunks[i:i+1024000] #vc2...vci chunk
			encrypted += encrypt_vci(chunk,AESkeys[kcount],iv)
			kcount+=1
	return encrypted

def pad(chunks:bytes):
	n = len(chunks)%1024000
	if n == 0:
		return chunks

	pads = (1024000 - n) * b'\x00'
	chunks = chunks + pads
	return chunks

def main_encrypt(video_path,email,db_path):
	
	#database connection to fetch pub key of user

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	with open(video_path,"rb") as f:
		chunks =  f.read()	
		chunks = pad(chunks)
	
		cursor.execute("SELECT pubk,mac FROM user WHERE email=?",(email,))
		row = cursor.fetchone()

		kpub = get_pubkey(row[0])

		print(kpub)

		rmac = get_mac(row[1])


		iv = get_random_bytes(16)

		AESkeys = []
		AESkeys.append(ecc_key_1_generation(rmac,vid_generation(video_path)))
		key = AESkeys[0]
		for i in range((len(chunks)//1024000)-2):
			keyi = ecc_key_i_generation(rmac,key)
			AESkeys.append(keyi)
			key = keyi
		c = encrypt(chunks,AESkeys,iv,kpub)
	
		return c,iv