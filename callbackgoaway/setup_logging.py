# -*- coding: utf-8 -*-

__all__ = ('get_logger', )


def get_logger(name):
    from logging import (getLogger, StreamHandler, DEBUG, )
    logger = getLogger(name)
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
    logger.addHandler(stream_handler)
    return logger
