import logging
import json_log_formatter

from image_processor import VERSION, MODULE, API_VERSION


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['message'] = message
        extra['level'] = record.levelname
        extra['processName'] = record.processName
        extra['threadName'] = record.threadName
        extra['funcName'] = record.funcName
        extra['api_version'] = API_VERSION
        extra['app_version'] = VERSION
        extra['app_name'] = MODULE

        return extra


logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
json_formater = CustomisedJSONFormatter()

handler = logging.StreamHandler()
handler.setFormatter(json_formater)
handler.setLevel(logging.INFO)

logger.addHandler(handler)


