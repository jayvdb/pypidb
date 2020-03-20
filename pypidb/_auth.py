from netrc import netrc

from logging_helper import setup_logging

logger = setup_logging()


def _get_token(hostname):
    try:
        conf = netrc()
        token = conf.hosts.get(hostname, [None])[0]
        return token
    except Exception as e:  # pragma: no cover
        logger.error("get_token e: {}".format(e))
