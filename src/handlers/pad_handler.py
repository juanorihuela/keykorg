import logging

from dtos.pad_event import PadEvent
from services.command_service import CommandService
from services.notification_service import NotificationService
from services.sequence_service import SequenceService

logger = logging.getLogger(__name__)


class PadHandler:
    def __init__(
        self,
        pad_map: dict,
        command_service: CommandService,
        sequence_service: SequenceService,
        notification_service: NotificationService,
    ):
        self.pad_map = pad_map
        self.command_service = command_service
        self.sequence_service = sequence_service
        self.notification_service = notification_service

    def handle(self, event: PadEvent) -> None:
        pad_config = self.pad_map.get(event.pad_id)
        if not pad_config:
            logger.warning(f"PAD_UNMAPPED | pad_id={event.pad_id}")
            self.notification_service.notify_warning(
                "Pad sin mapear", f"pad_id={event.pad_id}"
            )
            return

        pad_name = pad_config.get("name", f"pad_{event.pad_id}")
        pad_type = pad_config.get("type")

        logger.info(
            f"PAD_PRESS | pad_id={event.pad_id} | name={pad_name!r} | type={pad_type}"
        )

        if pad_type == "sequence":
            self.notification_service.notify_sequence()

        success = self._dispatch(pad_type, pad_config, pad_name)

        if success:
            self.notification_service.notify_done(
                pad_name,
                skip_notify=pad_config.get("skip_notify", False),
                skip_sound=pad_config.get("skip_sound", False),
            )

    def _dispatch(self, pad_type: str, pad_config: dict, pad_name: str) -> bool:
        if pad_type == "simple":
            return self.command_service.execute(pad_config["command"], pad_name)
        if pad_type == "sequence":
            return self.sequence_service.execute(pad_config["steps"], pad_name)
        logger.error(f"PAD_UNKNOWN_TYPE | type={pad_type!r}")
        self.notification_service.notify_warning(pad_name, "Tipo de pad desconocido")
        return False
