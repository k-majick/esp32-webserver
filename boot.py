from machine import Pin
import network
import esp32
import esp
import gc
import random

ap = network.WLAN(network.AP_IF)
nvs = esp32.NVS("storage")
led_1 = Pin(2, Pin.OUT)
led_2 = Pin(13, Pin.OUT)


def config():
    esp.osdebug(None)
    gc.collect()


def ap_init():
    ap.active(True)
    ap.config(essid="ESP32-AP", password="123")
    led_1.value(1)
    print(f"Access Point established at {ap.ifconfig()}")


def uid_check():
    stored_uid = None

    try:
        stored_uid = nvs.get_i32("device_uid")
    except OSError:
        print(f"Device UID not found, generating")
        stored_uid = random.randint(0, 2**31 - 1)
        nvs.set_i32("device_uid", stored_uid)
        nvs.commit()

    print(f"Device UID {stored_uid}")
    return stored_uid


config()
ap_init()
uid = uid_check()
