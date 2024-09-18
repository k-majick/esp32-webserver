from machine import Pin
import network
import esp32
import esp
import gc

esp.osdebug(None)
gc.collect()

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-AP", password="123")

led_1 = Pin(2, Pin.OUT)
led_2 = Pin(13, Pin.OUT)

led_1.value(1)
print("Access Point established")
print(ap.ifconfig())

def check_uid():
    nvs = esp32.NVS('storage')
    uid = 1
    stored_uid = None

    try:
        stored_uid = nvs.get_i32('uid')
    except OSError:
        nvs.set_i32('uid', uid)
        nvs.commit()
        stored_uid = nvs.get_i32('uid')

    return stored_uid

print('Device UID:', check_uid())
