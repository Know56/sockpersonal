import socket
import threading
from ping3 import verbose_ping
import time
import ssl
import sys
import os

#----------------------------------------------------------------------------------------------------------Servidor

class Socket_Personalizado:
    def __init__(self):
        self.clientes_conectados = []
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile="device.crt", keyfile="server.key")

    def timer_on(self, running_timer):
        while running_timer.is_set():
            try:
                verbose_ping('192.168.50.1', count=1) #Change this for the ip router
            except Exception as e:
                print(f"[PING ERROR] {e}")
            time.sleep(60)


    def handle_client(self, connection, addr):
        print(f"{time.ctime()} Connected by {addr}")
        connection.send("Welcome".encode())
        self.clientes_conectados.append(connection)

        while True:
            try:
                data = connection.recv(1024)
                if not data:
                    break
                mensaje = f"[{addr}] {data.decode()}"
                print(mensaje)

                for cliente in self.clientes_conectados:
                    if cliente != connection:
                        try:
                            cliente.send(mensaje.encode())
                        except Exception as e:
                            print(f"Error sending message to {cliente.getpeername()}: {e}")
            except Exception as e:
                print(f"Error handling message from {addr}: {e}")
                break

        self.clientes_conectados.remove(connection)
        connection.close()

    def ssl_server(self):
        service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        service.bind(('0.0.0.0', 4444))#Change this for the port "0.0.0.0" is public ip and private ip
        service.listen(30)
        print("Waiting for secure connections... (Ctrl+C to stop)")

        while True:
            try:
                conn, addr = service.accept()
                print(f"Incoming connection from {addr}")
                secure_socket = self.context.wrap_socket(conn, server_side=True)
                print(f"Secure connection established with {addr}")
                thread = threading.Thread(target=self.handle_client, args=(secure_socket, addr))
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                continue
    

    def thread(self):
        timer = threading.Event()
        timer.set()
        t = threading.Thread(target=self.timer_on, args=(timer,))
        t.start() 

#-------------------------------------------------------------------------------------------------Cliente




class Cliente_Personalizado:

    def __init__(self):
        self.d = None

    def connect_to_server(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                wrapped = ctx.wrap_socket(sock, server_hostname='colegiosanmarcos.zapto.org') #Change this for you domain
                wrapped.connect(('colegiosanmarcos.zapto.org', 4444)) # Change this for you domain and port
                print("¡Conectado al servidor!")
                self.d = wrapped
                return wrapped
            except Exception as e:
                print(f"Error al conectar: {e}. Reintentando en 30 min…")
                time.sleep(1800)

    def check_connection(self):
        while True:
            try:
                self.d.send(b"ping")
                response = self.d.recv(1024)
                if not response:
                    print("Servidor inactivo. Reconectando…")
                    self.d.close()
                    self.connect_to_server()
            except (socket.error, ssl.SSLError):
                print("Error de conexión. Intentando reconectar…")
                try:
                    self.d.close()
                except:
                    pass
                self.connect_to_server()
            time.sleep(10)

    def thread_1(self):
        threading.Thread(target=self.check_connection, daemon=True).start()

    def get_resource_path(self, filename):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, filename)
        return filename

    def abrir_pdf(self, nombre_archivo):
        pdf_path = self.get_resource_path(nombre_archivo)
        try:
            os.startfile(pdf_path)
        except Exception as e:
            print(f"Error al abrir el PDF: {e}")
