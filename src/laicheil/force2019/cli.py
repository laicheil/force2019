#!/usr/bin/env python3
# vim: set filetype=python sts=4 ts=4 sw=4 expandtab:
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
import tensorflow as tf
import sklearn as skl


from .argparse_tree import ArgParseNode
from . import __version__

from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras import backend as K
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,Lambda, Dense, Flatten
from tensorflow.image import grayscale_to_rgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

logger = logging.getLogger(__name__)

class MyModel:
    def __init__(self):
        pass

    def load_files(self, data_path):
        list_of_files = os.listdir(data_path)
        num_of_files = len(list_of_files)
        first_file_path = os.path.join(data_path, list_of_files[0])
        #print (first_file_path)
        with open(first_file_path,'r') as read_file:
          shape_of_files = (num_of_files,) + np.asarray(json.load(read_file)).shape + (1, )
        #print (shape_of_files)
        self.data = np.zeros((shape_of_files))
        self.labels = np.zeros(num_of_files)
        self.labels_ce = np.zeros((num_of_files,2))
        for i, filename in enumerate(os.listdir(data_path)):
            full_path = os.path.join(data_path,filename)
            self.labels[i] = int(filename.startswith('good'))
            self.labels_ce[i, int(filename.startswith('good'))] = 1
            with open(full_path,'r') as read_file:
                self.data[i, :, :, 0] = np.asarray(json.load(read_file))

        logger.info('labels shape %s', self.labels.shape)
        logger.info('labels for CE shape %s', self.labels_ce.shape)
        logger.info('data shape %s', self.data.shape)

        logger.debug(self.labels)
        logger.debug(os.listdir(data_path))
        logger.info("done ...");

    def add_data_augmentation(self):

        self.datagen = image.ImageDataGenerator (
            featurewise_center = True,
            featurewise_std_normalization=True,
            vertical_flip=True,
            horizontal_flip=True,
            rotation_range=90)
        self.datagen.fit (self.data)

        self.train_samples, validation_samples, train_labels, validation_labels = train_test_split(self.data, self.labels, test_size=.334)

        train_generator         = self.datagen.flow(self.train_samples, train_labels, batch_size=32)
        validation_generator    = self.datagen.flow(validation_samples , validation_labels , batch_size=32)


        train_samples_ce, validation_samples_ce, train_labels_ce, validation_labels_ce = train_test_split(self.data, self.labels_ce, test_size=.334)
        self.train_ce_generator         = self.datagen.flow(train_samples_ce, train_labels_ce, batch_size=32)
        self.validation_ce_generator    = self.datagen.flow(validation_samples_ce , validation_labels_ce , batch_size=32)

        logger.info("done ...");

    def compile_model(self, weights):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #config.gpu_options.per_process_gpu_memory_fraction = 0.33

        #with tf.device('/device:GPU:0'):
        K.set_session (tf.Session (config = config))

        logger.info('DONE LOADING MODEL')

        ## inputs
        self.inputs = Input (shape=self.data.shape[1:])#samples.shape[1:]
        #
        ## from grayscale to RGB, Xception needs 3 Channel input
        x = Lambda (lambda x: grayscale_to_rgb (x), name='grayscale_to_rgb') (self.inputs)
        base_model = ResNet50(weights=weights, input_tensor=x,include_top=False)
        output = Flatten()(base_model.output)
        output = Dense(1000, activation='relu')(output)
        output = Dense(100, activation='relu')(output)
        output = Dense(2, activation='softmax')(output)
        ## The model
        num_layers = len(base_model.layers)
        for i, layer in enumerate (base_model.layers):
          layer.trainable = i < 8 or i > num_layers-8
        self.model = Model(inputs=self.inputs, outputs=output)
        self.model.compile(optimizer='nadam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        logger.info("done ...");

    def evaluate(self):
        self.model.fit_generator(self.train_ce_generator,
            steps_per_epoch=int(self.train_samples.shape[0]),
            epochs=100,validation_data=self.validation_ce_generator)
        self.evaluation = self.model.evaluate_generator(self.validation_ce_generator)

        logger.info("done ...");

class Application:
    def __init__(self):
        self.apn_root = ArgParseNode(options={"add_help": True})

    def handle_stage_one(self, parse_result):
        model = MyModel()
        model.load_files(parse_result.fromdir)
        model.add_data_augmentation()
        weights = parse_result.weights
        if parse_result.skip_weights:
            weights = None
        model.compile_model(weights)
        model.evaluate()

    '''
    def handle_load_files(self, parse_result):

        data_path = parse_result.fromdir
        list_of_files = os.listdir(data_path)
        num_of_files = len(list_of_files)
        first_file_path = os.path.join(data_path, list_of_files[0])
        #print (first_file_path)
        with open(first_file_path,'r') as read_file:
          shape_of_files = (num_of_files,) + np.asarray(json.load(read_file)).shape + (1, )
        #print (shape_of_files)
        data = np.zeros((shape_of_files))
        labels = np.zeros(num_of_files)
        labels_ce = np.zeros((num_of_files,2))
        for i, filename in enumerate(os.listdir(data_path)):
            full_path = os.path.join(data_path,filename)
            labels[i] = int(filename.startswith('good'))
            labels_ce[i, int(filename.startswith('good'))] = 1
            with open(full_path,'r') as read_file:
                data[i, :, :, 0] = np.asarray(json.load(read_file))

        logger.info('labels shape %s', labels.shape)
        logger.info('labels for CE shape %s', labels_ce.shape)
        logger.info('data shape %s', data.shape)

        datagen = image.ImageDataGenerator (
            featurewise_center = True,
            featurewise_std_normalization=True,
            vertical_flip=True,
            horizontal_flip=True,
            rotation_range=90)
        datagen.fit (data)

        train_samples, validation_samples, train_labels, validation_labels = train_test_split(data, labels, test_size=.334)

        train_generator         = datagen.flow(train_samples, train_labels, batch_size=32)
        validation_generator    = datagen.flow(validation_samples , validation_labels , batch_size=32)


        train_samples_ce, validation_samples_ce, train_labels_ce, validation_labels_ce = train_test_split(data, labels_ce, test_size=.334)
        train_ce_generator         = datagen.flow(train_samples_ce, train_labels_ce, batch_size=32)
        validation_ce_generator    = datagen.flow(validation_samples_ce , validation_labels_ce , batch_size=32)

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #config.gpu_options.per_process_gpu_memory_fraction = 0.33

        #with tf.device('/device:GPU:0'):
        K.set_session (tf.Session (config = config))

        logger.info('DONE LOADING MODEL')


        ## inputs
        inputs = Input (shape=data.shape[1:])#samples.shape[1:]
        #
        ## from grayscale to RGB, Xception needs 3 Channel input
        x = Lambda (lambda x: grayscale_to_rgb (x), name='grayscale_to_rgb') (inputs)
        if parse_result.skip_weights:
            base_model = ResNet50(weights=None, input_tensor=x,include_top=False)
        else:
            base_model = ResNet50(weights=parse_result.weights, input_tensor=x,include_top=False)
        output = Flatten()(base_model.output)
        output = Dense(1000, activation='relu')(output)
        output = Dense(100, activation='relu')(output)
        output = Dense(2, activation='softmax')(output)
        ## The model
        num_layers = len(base_model.layers)
        for i, layer in enumerate (base_model.layers):
          layer.trainable = i < 8 or i > num_layers-8
        model = Model(inputs=inputs, outputs=output)
        model.compile(optimizer='nadam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        logger.info("done compiling model");

        model.fit_generator(train_ce_generator, steps_per_epoch=int(train_samples.shape[0]), epochs=100,validation_data=validation_ce_generator)
        evaluation = model.evaluate_generator(validation_ce_generator)

        logger.info("fit done ...");
    '''

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
        apn_current.parser.add_argument("--weights", dest="weights", action="store",
            type=str, default="imagenet", required=False)
        apn_current.parser.add_argument("--skip-weights", dest="skip_weights", action="store_true",
            default=False, required=False)
        apn_current.parser.set_defaults(handler=self.handle_stage_one)

        apn_current = apn_eventgrid = apn_root.get("stage-one")
        apn_current.parser.add_argument("--from", dest="fromdir", action="store", type=str, required=True)
        apn_current.parser.add_argument("--weights", dest="weights", action="store",
            type=str, default="imagenet", required=False)
        apn_current.parser.add_argument("--skip-weights", dest="skip_weights", action="store_true",
            default=False, required=False)
        apn_current.parser.set_defaults(handler=self.handle_stage_one)

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
