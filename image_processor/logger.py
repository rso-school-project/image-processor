import logging
import json_log_formatter

from image_processor import VERSION, MODULE, API_VERSION


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['message'] = message
        extra['level'] = 'WARN' if '/health/' in message else record.levelname
        extra['process'] = record.process
        extra['thread'] = record.thread
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


