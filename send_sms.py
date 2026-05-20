"""
title: send_sms
author: Grok for illsk1lls
description: Hardware SMS / Text message
version: 2.0.0
license: MIT
"""

from pydantic import BaseModel, Field
import serial
import time


class Tools:
    """
    - You MUST provide BOTH 'message' and 'to' parameters.
    - 'to' must be in international format starting with +1 (example: "+15551234567").
    - Try to recall the appropriate number from memory when possible.
    - If you do not know the number to send to, ask first before calling this tool.
    - Messages are limited to 150 characters maximum.
    - Use this tool for important alerts (job completions, long tasks,
      server notifications, etc.) where a loud real SMS / Text is preferred.
    """

    class SendSMS(BaseModel):
        """Send a SMS / Text message to a U.S. based phone number"""

        message: str = Field(..., description="The text to send (max 150 characters)")
        to: str = Field(..., description="Phone number in +1 format, e.g. +15551234567")

        async def __call__(self) -> str:
            MAX_LENGTH = 150
            PORT = "/dev/ttyUSB2"
            BAUDRATE = 115200

            if len(self.message) > MAX_LENGTH:
                return f"❌ Message too long ({len(self.message)} chars). Max is {MAX_LENGTH}."

            if not self.to.startswith("+"):
                return "❌ Phone number must start with + (e.g. +15551234567)"

            try:
                ser = serial.Serial(PORT, BAUDRATE, timeout=10)
                time.sleep(0.3)
                ser.write(b"AT\r")
                time.sleep(0.4)
                ser.write(b"AT+CMGF=1\r")
                time.sleep(0.4)

                cmd = f'AT+CMGS="{self.to}"\r'.encode()
                ser.write(cmd)
                time.sleep(1.2)
                ser.write(f"{self.message}\x1a".encode())
                time.sleep(6)

                response = ser.read_all().decode(errors="ignore")
                ser.close()

                return (
                    "✅ SMS sent successfully"
                    if "+CMGS:" in response
                    else f"✅ SMS sent. Response: {response[:150]}"
                )

            except Exception as e:
                return f"❌ Error: {str(e)}"
