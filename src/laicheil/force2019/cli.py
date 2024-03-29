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

class MyModel:
    def __init__(self):
        pass

    def load_files(self, data_path, limit=None):
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
            if not filename.endswith(".json"):
                logger.debug("Not loading data from %s", filename);
                continue
            if limit is not None and i >= limit:
                logger.info("Not loading more files as %s files have been loaded", limit);
                break
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

    def add_data_augmentation(self, batch_size=None):

        if batch_size is None:
            batch_size=32
        self.datagen = image.ImageDataGenerator (
            featurewise_center = True,
            featurewise_std_normalization=True,
            vertical_flip=True,
            horizontal_flip=True,
            rotation_range=90)
        self.datagen.fit (self.data)

        self.train_samples, validation_samples, train_labels, validation_labels = train_test_split(self.data, self.labels, test_size=.334)

        train_generator         = self.datagen.flow(self.train_samples, train_labels, batch_size=batch_size)
        validation_generator    = self.datagen.flow(validation_samples , validation_labels , batch_size=batch_size)


        train_samples_ce, validation_samples_ce, train_labels_ce, validation_labels_ce = train_test_split(self.data, self.labels_ce, test_size=.334)
        self.train_ce_generator         = self.datagen.flow(train_samples_ce, train_labels_ce, batch_size=batch_size)
        self.validation_ce_generator    = self.datagen.flow(validation_samples_ce , validation_labels_ce , batch_size=batch_size)
        self.test_ce_generator = self.validation_ce_generator

        logger.info("done ...");

    def compile_model(self, weights):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        #config.gpu_options.per_process_gpu_memory_fraction = 0.33

        #with tf.device('/device:GPU:0'):
        K.set_session (tf.Session (config = config))

        logger.info('DONE LOADING MODEL')

        self.now = datetime.datetime.now ()
        #self.date_str = self.now.strftime('%Y%m%d%H%M')
        self.date_str = "always"
        self.checkpoint_init_name = 'init_chkpnt_'+self.date_str+'.hdf5'

        self.callbacks = [
            tfkc.TensorBoard(log_dir=os.path.join(script_vardir, 'tbg'), histogram_freq=0, write_graph=True, write_images=True),
            EarlyStopping (monitor='val_acc', patience=9, verbose=1),
            ModelCheckpoint(self.checkpoint_init_name, monitor='val_acc', save_best_only=True, save_weights_only=True, verbose=1)
        ]

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
        #for i, layer in enumerate (base_model.layers):
        #  layer.trainable = i < 8 or i > num_layers-8
        self.model = Model(inputs=self.inputs, outputs=output)
        self.model.compile(optimizer='nadam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        logger.info("done ...");

    ## set steps per epoch
    def evaluate(self, epochs=None, steps_per_epoch=None):
        if epochs is None:
            epochs = 100
        logger.info("epochs=%s", epochs);
        if steps_per_epoch is None:
            steps_per_epoch=int(self.train_samples.shape[0])
        logger.info("steps_per_epoch=%s", steps_per_epoch);

        self.model.fit_generator(self.train_ce_generator, steps_per_epoch=steps_per_epoch, epochs=epochs,validation_data=self.validation_ce_generator)
        self.evaluation = self.model.evaluate_generator(self.validation_ce_generator)

        logger.info("done ...");

    def evaluate_k(self,epochs=None, steps_per_epoch=None):
        if epochs is None:
            epochs = 16
        logger.info("epochs=%s", epochs);
        if steps_per_epoch is None:
            steps_per_epoch=int(self.data.shape[0]/5)
        logger.info("steps_per_epoch=%s", steps_per_epoch);
        k_checkpoint_basename = os.path.join(script_vardir, 'CHK_' + self.date_str + '_K')
        kf = KFold (shuffle=True, n_splits=5)
        last_good_model_weights = ''
        k=0
        folds_map={}
        for train_index, test_index in kf.split(self.data, self.labels_ce):
            print('At fold K=',k,' with ', len(train_index), ' samples out of total ', self.data.shape[0])
            kf_filepath=k_checkpoint_basename + str(k) + '.hdf5'
            logger.info("kf_filepath=%s", kf_filepath);
            self.callbacks[-1].filepath = kf_filepath
            logger.info("before fit_generator ...")
            history = self.model.fit_generator (generator       = self.datagen.flow(self.data[train_index], self.labels_ce[train_index], batch_size=16),
                                           validation_data = self.datagen.flow(self.data[test_index] , self.labels_ce[test_index] , batch_size=16),
                                           steps_per_epoch = steps_per_epoch,
                                           epochs          = epochs,
                                           callbacks       = self.callbacks)
            logger.info("After fit_generator ...")
            if os.path.isfile(kf_filepath):
                logger.info("isfile(%s) = True ...", kf_filepath)
                #self.model.load_weights (kf_filepath) #Load best
                last_good_model_weights = kf_filepath
            if os.path.isfile(last_good_model_weights):
                logger.info("isfile(%s) = True ...", last_good_model_weights)
                self.model.load_weights (last_good_model_weights)
                self.evaluation = self.model.evaluate_generator(self.test_ce_generator)
                print ('Evaluation:', self.evaluation)
                folds_map [k] = {
                    'evaluation'   : self.evaluation,
                    'history'      : history,
                    'filepath'     : kf_filepath }
                k += 1
        print(folds_map)

class Application:
    def __init__(self):
        self.apn_root = ArgParseNode(options={"add_help": True})

    def handle_stage_one(self, parse_result):
        model = MyModel()
        model.load_files(parse_result.fromdir, parse_result.limit_input)
        model.add_data_augmentation(parse_result.batch_size)
        weights = parse_result.weights
        if parse_result.skip_weights:
            weights = None
        model.compile_model(weights)
        if parse_result.eval_k:
            model.evaluate_k(parse_result.epochs, parse_result.steps_per_epoch)
        else:
            model.evaluate(parse_result.epochs, parse_result.steps_per_epoch)

    def handle_visualize(self, parse_result):
        os.makedirs(parse_result.todir, exist_ok=True);
        data_path = parse_result.fromdir
        for i, filename in enumerate(os.listdir(data_path)):
            if not filename.endswith(".json"):
                logger.debug("Not loading data from %s", filename);
                continue
            full_path = os.path.join(data_path,filename)
            logger.debug("Loading %s", full_path)
            with open(full_path,'r') as read_file:
                #data = np.asarray(json.load(read_file))
                #matplotlib.pyplot.imsave(os.path.join(parse_result.todir, os.path.basename(full_path).replace(".json", ".png")), data, format="png")
                from_json = json.load(read_file)
                loaded = np.asarray(from_json, dtype=np.float)
                std  = np.nanstd(loaded)
                mean = np.nanmean(loaded)
                vmin = np.nanmin(loaded)
                vmax = np.nanmax(loaded)
                vrange = np.abs(vmax-vmin)
                loaded = (loaded - std) / mean
                loaded [np.isnan(loaded)] = 0
                #data = np.asarray(json.load(read_file))
                matplotlib.pyplot.imsave(os.path.join(parse_result.todir, os.path.basename(full_path).replace(".json", ".png")), loaded, format="png")

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

        apn_current = apn_eventgrid = apn_root.get("visualize")
        apn_current.parser.add_argument("--from", dest="fromdir", action="store", type=str, required=True)
        apn_current.parser.add_argument("--to", dest="todir", action="store", type=str, required=True)
        apn_current.parser.set_defaults(handler=self.handle_visualize)

        apn_current = apn_eventgrid = apn_root.get("stage-one")
        apn_current.parser.add_argument("--limit-input", dest="limit_input", action="store", default=None, type=int, required=False)
        apn_current.parser.add_argument("--from", dest="fromdir", action="store", type=str, required=True)
        apn_current.parser.add_argument("--weights", dest="weights", action="store",
            type=str, default="imagenet", required=False)
        apn_current.parser.add_argument("--skip-weights", dest="skip_weights", action="store_true",
            default=False, required=False)
        apn_current.parser.add_argument("--eval-k", dest="eval_k", action="store_true",
            default=False, required=False)
        apn_current.parser.add_argument("--epochs", dest="epochs", action="store",
            type=int, default=None, required=False)
        apn_current.parser.add_argument("--batch-size", dest="batch_size", action="store",
            type=int, default=None, required=False)
        apn_current.parser.add_argument("--steps-per-epoch", dest="steps_per_epoch", action="store",
            type=int, default=None, required=False)
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
