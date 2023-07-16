#!/usr/bin/env python3
import socket
import threading
import re
import keygeneration.server_main as server_main
import sqlite3
import base64
import os


# host = '127.0.0.1'
host = '0.0.0.0'
port = 9999

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
print("Server is listening")
server.listen()

clients = ["test"]
emails = ["test@gmail.com"]


def get_encrypted_video(choice,email):
	root = os.getcwd()
	db_path = "/".join(root.split("/")[:-2])+"/database.db"
	video_path = "/".join(root.split("/"))+"/videos/"+choice+".mp4"
	
	enc_video,iv = server_main.main_encrypt(video_path,email,db_path)
	return enc_video,iv
def handle(client):
	while True:
		try:
			root = os.getcwd()
			db_path = "/".join(root.split("/")[:-2])+"/database.db"
			#database connection
			conn = sqlite3.connect(db_path)		
			cursor = conn.cursor()

			creds = client.recv(1024).decode("ascii")		#c1
			email = creds.split(",")[0]
			if email:
				print(f"Email of the client is {email} ")    # printed on server console
				emails.append(email)
				clients.append(client)


			password = creds.split(",")[1]
			password = base64.b64decode(password).decode("ascii")

			cursor.execute("SELECT * FROM user WHERE email = ? AND password = ?", (email, password))
			row = cursor.fetchone()

			if row is None:
				client.send("Login failed..".encode("ascii"))	#2

				break

			print(f"{email} login success")
			client.send("Login Success..".encode("ascii"))	#2

			playlist = """
		-------------------------------------------------
		Playlist : 
			1. What is cryptography
			2. Learn about RSA
			3. Digital Signatures
			4. AES security
			0. Exit
		Choose any one video from the playlist(1/2/3/4) : """

			client.send(playlist.encode("ascii"))  #3
			choice = client.recv(2).decode("ascii") 	#c3
			print(choice)
			if choice:
				print(f'{email} choosed {choice}')

			video,iv = get_encrypted_video(choice,email)

			client.send("Receiving video chunks...".encode("ascii"))	#4

			client.send(iv)		#5
			
			# sending encrypted raw video data
			chunk_size = 1024
			offset = 0
			while offset < len(video):
				chunk = video[offset:offset+chunk_size]
				client.send(chunk)			#6
				offset += len(chunk)
			client.send("DONE".encode("ascii"))	#7

		except Exception as e:
			client.close()
			print(e)
			print(f'{email} disconnected..')
			break
def recieve():
	while True:
		client, address = server.accept()
		print(f"Connected with {str(address)}")		# printed on server console
		client.send("Connected to the server! ".encode("ascii"))  #1

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()
recieve()