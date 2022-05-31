# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals
from gamera import knnga

import json


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
        self.methods.sort()
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
        self.methods.sort()
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
        self.methods.sort()
        self.mutation.setInversionMutation()

    def setShiftMutation(self):
        if not len([x for x in self.methods if x["method"] == "shift"]):
            self.methods.append(
                {
                    "method": "shift",
                    "parameters": {}
                }
            )
        self.methods.sort()
        self.mutation.setShiftMutation()

    def setSwapMutation(self):
        if not len([x for x in self.methods if x["method"] == "swap"]):
            self.methods.append(
                {
                    "method": "swap",
                    "parameters": {}
                }
            )
        self.methods.sort()
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
        self.methods.sort()
        self.crossover.setHypercubeCrossover(numFeatures, min, max, alpha)

    def setNPointCrossover(self, n):
        self.methods = [x for x in self.methods if x["method"] != "nPoint"]
        self.methods.append(
            {
                "method": "nPoint",
                "parameters": {"n": n}
            }
        )
        self.methods.sort()
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
        self.methods.sort()
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
        self.methods.sort()
        self.crossover.setSegmentCrossover(numFeatures, min, max, alpha)

    def setUniformCrossover(self, preference=DEFAULT_PREFERENCE):
        self.methods = [x for x in self.methods if x["method"] != "uniform"]
        self.methods.append(
            {
                "method": "uniform",
                "parameters": {"preference": preference}
            }
        )
        self.methods.sort()
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
        self.methods.sort()
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
        self.methods.sort()
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
        self.methods.sort()
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
        self.methods.sort()
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
