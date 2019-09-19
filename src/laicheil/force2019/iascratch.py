#!/usr/bin/env python3
# vim: set filetype=python sts=2 ts=2 sw=2 expandtab:
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
import glob

import numpy as np
import tensorflow as tf
import sklearn as skl

logger = logging.getLogger(__name__)

script_dirname = os.path.dirname(__file__)
script_dirnamea = os.path.abspath(script_dirname)
script_basename = os.path.basename(__file__)
script_vardir = os.path.join(script_dirnamea,"..","..","..","var")

from .argparse_tree import ArgParseNode
from . import __version__

from tensorflow.python.keras.callbacks import CSVLogger, EarlyStopping, ModelCheckpoint
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Lambda, Dense, Flatten
from tensorflow.image import grayscale_to_rgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

import tensorflow.keras.callbacks as tfkc

import matplotlib.pyplot

logger = logging.getLogger(__name__)

def analise_samples(data_path, select_clazz=None):
  filenames = os.listdir(data_path)
  index_max = 0
  clazzes = set([])
  types = set([])
  clazz_type_counts = {}
  clazz_index_max = {}
  for filename in filenames:
    filename_parts = filename.split('.')[0].split('_')
    filename_index = int(filename_parts[-1])
    filename_clazz = filename_parts[-2]
    filename_type = '_'.join(filename_parts[0:-2])
    clazzes.add(filename_clazz)
    types.add(filename_type)

    clazz_type_counts.setdefault(filename_type, {})
    clazz_type_counts[filename_type].setdefault(filename_clazz, 0)
    clazz_index_max.setdefault(filename_clazz, 0);

    clazz_type_counts[filename_type][filename_clazz] += 1
    clazz_index_max[filename_clazz] = max(clazz_index_max[filename_clazz], filename_index)
    index_max = max(index_max, filename_index)

  print("types = ", types)
  print("clazzes = ", clazzes)
  print("index_max", index_max)
  print("clazz_type_counts = ", clazz_type_counts)
  print("clazz_index_max = ", clazz_index_max)
  return ( types, clazzes, index_max )

def load_sample(data_path, clazz, index, xglob="*"):
  sample_files = glob.glob(os.path.join(data_path,"{:s}_{:s}_{:d}.json".format(xglob, clazz, index)))
  print("sample_files = ", sample_files)

def load_samples(data_path, limit=None):
  ( types, clazzes, index_max ) = analise_samples(data_path)

def load_files(data_path, limit=None):
  #data_path = os.path.join('force2019-data-000', 'data-001')#'hackathon_training_data'
  #data_path = os.path.join('/content/drive/My Drive/force-hackathon-2019', 'data-002')
  num_of_sample = 0
  list_of_files = os.listdir(data_path)
  for filename in [f for f in list_of_files if f.startswith('zone')]:
    num_of_sample = max (num_of_sample,int(filename.split('.')[0].split('_')[-1]))

  num_of_files = len(list_of_files)
  first_file_path = os.path.join(data_path, list_of_files[0])


  num_smp = num_of_sample * 2 # Good & Bad
  with open(first_file_path,'r') as read_file:
    shape_of_files = (num_smp,) + np.asarray(json.load(read_file)).shape + (2, )

  # the shape of the data is (num_smp, width, length, chanels)
  data = np.zeros((shape_of_files))

  # labels are a vector the size of the number of sumples
  labels = np.zeros(num_smp)

  # labels for categorical crossentropy are a matrix of num_smp X num_classes
  labels_ce = np.zeros((num_smp,2))

  for filename in os.listdir(data_path):

    if not filename.startswith('seismic'):
      splitted_name = filename.split('.')[0].split('_')
      if splitted_name[1] == 'seismic':
        continue

      # Horizon A and B are on two different channels
      chan = int(splitted_name[0]=='topa')

      # calculate the index of the data (if data belongs to the "Good" class I shift it)
      i = int(splitted_name[-1])
      is_good = int (splitted_name[1] == 'good')
      i += (num_of_sample) * is_good

      full_path = os.path.join(data_path,filename)
      labels[i] = is_good #int(filename.startswith('good'))
      labels_ce[i, is_good] = 1
      with open(full_path,'r') as read_file:
          loaded = np.asarray(json.load(read_file))
          #mask = np.zeros_like(loaded)
          #mask[np.argwhere(loaded > 999990)] = 1
          data[i, :, :, chan] = loaded

  print('labels shape', labels.shape)
  print('labels for CE shape', labels_ce.shape)
  print('data shape', data.shape)

class Application:
    def __init__(self):
        self.apn_root = ArgParseNode(options={"add_help": True})

    def handle_load_data(self, parse_result):
        analise_samples(parse_result.fromdir)
        load_sample(parse_result.fromdir, "good", 0)
        #load_files(parse_result.fromdir, parse_result.limit_input)

    def main(self):
        # pylint: disable=too-many-statements
        apn_current = apn_root = self.apn_root

        apn_root.parser.add_argument("--version",
            action="version", version="{:s}".format(__version__))
        apn_root.parser.add_argument("-v", "--verbose",
            action="count", dest="verbosity",
            help="increase verbosity level")
        apn_root.parser.add_argument("--vardir",
            action="store", dest="vardir",
            default=None, required=False)

        apn_current = apn_eventgrid = apn_root.get("load_files")
        apn_current.parser.add_argument("--from", dest="fromdir", action="store", type=str, required=True)
        apn_current.parser.add_argument("--limit-input", dest="limit_input", action="store", default=None, type=int, required=False)
        apn_current.parser.set_defaults(handler=self.handle_load_data)

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

        global script_vardir
        if parse_result.vardir is not None:
            script_vardir = parse_result.vardir

        logger.info("start ... script_vardir = %s", script_vardir);
        os.makedirs(script_vardir, exist_ok=True);

        if "handler" in parse_result and parse_result.handler:
            parse_result.handler(parse_result)


def main():

    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%dT%H:%M:%S", stream=sys.stderr,
        format=("%(asctime)s %(process)d %(thread)x %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"))
    application = Application()
    application.main()

if __name__ == "__main__":
    main()
