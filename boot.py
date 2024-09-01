from machine import Pin
import network
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
