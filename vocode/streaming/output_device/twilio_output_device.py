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
from vocode.streaming.telephony.templater import Templater


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
        self.current_conversation_id = None
        self.current_call_id = None
        self.base_url = None
        self.templater = Templater()

        self.twilio_client = None
        self.heuristic_func = None
        self.playing_dtmf = False

    async def process(self):
        logger.info(f"Current state of DTMF: {self.playing_dtmf}")
        while self.active:
            message = await self.queue.get()
            message = json.loads(message)
            try:
                if self.twilio_client is not None and self.current_call_id is not None and self.current_conversation_id is not None and "event" in message and message["event"] == "dtmf":
                    self.playing_dtmf = True
                    xml = self.templater.update_twiml_connection_with_digits_to_string(
                        call_id=self.current_conversation_id,
                        base_url=self.base_url,
                        digits=message["dtmf"]["digit"],
                    )
                    logger.debug(f"XML: {xml}")
                    call = self.twilio_client.get_call(self.current_call_id).update(twiml=xml)
                else:
                    # logger.debug(f"V2: From within twilio_output_device process, message: {message}")
                    await self.ws.send_text(json.dumps(message))
            except Exception:
                logger.exception("Unable to get XML")
                await self.ws.send_text(json.dumps(message))

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
