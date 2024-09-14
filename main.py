try:
    import usocket as socket
except:
    import socket
from time import sleep
from template import html_template
import json

esp32_ip = ""

def urldecode(encoded_str):
    hex_chars = "0123456789ABCDEFabcdef"
    decoded_str = ""
    i = 0
    while i < len(encoded_str):
        if encoded_str[i] == '%' and i + 2 < len(encoded_str) and encoded_str[i+1] in hex_chars and encoded_str[i+2] in hex_chars:
            decoded_str += chr(int(encoded_str[i+1:i+3], 16))
            i += 3
        else:
            decoded_str += encoded_str[i]
            i += 1
    return decoded_str

def close_ap():
    s.close()
    sleep(1)
    ap.active(False)
    print("Access Point closed")
    return

def connect_to_wifi(ssid, password):
    global esp32_ip
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)

    while not station.isconnected():
        led_2.value(not led_2.value())
        sleep(0.5)
        pass

    esp32_ip = station.ifconfig()[0]
    print(f"Successfully connected to {ssid} with {esp32_ip}")
    led_2.value(1)

def web_page(mode=""):
    global esp32_ip
    if mode == "connected":
        content = f"""
        <h1>Wi-Fi credentials received</h1>
        <p>Your IP is: {esp32_ip}</p>
        <p>Hit the button to close AP mode</p>
        <form action="/close_ap" method="post">
          <input type="submit" value="Close">
        </form>
        """
    elif mode == "close":
        content = """
        <h1>Access Point closed</h1>
        <p>You may safely close this tab and connect with the device through your Wi-Fi network.</p>
        """
    else:
        content = """
        <h1>Welcome to ESP32 Access Point</h1>
        <p>Enter your Wi-Fi credentials</p>
        <form action="/connect" method="post">
          <div>
            <label>SSID</label>
            <input type="text" name="ssid" value="catnip">
          </div>
          <div>
            <label>Password</label>
            <input type="password" name="password" value="MiawMiaw666!!">
          </div>
          <input type="submit" value="Connect">
        </form>
        """

    html = html_template.format(content=content)
    return html

def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", port))
    except OSError as e:
        if e.errno == 112:
            print("Port is already in use, waiting for it to be released...")
            time.sleep(5)
            s.bind(("", port))
    s.listen(5)
    print(f"Socket created on port: {port}")
    return s

s = create_socket(80)

def reinitialize_socket(port):
    global s
    s = create_socket(port)

def main_loop():
    while True:
        print("running")
        try:
            conn, addr = s.accept()
            print("Got a connection from %s" % str(addr))
            request = conn.recv(1024)
            request = str(request)
            print("Content = %s" % request)
            response = None
            mode = ""

            if "/connect" in request:
                ssid_start = request.find("ssid=") + 5
                ssid_end = request.find("&", ssid_start)
                ssid = request[ssid_start:ssid_end]

                password_start = request.find("password=") + 9
                password_end = request.find(" HTTP", password_start)
                password = request[password_start:password_end]

                try:
                    ssid = urldecode(ssid)
                    password = urldecode(password)
                    connect_to_wifi(ssid, password)
                    mode = "connected"

                except Exception as e:
                    print(f"Error: {e}")

            if "/close_ap" in request:
                mode = "close"

            if "/toggle" in request:
                led_1.value(not led_1.value())
                led_2.value(not led_2.value())
                led_status = {"led_1": led_1.value(), "led_2": led_2.value()}
                response = json.dumps({"mode": mode, "led_status": led_status})
                conn.send("HTTP/1.1 200 OK\n")
                conn.send("Content-Type: application/json\n")
                conn.send("Access-Control-Allow-Origin: *\n")
                conn.send("Access-Control-Allow-Headers: Content-Type\n")  # Add this line
                conn.send("Connection: close\n\n")
                conn.sendall(response)
                conn.close()
                continue  # Skip the rest of the loop for /toggle request

            response = web_page(mode)
            conn.send("HTTP/1.1 200 OK\n")
            conn.send("Content-Type: text/html\n")
            conn.send("Connection: close\n\n")
            conn.sendall(response)
            conn.close()

            if "/close_ap" in request:
                close_ap()
                reinitialize_socket(80)
                continue  # Restart the loop after reinitializing the socket

        except OSError as e:
            print(f"OSError: {e}")

main_loop()