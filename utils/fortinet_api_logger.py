import logging
from flask import g, request


class FortinetAPILogger(object):
    """Fortinet API Logger"""
    def __init__(self, logger=None):
        if logger:
            self._logger = logger
        else:
            # root logger
            self._logger = logging.getLogger()

    def critical(self, msg, *args, **kwargs):
        """critical"""
        self._logger.critical(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        """v"""
        self._logger.fatal(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """error"""
        self._logger.error(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """exception"""
        self._logger.exception(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """warn"""
        self._logger.warn(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """info"""
        self._logger.info(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """debug"""
        self._logger.debug(self.__append_correlation_id_and_ip(msg), *args, **kwargs)

    @staticmethod
    def __append_correlation_id_and_ip(msg):
        if hasattr(g,'Correlationid'):
            _msg = f"""[{ request.remote_addr }] [{ g.Correlationid }] { msg }"""
        else:
            _msg = f"""[{request.remote_addr}] missing correlation id for {msg}"""
        return _msg