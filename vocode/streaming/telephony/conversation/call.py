from fastapi import WebSocket
from enum import Enum
import logging
from typing import Optional, TypeVar, Union
from vocode.streaming.agent.factory import AgentFactory
from vocode.streaming.models.agent import AgentConfig
from vocode.streaming.models.events import PhoneCallEndedEvent
from vocode.streaming.output_device.vonage_output_device import VonageOutputDevice

from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.output_device.twilio_output_device import TwilioOutputDevice
from vocode.streaming.models.synthesizer import (
    SynthesizerConfig,
)
from vocode.streaming.models.transcriber import (
    TranscriberConfig,
)
from vocode.streaming.models.telephony import (
    BaseCallConfig,
)
from vocode.streaming.synthesizer.factory import SynthesizerFactory
from vocode.streaming.telephony.config_manager.base_config_manager import (
    BaseConfigManager,
)
from vocode.streaming.telephony.constants import DEFAULT_SAMPLING_RATE
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.transcriber.factory import TranscriberFactory
from vocode.streaming.utils.events_manager import EventsManager
from vocode.streaming.utils.conversation_logger_adapter import wrap_logger
from vocode.streaming.utils import create_conversation_id

TelephonyOutputDeviceType = TypeVar(
    "TelephonyOutputDeviceType", bound=Union[TwilioOutputDevice, VonageOutputDevice]
)


class Call(StreamingConversation[TelephonyOutputDeviceType]):
    def __init__(
        self,
        from_phone: str,
        to_phone: str,
        base_url: str,
        config_manager: BaseConfigManager,
        call_config: BaseCallConfig,
        output_device: TelephonyOutputDeviceType,
        agent_config: AgentConfig,
        transcriber_config: TranscriberConfig,
        synthesizer_config: SynthesizerConfig,
        conversation_id: Optional[str] = None,
        transcriber_factory: TranscriberFactory = TranscriberFactory(),
        agent_factory: AgentFactory = AgentFactory(),
        synthesizer_factory: SynthesizerFactory = SynthesizerFactory(),
        events_manager: Optional[EventsManager] = None,
        logger: Optional[logging.Logger] = None,
    ):
        conversation_id = conversation_id or create_conversation_id()
        logger = wrap_logger(
            logger or logging.getLogger(__name__),
            conversation_id=conversation_id,
        )

        self.from_phone = from_phone
        self.to_phone = to_phone
        self.base_url = base_url
        self.config_manager = config_manager
        self.call_config = call_config
        super().__init__(
            output_device,
            transcriber_factory.create_transcriber(transcriber_config, logger=logger),
            agent_factory.create_agent(agent_config, logger=logger),
            synthesizer_factory.create_synthesizer(synthesizer_config, logger=logger),
            conversation_id=conversation_id,
            per_chunk_allowance_seconds=0.01,
            events_manager=events_manager,
            logger=logger,
            transcript=call_config.transcript
        )

    def attach_ws(self, ws: WebSocket):
        self.logger.debug("Trying to attach WS to outbound call")
        self.output_device.ws = ws
        self.output_device.current_conversation_id = self.id
        self.output_device.base_url = self.base_url
        self.logger.debug("Attached WS to outbound call")

    async def attach_ws_and_start(self, ws: WebSocket):
        raise NotImplementedError

    async def tear_down(self):
        conversation_ended = not self.output_device.playing_dtmf

        if conversation_ended:
            self.events_manager.publish_event(PhoneCallEndedEvent(conversation_id=self.id))
        else:
            self.logger.info("Saving call_config")
            # Save the transcript on the call config before we store it
            self.call_config.transcript = self.transcript
            # But clear out the events_manager because it may not be JSON serializable
            self.call_config.transcript.events_manager = None
            # Now store it, so we can continue with the same transcript when we get the next websocket connection
            self.config_manager.save_config(conversation_id=self.id, config=self.call_config)

        await self.terminate(conversation_ended=conversation_ended)
