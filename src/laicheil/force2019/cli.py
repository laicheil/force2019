#!/usr/bin/env python3
# vim: set filetype=python sts=4 ts=4 sw=4 expandtab tw=100 cc=+1:
"""
Command line interface module
"""
# pylint: disable=unused-variable
# pylint: disable=fixme
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=pointless-string-statement
import logging
import sys
import asyncio
import signal
import uuid
import datetime
import json
import os
import numpy as np

from .argparse_tree import ArgParseNode
from . import __version__

logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.apn_root = ArgParseNode(options={"add_help": True})

    def load_files(self, parse_result):
        data_path = parse_result.fromdir
        list_of_files = os.listdir(data_path)
        num_of_files = len(list_of_files)
        first_file_path = os.path.join(data_path, list_of_files[0])
        with open(first_file_path,'r') as read_file:
          shape_of_files = (num_of_files,) + np.asarray(json.load(read_file)).shape + (1, )
        data = np.zeros((shape_of_files))
        labels = np.zeros(num_of_files)
        for i, filename in enumerate(os.listdir(data_path)):
            full_path = os.path.join(data_path,filename)
            labels[i] = int(filename.startswith('good'))
            with open(full_path,'r') as read_file:
                data[i, :, :, 0] = np.asarray(json.load(read_file))

        logger.info('labels shape %s', labels.shape)
        logger.info('data shape %s', data.shape)


    def main(self):
        # pylint: disable=too-many-statements
        apn_current = apn_root = self.apn_root

        apn_root.parser.add_argument("--version",
            action="version", version="{:s}".format(__version__))
        apn_root.parser.add_argument("-v", "--verbose",
            action="count", dest="verbosity",
            help="increase verbosity level")

        apn_current = apn_eventgrid = apn_root.get("load_files")
        apn_current.parser.add_argument("--from", dest="fromdir", action="store", type=str, required=True)
        apn_current.parser.set_defaults(handler=self.load_files)

        parse_result = self.parse_result = apn_root.parser.parse_args(args=sys.argv[1:])


        verbosity = parse_result.verbosity
        if verbosity is not None:
            root_logger = logging.getLogger("")
            root_logger.propagate = True
            new_level = (root_logger.getEffectiveLevel() -
                (min(1, verbosity)) * 10 - min(max(0, verbosity - 1), 9) * 1)
            root_logger.setLevel(new_level)
        else:
            # XXX TODO FIXME this is here because this logger has it is logging things on
            # info level that should be logged as debugging
            # to re-enable you can use PYLOG_LEVELS="{ azure.storage.common.storageclient: INFO }"
            logging.getLogger("azure.storage.common.storageclient").setLevel(logging.WARNING)

        logger.debug("sys.argv = %s, parse_result = %s, logging.level = %s, logger.level = %s",
            sys.argv, parse_result, logging.getLogger("").getEffectiveLevel(),
            logger.getEffectiveLevel())

        logger.info("start ...");

        if "handler" in parse_result and parse_result.handler:
            parse_result.handler(parse_result)


def main():

    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%dT%H:%M:%S", stream=sys.stderr,
        format=("%(asctime)s %(process)d %(thread)x %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"))

    '''
    root_logger = logging.getLogger("")
    root_logger.propagate = True
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(coloredlogs.ColoredFormatter(datefmt="%Y-%m-%dT%H:%M:%S",
        fmt=("%(asctime)s %(process)d %(thread)x %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s")
        ))
    root_logger.addHandler(handler)
    '''
    application = Application()
    application.main()

if __name__ == "__main__":
    main()
