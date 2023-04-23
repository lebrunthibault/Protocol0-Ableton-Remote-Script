from typing import Dict, Any

from protocol0.shared.Config import Config
from protocol0.shared.logging.Logger import Logger


class SentryService(object):
    def __init__(self):
        # type: () -> None
        self.activated = False

    def activate(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        import sentry_sdk

        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            before_send=self._before_send,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
        )
        self.activated = True
        Logger.info("Sentry: activated")

    def _before_send(self, event, _):
        # type: (Dict[str, Any], Dict[str, Any]) -> Dict[str, Any]
        """Rewrite filenames so that GitHub integration works"""
        for frame in event["exception"]["values"][0]["stacktrace"]["frames"]:
            frame["abs_path"] = frame["abs_path"].replace("\\", "/")
            frame["filename"] = frame["filename"].replace("\\", "/")

        return event
