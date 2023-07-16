from keygeneration.client_keygeneration import *
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

#decrypting VC0 with RSA, Rpr.
def decrypt_vc0(vc0:bytes,kpr):
	dvc0 = b""
	cipher = PKCS1_OAEP.new(kpr)

	# decrypt the vc0 with the private key
	for i in range(0,len(vc0),256):
		input_data = vc0[i:i+256]
		decrypted_data = cipher.decrypt(input_data)
		dvc0 += decrypted_data
	return dvc0

def decrypt_vci(chunk:bytes,key:bytes,iv:bytes): # decrypt with AES-256 
	cipher = AES.new(key, AES.MODE_CBC, iv)
	decrypted_vci = cipher.decrypt(chunk)
	return decrypted_vci

def decrypt(chunks:bytes,AESkeys:list,iv,kpub,vc0_decrypted:bytes):
	decrypted = b""+vc0_decrypted

	kcount = 0
	for i in range(1310720,len(chunks),1024000):
		if i == 1310720: 
			chunk = chunks[i:i+1024000] #vc1 chunk
			decrypted += decrypt_vci(chunk,AESkeys[0],iv)
			kcount+=1
		else:
			chunk = chunks[i:i+1024000] #vc2...vci chunk
			decrypted += decrypt_vci(chunk,AESkeys[kcount],iv)
			kcount+=1
	return decrypted

def main_decrypt(enc_video,iv):

		kpr = get_prkey()
		rmac = get_mac()

	
		vc0_len  = 1310720 # 102400 --> RSA-2048 ---> 1310720
		vc0 = decrypt_vc0(enc_video[:vc0_len],kpr)
		vid = vid_generation(vc0[:16])

		AESkeys = []
		AESkeys.append(ecc_key_1_generation(rmac,vid))
		key = AESkeys[0]
		for i in range((len(enc_video)//1024000)-2):
			keyi = ecc_key_i_generation(rmac,key)
			AESkeys.append(keyi)
			key = keyi

		# print(AESkeys)
		print("Buffering...⏳⏳⏳⏳⏳⏳") #####
		m = decrypt(enc_video,AESkeys,iv,kpr,vc0)

		m = m.rstrip(b'\x00')
		return m
