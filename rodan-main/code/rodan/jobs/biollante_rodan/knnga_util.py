# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals
from gamera import knnga

import json
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

# All default values are taken from the
# corresponding Gamera functions.
DEFAULT_PRESSURE = 2.0
DEFAULT_EXPONENT = 1.0
DEFAULT_TSIZE = 3
DEFAULT_RATE = 0.05
DEFAULT_ALPHA = 0.0
DEFAULT_ETA = 1.0
DEFAULT_PREFERENCE = 0.5
DEFAULT_OPTIMUM = 1.0
DEFAULT_EVAL_N = 5000
DEFAULT_GEN_N = 100
DEFAULT_MIN_GEN = 40
DEFAULT_NO_CHANGE_GEN = 10

# A function to compare dictionaries in python 3
# and A function to sort a list of dictionaries 
def dict_comparison(dict1, dict2):
    """Returns 0 if the two dicts are equal. Returns -1 if the first
    dict input is less than the second dict input and returns 1 otherwise. The rule is based on 
    python2 comparison between two dictionaries algorithm. 

    Args:
        dict1 (dict): first dictionary 
        dict2 (dict): second dictionary 

    Returns:
        int: 0 if dict1 == dict2 -1 if dict1 < dict2 1 otherwise.
    """
    # check if the dicts are equal 
    if dict1 == dict2: 
        return 0
        
    # check the keys of both 
    keys1= list(dict1.keys())
    keys2= list(dict2.keys())
 
    # unequal lengths in the first priority 
    # first to prevent the errors 
    if len(keys1) == 0:
        if len(keys2) == 0:
            return 0
        else:
            return -1
    if len(keys2) == 0:
        return 1

    list(dict1.keys()).sort()
    list(dict2.keys()).sort()

    if len(keys1) < len(keys2):
        return -1
    elif len(keys1) > len(keys1):
        return 1

    # equal lengths: compare the keys 
    for key_index in range(len(keys1)):
        if keys1[key_index] < keys2[key_index]:
            # the min element of the first is less 
            # so, in general, its less
            return -1
        elif keys1[key_index] > keys2[key_index]:
            # the min element of the first is greater
            # so, in general, its greater
            return 1

    # exited the loop -> same key lists 
    # now, looking into the values of the dictionary 
    for key_index in range(len(keys1)):
        value1 = dict1[keys1[key_index]]
        value2 = dict2[keys1[key_index]]
        if type(value1) == dict:
            # if both values are of type dict
            value_comparison= dict_comparison(value1, value2)
            if value_comparison < 0:
                return -1
            elif value_comparison > 0:
                return 1
            
        else:
            # when the type of the values are is not dict
            # python 3 allows comparison for those types 
            if value1 < value2 : return -1
            elif value1 > value2 : return 1

    # just in case (to avoid errors) - meaning that the two dicts are equal 
    return 0

# bubble sort for the methods list
# using bubble sort because the list is consisted of very limited number of dicts
def simple_sort(list_of_dicts):
    """To sort a list of dictionaries for the methods of the classes below 

    Args:
        list_of_dicts (list): the list to be sorted

    Returns:
        list: the sorted list of dicts 
    """
    for item in range(len(list_of_dicts)):
        for j in range(0, (len(list_of_dicts) - item - 1)):
            if dict_comparison(list_of_dicts[j],list_of_dicts[j + 1]) > 0:
                (list_of_dicts[j], list_of_dicts[j + 1]) = (list_of_dicts[j + 1], list_of_dicts[j])

    return list_of_dicts

class SerializableSelection():
    """
    Extension of gamera.knnga.GASelection that provides
    access to the selection and parameters used.
    """

    def __init__(self):
        self.method = None
        self.parameters = {}
        self.selection = knnga.GASelection()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            a = self.__dict__.copy()
            del a['selection']
            b = other.__dict__.copy()
            del b['selection']
            return a == b
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def setRandomSelection(self):
        self.method = "random"
        self.parameters = {}
        self.selection.setRandomSelection()

    def setRankSelection(
        self,
        pressure=DEFAULT_PRESSURE,
        exponent=DEFAULT_EXPONENT
    ):
        self.method = "rank"
        self.parameters = {
            "pressure": pressure,
            "exponent": exponent
        }
        self.selection.setRankSelection(pressure, exponent)

    def setRouletteWheel(self):
        self.method = "roulette"
        self.parameters = {}
        self.selection.setRoulettWheel()

    def setRouletteWheelScaled(self, pressure=DEFAULT_PRESSURE):
        self.method = "roulette_scaled"
        self.parameters = {"pressure": pressure}
        self.selection.setRoulettWheelScaled(pressure)

    def setStochUniSampling(self):
        self.method = "stochiastic"
        self.parameters = {}
        self.selection.setStochUniSampling()

    def setTournamentSelection(self, tSize=DEFAULT_TSIZE):
        self.method = "tournament"
        self.parameters = {"tSize": tSize}
        self.selection.setTournamentSelection(tSize)

    def toJSON(self):
        d = self.__dict__.copy()
        del d['selection']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        return SerializableSelection.from_dict(d)

    @staticmethod
    def from_dict(d):
        p = d["parameters"]
        e = SerializableSelection()

        if d["method"] == "random":
            e.setRandomSelection()
        elif d["method"] == "rank":
            if "pressure" in p and "exponent" in p:
                e.setRankSelection(p["pressure"], p["exponent"])
            elif "pressure" in p:
                e.setRankSelection(p["pressure"])
            elif "exponent" in p:
                e.setRankSelection(exponent=p["exponent"])
            else:
                e.setRankSelection()
        elif d["method"] == "roulette":
            e.setRouletteWheel()
        elif d["method"] == "roulette_scaled":
            if "pressure" in p:
                e.setRouletteWheelScaled(p["pressure"])
            else:
                e.setRouletteWheelScaled()
        elif d["method"] == "stochiastic":
            e.setStochUniSampling()
        elif d["method"] == "tournament":
            if "tSize" in p:
                e.setTournamentSelection(p["tSize"])
        return e


class SerializableReplacement():
    """
    Extension of gamera.knnga.GAReplacement that provides
    access to selection method and parameters.
    """

    def __init__(self):
        self.method = None
        self.parameters = {}
        self.replacement = knnga.GAReplacement()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            a = self.__dict__.copy()
            del a['replacement']
            b = other.__dict__.copy()
            del b['replacement']
            return a == b
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def setGenerationalReplacement(self):
        self.method = "generational"
        self.parameters = {}
        self.replacement.setGenerationalReplacement()

    def setSSGAdetTournament(self, tSize=DEFAULT_TSIZE):
        self.method = "SSGAdetTournament"
        self.parameters = {"tSize": tSize}
        self.replacement.setSSGAdetTournament(tSize)

    def setSSGAworse(self):
        self.method = "SSGAworse"
        self.parameters = {}
        self.replacement.setSSGAworse()

    def toJSON(self):
        d = self.__dict__.copy()
        del d['replacement']
        return json.dumps(d)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        return SerializableReplacement.from_dict(d)

    @staticmethod
    def from_dict(d):
        e = SerializableReplacement()
        if d["method"] == "generational":
            e.setGenerationalReplacement()
        elif d["method"] == "SSGAdetTournament":
            if "tSize" in d["parameters"]:
                e.setSSGAdetTournament(d["parameters"]["tSize"])
            else:
                e.setSSGAdetTournament()
        elif d["method"] == "SSGAworse":
            e.setSSGAworse()
        return e


class SerializableMutation:
    """
    Extension of gamera.knnga.GAMutation that provides
    access to mutation methods and parameters
    """

    def __init__(self):
        self.methods = []
        self.mutation = knnga.GAMutation()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.methods == other.methods
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def setBinaryMutation(self, rate=DEFAULT_RATE, normalize=True):
        self.methods = [x for x in self.methods if x["method"] != "binary"]
        self.methods.append(
            {
                "method": "binary",
                "parameters": {
                    "rate": rate,
                    "normalize": normalize
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        # the sort is either by the keys or the values. maybe using external libs? maybe skipping? maybe checking gamera source code?
        self.mutation.setBinaryMutation(rate, normalize)

    def setGaussMutation(self, numFeatures, minVal, maxVal, sigma, rate):
        self.methods = [x for x in self.methods if x["method"] != "gauss"]
        self.methods.append(
            {
                "method": "gauss",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": minVal,
                    "max": maxVal,
                    "sigma": sigma,
                    "rate": rate
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        # mostly the same as list - most prolly have to be sorted with the key of the dict
        self.mutation.setGaussMutation(
            numFeatures,
            minVal,
            maxVal,
            sigma,
            rate
        )

    def setInversionMutation(self):
        if not len([x for x in self.methods if x["method"] == "inversion"]):
            self.methods.append(
                {
                    "method": "inversion",
                    "parameters": {}
                }
            )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.mutation.setInversionMutation()

    def setShiftMutation(self):
        if not len([x for x in self.methods if x["method"] == "shift"]):
            self.methods.append(
                {
                    "method": "shift",
                    "parameters": {}
                }
            )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.mutation.setShiftMutation()

    def setSwapMutation(self):
        if not len([x for x in self.methods if x["method"] == "swap"]):
            self.methods.append(
                {
                    "method": "swap",
                    "parameters": {}
                }
            )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.mutation.setSwapMutation()

    def toJSON(self):
        return json.dumps(self.methods)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        return SerializableMutation.from_dict(d)

    @staticmethod
    def from_dict(d, num_features=None):
        e = SerializableMutation()
        for op in d:
            m = op["method"]
            p = op["parameters"]

            if m == "binary":
                if "rate" in p and "normalize" in p:
                    e.setBinaryMutation(p["rate"], p["normalize"])
                elif "rate" in p:
                    e.setBinaryMutation(p["rate"])
                elif "normalize" in p:
                    e.setBinaryMutation(normalize=p["normalize"])
                else:
                    e.setBinaryMutation
            elif m == "gauss":
                num = num_features if num_features is not None \
                    else p["numFeatures"]
                e.setGaussMutation(
                    num,
                    p["min"],
                    p["max"],
                    p["sigma"],
                    p["rate"]
                )
            elif m == "inversion":
                e.setInversionMutation()
            elif m == "shift":
                e.setShiftMutation()
            elif m == "swap":
                e.setSwapMutation()

        return e


class SerializableCrossover:
    """
    Serializable version of gamera.knnga.GACrossover.
    """

    def __init__(self):
        self.methods = []
        self.crossover = knnga.GACrossover()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.methods == other.methods
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def setHypercubeCrossover(
        self,
        numFeatures,
        min,
        max,
        alpha=DEFAULT_ALPHA
    ):
        self.methods = [x for x in self.methods if x["method"] != "hypercube"]
        self.methods.append(
            {
                "method": "hypercube",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "alpha": alpha
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.crossover.setHypercubeCrossover(numFeatures, min, max, alpha)

    def setNPointCrossover(self, n):
        self.methods = [x for x in self.methods if x["method"] != "nPoint"]
        self.methods.append(
            {
                "method": "nPoint",
                "parameters": {"n": n}
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.crossover.setNPointCrossover(n)

    def setSBXCrossover(self, numFeatures, min, max, eta=DEFAULT_ETA):
        self.methods = [x for x in self.methods if x["method"] != "sbx"]
        self.methods.append(
            {
                "method": "sbx",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "eta": eta
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.crossover.setSBXcrossover(numFeatures, min, max, eta)

    def setSegmentCrossover(self, numFeatures, min, max, alpha=DEFAULT_ALPHA):
        self.methods = [x for x in self.methods if x["method"] != "segment"]
        self.methods.append(
            {
                "method": "segment",
                "parameters": {
                    "numFeatures": numFeatures,
                    "min": min,
                    "max": max,
                    "alpha": alpha
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.crossover.setSegmentCrossover(numFeatures, min, max, alpha)

    def setUniformCrossover(self, preference=DEFAULT_PREFERENCE):
        self.methods = [x for x in self.methods if x["method"] != "uniform"]
        self.methods.append(
            {
                "method": "uniform",
                "parameters": {"preference": preference}
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.crossover.setUniformCrossover(preference)

    def toJSON(self):
        return json.dumps(self.methods)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        return SerializableCrossover.from_dict(d)

    @staticmethod
    def from_dict(d, num_features=None):
        e = SerializableCrossover()
        for op in d:
            m = op["method"]
            p = op["parameters"]

            if m == "hypercube":
                num = num_features if num_features is not None \
                    else p["numFeatures"]
                if "alpha" in p:
                    e.setHypercubeCrossover(
                        num,
                        p["min"],
                        p["max"],
                        p["alpha"]
                    )
                else:
                    e.setHypercubeCrossover(
                        num,
                        p["min"],
                        p["max"]
                    )
            elif m == "nPoint":
                e.setNPointCrossover(p["n"])
            elif m == "sbx":
                num = num_features if num_features is not None \
                    else p["numFeatures"]
                if "eta" in p:
                    e.setSBXCrossover(
                        num,
                        p["min"],
                        p["max"],
                        p["eta"]
                    )
                else:
                    e.setSBXCrossover(
                        num,
                        p["min"],
                        p["max"]
                    )
            elif m == "segment":
                num = num_features if num_features is not None \
                    else p["numFeatures"]
                if "alpha" in p:
                    e.setSegmentCrossover(
                        num,
                        p["min"],
                        p["max"],
                        p["alpha"]
                    )
                else:
                    e.setSegmentCrossover(
                        num,
                        p["min"],
                        p["max"]
                    )
            elif m == "uniform":
                if "preference" in p:
                    e.setUniformCrossover(p["preference"])
                else:
                    e.setUniformCrossover()
        return e


class SerializableStopCriteria:
    """
    Serializable version of gamera.knnga.GAStopCriteria
    """

    def __init__(self):
        self.methods = []
        self.sc = knnga.GAStopCriteria()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.methods == other.methods
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def setBestFitnessStop(self, optimum=DEFAULT_OPTIMUM):
        self.methods = [x for x in self.methods
                        if x["method"] != "bestFitness"]
        self.methods.append(
            {
                "method": "bestFitness",
                "parameters": {"optimum": optimum}
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.sc.setBestFitnessStop(optimum)

    def setMaxFitnessEvals(self, n=DEFAULT_EVAL_N):
        self.methods = [x for x in self.methods
                        if x["method"] != "maxFitnessEvals"]
        self.methods.append(
            {
                "method": "maxFitnessEvals",
                "parameters": {"n": n}
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.sc.setMaxFitnessEvals(n)

    def setMaxGenerations(self, n=DEFAULT_GEN_N):
        self.methods = [x for x in self.methods
                        if x["method"] != "maxGenerations"]
        self.methods.append(
            {
                "method": "maxGenerations",
                "parameters": {"n": n}
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.sc.setMaxGenerations(n)

    def setSteadyStateStop(
        self,
        minGens=DEFAULT_MIN_GEN,
        noChangeGens=DEFAULT_NO_CHANGE_GEN
    ):
        self.methods = [x for x in self.methods
                        if x["method"] != "steadyState"]
        self.methods.append(
            {
                "method": "steadyState",
                "parameters": {
                    "minGens": minGens,
                    "noChangeGens": noChangeGens
                }
            }
        )
        logger.info(("methods is {0}").format(self.methods))
        self.methods = simple_sort(self.methods)
        self.sc.setSteadyStateStop(minGens, noChangeGens)

    def toJSON(self):
        return json.dumps(self.methods)

    @staticmethod
    def fromJSON(jsonString):
        d = json.loads(jsonString)
        return SerializableStopCriteria.from_dict(d)

    @staticmethod
    def from_dict(d):
        e = SerializableStopCriteria()
        for op in d:
            m = op["method"]
            p = op["parameters"]

            if m == "bestFitness":
                if "optimum" in p:
                    e.setBestFitnessStop(p["optimum"])
                else:
                    e.setBestFitnessStop()
            elif m == "maxFitnessEvals":
                if "n" in p:
                    e.setMaxFitnessEvals(p["n"])
                else:
                    e.setMaxFitnessEvals()
            elif m == "maxGenerations":
                if "n" in p:
                    e.setMaxGenerations(p["n"])
                else:
                    e.setMaxGenerations()
            elif m == "steadyState":
                if "minGens" in p and "noChangeGens" in p:
                    e.setSteadyStateStop(p["minGens"], p["noChangeGens"])
                elif "minGens" in p:
                    e.setSteadyStateStop(p["minGens"])
                elif "noChangeGens" in p:
                    e.setSteadyStateStop(noChangeGens=p["noChangeGens"])
                else:
                    e.setSteadyStateStop()
        return e


def base_to_json(setting):
    return json.dumps({
        "opMode": setting.opMode,
        "popSize": setting.popSize,
        "crossRate": setting.crossRate,
        "mutRate": setting.mutRate
    })


def json_to_base(jsonString):
    vals = json.loads(jsonString)
    return dict_to_base(vals)


def dict_to_base(vals):
    base = knnga.GABaseSetting()
    base.opMode = vals["opMode"]
    base.popSize = vals["popSize"]
    base.crossRate = vals["crossRate"]
    base.mutRate = vals["mutRate"]
    return base
