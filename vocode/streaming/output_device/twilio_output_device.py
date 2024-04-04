from __future__ import annotations

import asyncio
import json
import base64
from typing import Callable, Optional
import logging

from fastapi import WebSocket

from vocode.streaming.output_device.base_output_device import BaseOutputDevice
from vocode.streaming.telephony.constants import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_SAMPLING_RATE,
)
from ...streaming.telephony.templater import update_twiml_connection_with_digits_to_string


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TwilioOutputDevice(BaseOutputDevice):
    def __init__(
        self, ws: Optional[WebSocket] = None, stream_sid: Optional[str] = None, handle_digits: Optional[Callable] = None
    ):
        super().__init__(
            sampling_rate=DEFAULT_SAMPLING_RATE, audio_encoding=DEFAULT_AUDIO_ENCODING
        )
        self.ws = ws
        self.stream_sid = stream_sid
        self.active = True
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.process_task = asyncio.create_task(self.process())
        self.handle_digits = handle_digits
        self.conversation_id = None
        self.base_url = None

    async def process(self):
        while self.active:
            message = await self.queue.get()
            logger.info(f"From within twilio_output_device process, message: {message}")
            try:
                if "event" in message and message["event"] == "dtmf":
                    xml = update_twiml_connection_with_digits_to_string(
                        call_id=self.conversation_id,
                        base_url=self.base_url,
                        digits="1"
                    )
                    logger.info(f"XML: {xml}")
            except Exception as e:
                logger.error(f"Unable to get XML: {xml}")
            await self.ws.send_text(message)

    def consume_dtmf_message(self, digit: str, sequence_number: str):
        twilio_message = { 
            "event": "dtmf", 
            "streamSid": self.stream_sid, 
            "sequenceNumber": sequence_number, 
            "dtmf": { 
                "track":"inbound_track", 
                "digit": digit
            }
        }
        self.queue.put_nowait(json.dumps(twilio_message))

    def consume_nonblocking(self, chunk: bytes):
        twilio_message = {
            "event": "media",
            "streamSid": self.stream_sid,
            "media": {"payload": base64.b64encode(chunk).decode("utf-8")},
        }
        self.queue.put_nowait(json.dumps(twilio_message))

    def maybe_send_mark_nonblocking(self, message_sent):
        mark_message = {
            "event": "mark",
            "streamSid": self.stream_sid,
            "mark": {
                "name": "Sent {}".format(message_sent),
            },
        }
        self.queue.put_nowait(json.dumps(mark_message))

    def terminate(self):
        self.process_task.cancel()
