# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)


def run_cmd(container, cmd):
    logger.debug("Running %s" % (' '.join(cmd)))
    exit_code, stdout, stderr = container.execute(cmd)
    logger.debug(stdout)
    logger.debug(stderr)
    return exit_code
