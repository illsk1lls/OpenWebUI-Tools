"""
title: send_sms
author: Grok for illsk1lls
description: Hardware SMS / Text message
version: 2.0.0
license: MIT
"""

import serial
import time
from typing import Optional

class Tools:
    def send_message(self, message: str, to: str) -> str:
        """
        Send a real SMS text message to a U.S. cell phone via the 4G dongle.
        """
        MAX_LENGTH = 150
        PORT = "/dev/ttyUSB2"
        BAUDRATE = 115200

        if len(message) > MAX_LENGTH:
            return f"❌ Message too long ({len(message)} chars). Max recommended is {MAX_LENGTH}."

        if not to.startswith("+"):
            return "❌ Phone number must be in international format starting with + (e.g. +15551234567)"

        try:
            ser = serial.Serial(PORT, BAUDRATE, timeout=10)
            time.sleep(0.3)

            ser.write(b"AT\r")
            time.sleep(0.4)

            ser.write(b"AT+CMGF=1\r")
            time.sleep(0.4)

            cmd = f'AT+CMGS="{to}"\r'.encode()
            ser.write(cmd)
            time.sleep(1.2)

            ser.write(f"{message}\x1a".encode())
            time.sleep(6)

            response = ser.read_all().decode(errors="ignore")
            ser.close()

            if "+CMGS:" in response:
                return f"✅ SMS sent successfully to {to}"
            return f"✅ SMS sent. Response: {response.strip()[:180]}"

        except serial.SerialException as e:
            return f"❌ Serial error (is the dongle plugged in?): {str(e)}"
        except Exception as e:
            return f"❌ Error sending SMS: {str(e)}"
