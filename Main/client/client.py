#!/usr/bin/env python3
import socket
import threading
import re
import base64
import keygeneration.client_main as client_main
from moviepy.editor import VideoFileClip

def playvideo(video_path):
	# Load the video clip
	video_clip = VideoFileClip(video_path)

	# Play the video clip
	video_clip.preview()

	# Close the video clip after playback
	video_clip.close()

	return True

def get_decrypted_video(enc_video,iv):
	dec_video = client_main.main_decrypt(enc_video,iv)
	return dec_video


def check_email_address(email_address):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email_address):
        return True
    else:
        return False

email = input("Enter Email : ")
if not check_email_address(email):
	print("🛑Invalid Email")
	exit(1)

password = input("Enter Password : ")
if not password:
	print("🛑Password shouldn't be empty..")
	exit(1)

password = base64.b64encode(password.encode())


target = input("Enter your assigned server address : ")
port = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target,port))

def recieve():
	while True:
		try:
			message = client.recv(1024).decode("ascii")   #1
			print(message)
			
			creds = email.encode("ascii")+b","+password

			client.send(creds)		#c1
			
			login_status = client.recv(1024).decode("ascii")	#2

			if login_status == "Login failed..":
				print(login_status)
				exit(1)
			print(login_status)

			playlist = client.recv(1024).decode("ascii")	#3
			print(playlist)

			choice = input()
			while (int(choice) not in [1,2,3,4]):
				if choice == "0" or choice=="00":
					exit(1)
				print("Invalid Option..")
				choice =input("Enter again :")
			client.send(choice.encode("ascii"))		#c3

			print(f"Sending Your Request for Video {choice}...")
			#printing receiving video
			recv_status = client.recv(25).decode("ascii")	#4
			print(recv_status)

			# receive iv
			iv = client.recv(16)		#5
			# receive video
			chunk_size = 1024
			received_data = b""

			
			while True:
			    chunk = client.recv(chunk_size)		#6
			    if b"DONE" in chunk:
			        break
			    received_data += chunk

			# decrypting video
			video = get_decrypted_video(received_data,iv)
			video = video.rstrip(b"\x00")		#removing padded bytes
			with open(f"outputs/{choice}.mp4","wb") as f:
				f.write(video)
				print("\nPlaying Video ▶️ ")

			final_status = playvideo(f"outputs/{choice}.mp4")
			if final_status:
				print("\n✅ It was done :)")
				exit(1)


		except Exception as e:
			print("Error occurred!")
			if e:
				print("🛑  Oops, Thats not a Valid Private Key")
				print("🛑 1. Check your Registered MAC\n2. Enter Private_key of registered public key")
				print("🛑 Error Message : ",e)
				print("🛑 If none of these works send Error Message to the ADMIN")
			client.close()
			break

r_thread = threading.Thread(target=recieve)
r_thread.start()
