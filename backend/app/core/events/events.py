from collections import defaultdict
from typing import Callable, Dict, List
from app.logger import logger

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        # When False (default), handler errors are logged and publishing continues.
        # When True, the first handler error will be raised to the caller.
        self.event_handler_fail_fatal: bool = False

    def subscribe(self, event_name: str, handler: Callable):
        self.subscribers[event_name].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to event {event_name}")

    def publish(self, event_name: str, payload: dict):
        logger.info(f"Publishing event {event_name} with payload: {payload}")
        handlers = self.subscribers.get(event_name, [])
        logger.info(f"Found {len(handlers)} handlers for event {event_name}")

        for handler in handlers:
            try:
                logger.info(f"Executing handler {handler.__name__} for event {event_name}")
                handler(payload)
                logger.info(f"Successfully executed handler {handler.__name__} for event {event_name}")
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__} for event {event_name}: {str(e)}", exc_info=True)
                if getattr(self, "event_handler_fail_fatal", False):
                    raise
                # Continue with other handlers even if one fails
                continue

event_bus = EventBus()
