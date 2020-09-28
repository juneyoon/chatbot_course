jupyter:
	nohup jupyter notebook --ip=0.0.0.0 --port=5000 --no-browser &
client_server:
	cd client; nohup http-server -o --cors -S -C cert.pem &
server:
	cd server; nohup python server.py &
