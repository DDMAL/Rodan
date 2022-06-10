# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from gamera import knn, knnga
from rodan.jobs.base import RodanTask
from tempfile import NamedTemporaryFile as NTF
from time import sleep

import json
from rodan.jobs.biollante_rodan import knnga_util as util
import shutil


STATE_INIT = 0
STATE_NOT_OPTIMIZING = 1
STATE_OPTIMIZING = 2
STATE_FINISHING = 3


class BiollanteRodan(RodanTask):
    name = "Biollante"
    author = "Juliette Regimbal"
    description = "GA Optimizer for kNN Classifiers"
    settings = {
        "job_queue": "Python3"  # This is due to using gamera
    }
    enabled = True
    category = "Optimization"
    interactive = True

    base = None
    selection = None
    replacement = None
    mutation = None
    crossover = None
    stop_criteria = None
    optimizer = None

    logger = get_task_logger(__name__)

    input_port_types = [
        {
            "name": "Classifier Data",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["application/gamera+xml"]
        }
    ]
    output_port_types = [
        {
            "name": "Feature Weights/Selection",
            "minimum": 1,
            "maximum": 1,
            "resource_types": ["application/gamera+xml"]
        }
    ]

    def get_my_interface(self, inputs, settings):
        self.logger.info(settings)

        context = {
            "base": json.loads(settings["@base"]),
            "selection": json.loads(settings["@selection"]),
            "replacement": json.loads(settings["@replacement"]),
            "mutation": json.loads(settings["@mutation"]),
            "crossover": json.loads(settings["@crossover"]),
            "stop_criteria": json.loads(settings["@stop_criteria"]),
            "optimizer": settings["@results"],
            "weights": settings["@weights"],
        }
        return "index.html", context

    def validate_my_user_input(self, inputs, settings, user_input):
        assert settings["@state"] == STATE_NOT_OPTIMIZING, \
            "Must not be optimizing! State is %s" % str(settings["@state"])

        # Start the optimization process
        if user_input["method"] == "start":
            try:
                self.setup_optimizer(user_input, settings["@num_features"])
            except Exception as e:
                raise self.ManualPhaseException(str(e))

            d = self.knnga_dict()
            d["@state"] = STATE_OPTIMIZING
            d["@settings"] = settings["@settings"]
            return d

        # Save the latest classifier version and finsh job.
        elif user_input["method"] == "finish":
            return {
                "@state": STATE_FINISHING,
                "@settings": settings["@settings"]
            }
        else:
            self.logger.warn("Unknown method: %s" % user_input["method"])
            return {}

    def run_my_task(self, inputs, settings, outputs):
        
        # debugging tests printed in the log
        dict_check_list = ["@base", "@selection", "@replacement", "@mutation", "@crossover", "@stop_criteria",
        "@results", "@weights"]
        for key in dict_check_list:
            if key in settings:
                self.logger.info(("settings[{0}] has type: {1} and the value is {2}").format(str(key), type(settings[key]), settings[key]))
            else:
                self.logger.info(str(key) + " does not exist inside the settings dictionary")

        if "@state" not in settings:
            settings["@state"] = STATE_INIT

        if settings["@state"] == STATE_INIT:
            self.logger.info("State: Init")

            with NTF(suffix=".xml") as temp:
                self.logger.info(temp.name)
                # Gamera fails to load files without xml extension.
                shutil.copy2(
                    inputs["Classifier Data"][0]["resource_path"],
                    temp.name
                )
                self.logger.info("copied the file")
                # will be doing machine learning in the next line 
                classifier = knn.kNNNonInteractive(temp.name)
                self.logger.info("created the classifier variable")

            with NTF() as temp:
                classifier.save_settings(temp.name)
                self.logger.info("saved the settings")
                temp.flush()
                self.logger.info("done flushing")
                temp.seek(0)
                self.logger.info("done seeking")
                settings["@settings"] = temp.read()
                self.logger.info("done reading and writing settings[\"@settings\"]")
                self.logger.info("type of the above thing is: " + str(type(settings["@settings"])))

            # Preserve the number of features and weights for
            # certain kinds of operations the GA optimizer might perform.
            # (e.g., Gauss mutation)
            settings["@num_features"] = classifier.num_features
            settings["@weights"] = classifier.get_weights_by_features()

            self.base = knnga.GABaseSetting()
            self.selection = util.SerializableSelection()
            self.replacement = util.SerializableReplacement()
            self.mutation = util.SerializableMutation()
            self.crossover = util.SerializableCrossover()
            self.stop_criteria = util.SerializableStopCriteria()

            settings["@state"] = STATE_NOT_OPTIMIZING

        if settings["@state"] == STATE_NOT_OPTIMIZING:
            self.logger.info("State: Not Optimizing")

            # Create set of parameters for template
            d = self.knnga_dict()
            d["@state"] = STATE_NOT_OPTIMIZING

            # decoding for python3 must be done manually
            d["@settings"] = settings["@settings"].decode("UTF-8")

            d["@weights"] = settings["@weights"]
            self.logger.info("returning waiting for user input") 
            self.logger.info("here are the settings and the types: ")
            coutner = 1
            for key in settings:
                self.logger.info(
                ("{0}th key: {1} with type {2} and its value: {3} with type {4}").format(coutner, key, type(key), settings[key], type(settings[key]))
                )
                coutner += 1
            return self.WAITING_FOR_INPUT(d)

        elif settings["@state"] == STATE_OPTIMIZING:
            self.logger.info("State: Optimizing")
            self.load_from_settings(settings)
            self.logger.info("loaded the settings and optimizing...")

            # Load data
            with NTF(suffix=".xml") as temp:
                shutil.copy2(
                    inputs["Classifier Data"][0]["resource_path"],
                    temp.name
                )
                classifier = knn.kNNNonInteractive(temp.name)
                self.logger.info("created the classifier object")

            # Load selection and weights
            with NTF(suffix=".xml") as temp:
                temp.write(settings["@settings"].encode("UTF-8"))
                self.logger.info("encoded settings[\"@settings\"] again and it will have type bytes from now on (until modified later)")
                temp.flush()
                classifier.load_settings(temp.name)

            self.optimizer = knnga.GAOptimization(
                classifier,
                self.base,
                self.selection.selection,
                self.crossover.crossover,
                self.mutation.mutation,
                self.replacement.replacement,
                self.stop_criteria.sc,
                knnga.GAParallelization(True, 4)
            )
            self.logger.info("Created the self.optimizer field and continuing")
            assert isinstance(self.optimizer, knnga.GAOptimization), \
                "Optimizer is %s" % str(type(self.optimizer))

            try:
                self.optimizer.startCalculation()
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Failed to start optimizing!")
                return False

            # Wait for optimization to finish
            while self.optimizer.status:
                sleep(30000)    # 30 seconds
                self.logger.info(self.optimizer.monitorString)

            # This is necessary since the classifier object isn't persistent
            settings = self.knnga_dict()

            with NTF() as temp:
                classifier.save_settings(temp.name)
                temp.flush()
                temp.seek(0)
                settings["@settings"] = temp.read()
                self.logger.info("read the settings again, now going to classify and get the features.")

            self.logger.info(classifier.get_weights_by_features())
            settings["@state"] = STATE_NOT_OPTIMIZING
            settings["@weights"] = classifier.get_weights_by_features()
            self.logger.info("created settings[@state] and settings[@weights]")
            return self.WAITING_FOR_INPUT(settings)

        else:   # Finish
            self.logger.info("State: Finishing")
            with open(
                outputs["Feature Weights/Selection"][0]["resource_path"], 'w'
            ) as f:
                self.logger.info("writing the result as the final step")            
                f.write(settings["@settings"])
            return True

    def my_error_information(self, exc, traceback):
        raise NotImplementedError

    def test_my_task(self, testcase):
        with NTF() as outfile:
            inputs = {
                "kNN Training Data": [
                    {
                        "resource_path":
                            "rodan/jobs/biollante-rodan/test_resources/" +
                            "Dalhousie_TD_421_422_NC-based_classifier.xml"
                    }
                ]
            }
            outputs = {
                "GA Optimized Classifier": [
                    {"resource_path": outfile.name}
                ]
            }

            # Test initial run
            result = self.run_my_task(inputs, {}, outputs)
            testcase.assertTrue(
                isinstance(result, self.WAITING_FOR_INPUT),
                "Result was actually %s" % type(result)
            )
            testcase.assertEqual(
                result.settings_update["@state"],
                STATE_NOT_OPTIMIZING,
                "State was %s" % str(result.settings_update["@state"])
            )

            # Start without enough GA optimizer settings
            with testcase.assertRaises(self.ManualPhaseException):
                self.validate_my_user_input(
                    inputs,
                    {"@state": STATE_NOT_OPTIMIZING, "@num_features": 42},
                    {"method": "start"}
                )

            # Try to write in finish step
            settings = {
                "@state": STATE_FINISHING,
                "@settings": "Hello, Test!"
            }
            testcase.assertTrue(self.run_my_task(inputs, settings, outputs))
            outfile.seek(0)
            contents = outfile.read()
            testcase.assertEqual(contents, "Hello, Test!", contents)
            return True

    def knnga_dict(self):
        """
        Return a dictionary object with serializations
        of settings objects and a result summary (if any).
        """
        return {
            "@base": util.base_to_json(self.base),
            "@selection": self.selection.toJSON(),
            "@replacement": self.replacement.toJSON(),
            "@mutation": self.mutation.toJSON(),
            "@crossover": self.crossover.toJSON(),
            "@stop_criteria": self.stop_criteria.toJSON(),
            "@results": None if self.optimizer is None else {
                "generation": self.optimizer.generation,
                "bestFitness": self.optimizer.bestFitness,
            }
        }

    def load_from_settings(self, settings):
        self.base = util.json_to_base(settings["@base"])
        self.selection = util.SerializableSelection.fromJSON(
            settings["@selection"]
        )
        self.replacement = util.SerializableReplacement.fromJSON(
            settings["@replacement"]
        )
        self.mutation = util.SerializableMutation.fromJSON(
            settings["@mutation"]
        )
        self.crossover = util.SerializableCrossover.fromJSON(
            settings["@crossover"]
        )
        self.stop_criteria = util.SerializableStopCriteria.fromJSON(
            settings["@stop_criteria"]
        )

    def setup_optimizer(self, options, num_features):
        """
        Ensure we have the info necessary to run GA optimization.
        """
        assert num_features is not None, "NUM FEATURES"
        base = util.dict_to_base(options["base"])
        selection = util.SerializableSelection.from_dict(
            options["selection"]
        )
        replacement = util.SerializableReplacement.from_dict(
            options["replacement"]
        )
        mutation = util.SerializableMutation.from_dict(
            options["mutation"],
            num_features
        )
        crossover = util.SerializableCrossover.from_dict(
            options["crossover"],
            num_features
        )
        stop_criteria = util.SerializableStopCriteria.from_dict(
            options["stop_criteria"]
        )

        assert selection.method is not None, "No selection method"
        assert replacement.method is not None, "No replacement method"
        assert len(mutation.methods) > 0, "No mutation methods"
        assert len(crossover.methods) > 0, "No crossover methods"
        assert len(stop_criteria.methods) > 0, "No stop criteria"

        self.base, self.selection, self.replacement, self.mutation, \
            self.crossover, self.stop_criteria = base, selection,   \
            replacement, mutation, crossover, stop_criteria
