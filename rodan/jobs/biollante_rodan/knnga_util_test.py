# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import unicode_literals
from gamera import knnga

import json
import knnga_util
import unittest


class TestSelection(unittest.TestCase):
    def setUp(self):
        self.selection = knnga_util.SerializableSelection()

    def tearDown(self):
        self.selection = None

    def test_to_json(self):
        self.selection.setRandomSelection()     # This should be overwritten
        self.selection.setRankSelection(1.5, 1.0)
        self.assertEqual(
            json.loads(self.selection.toJSON()),
            {
                "method": "rank",
                "parameters": {
                    "pressure": 1.5,
                    "exponent": 1.0
                }
            }
        )

    def test_from_json(self):
        self.selection.setRouletteWheelScaled()
        testJSON = self.selection.toJSON()
        test = knnga_util.SerializableSelection.fromJSON(testJSON)
        self.assertEqual(self.selection, test)

    def test_overwrite(self):
        self.selection.setRouletteWheel()
        self.assertEqual(self.selection.method, "roulette")
        self.assertEqual(len(self.selection.parameters), 0)
        self.selection.setTournamentSelection(3)
        self.assertEqual(self.selection.method, "tournament")
        self.assertEqual(len(self.selection.parameters), 1)
        self.assertEqual(self.selection.parameters["tSize"], 3)

    def test_all_settings(self):
        # This just shouldn't error
        self.selection.setRandomSelection()
        self.selection.setRankSelection()
        self.selection.setRouletteWheel()
        self.selection.setRouletteWheelScaled()
        self.selection.setStochUniSampling()
        self.selection.setTournamentSelection()


class TestReplacement(unittest.TestCase):
    def setUp(self):
        self.replacement = knnga_util.SerializableReplacement()

    def tearDown(self):
        self.replacement = None

    def test_to_json(self):
        # This should be overwritten
        self.replacement.setGenerationalReplacement()
        self.replacement.setSSGAdetTournament(30)
        self.assertEqual(
            json.loads(self.replacement.toJSON()),
            {
                "method": "SSGAdetTournament",
                "parameters": {"tSize": 30}
            }
        )

    def test_from_json(self):
        self.replacement.setSSGAworse()
        testJSON = self.replacement.toJSON()
        test = knnga_util.SerializableReplacement.fromJSON(testJSON)
        self.assertEqual(self.replacement, test)

    def test_overwrite(self):
        self.replacement.setSSGAworse()
        self.assertEqual(self.replacement.method, "SSGAworse")
        self.assertEqual(len(self.replacement.parameters), 0)
        self.replacement.setSSGAdetTournament(3)
        self.assertEqual(self.replacement.method, "SSGAdetTournament")
        self.assertEqual(len(self.replacement.parameters), 1)
        self.assertEqual(self.replacement.parameters["tSize"], 3)

    def test_all_settings(self):
        # This just shouldn't error
        self.replacement.setGenerationalReplacement()
        self.replacement.setSSGAdetTournament()
        self.replacement.setSSGAworse()


class TestMutation(unittest.TestCase):
    def setUp(self):
        self.mutation = knnga_util.SerializableMutation()

    def tearDown(self):
        self.mutation = None

    def test_to_json(self):
        # These should be combined
        self.mutation.setInversionMutation()
        self.mutation.setGaussMutation(30, 0.0, 1.0, 0.5, 1.0)
        self.assertEqual(
            json.loads(self.mutation.toJSON()),
            sorted([{
                "method": "inversion",
                "parameters": {}
            }, {
                "method": "gauss",
                "parameters": {
                    "numFeatures": 30,
                    "min": 0.0,
                    "max": 1.0,
                    "sigma": 0.5,
                    "rate": 1.0
                }
            }])
        )

    def test_from_json(self):
        self.mutation.setInversionMutation()
        self.mutation.setBinaryMutation()
        testJSON = self.mutation.toJSON()
        test = knnga_util.SerializableMutation.fromJSON(testJSON)
        self.assertEqual(self.mutation, test)

    def test_overwrite_same(self):
        self.mutation.setBinaryMutation(0.07, False)
        self.mutation.setBinaryMutation(0.05, True)
        self.assertEqual(len(self.mutation.methods), 1)
        self.assertEqual(
            self.mutation.methods,
            [{
                "method": "binary",
                "parameters": {
                    "rate": 0.05,
                    "normalize": True
                }
            }]
        )

    def test_all_settings(self):
        self.mutation.setBinaryMutation()
        self.mutation.setGaussMutation(10, 0.0, 1.0, 0.05, 1.0)
        self.mutation.setInversionMutation()
        self.mutation.setShiftMutation()
        self.mutation.setSwapMutation()


class TestCrossover(unittest.TestCase):
    def setUp(self):
        self.crossover = knnga_util.SerializableCrossover()

    def tearDown(self):
        self.tearDown = None

    def test_to_json(self):
        # These should be combined
        self.crossover.setUniformCrossover()
        self.crossover.setHypercubeCrossover(30, 0.0, 1.0)
        self.assertEqual(
            json.loads(self.crossover.toJSON()),
            sorted([{
                "method": "uniform",
                "parameters": {"preference": 0.5}
            }, {
                "method": "hypercube",
                "parameters": {
                    "numFeatures": 30,
                    "min": 0.0,
                    "max": 1.0,
                    "alpha": 0.0
                }
            }])
        )

    def test_from_json(self):
        self.crossover.setSegmentCrossover(30, 0.0, 1.0)
        testJSON = self.crossover.toJSON()
        test = knnga_util.SerializableCrossover.fromJSON(testJSON)
        self.assertEqual(self.crossover, test)

    def test_overwrite_same(self):
        self.crossover.setNPointCrossover(10)
        self.crossover.setNPointCrossover(20)
        self.assertEqual(len(self.crossover.methods), 1)
        self.assertEqual(
            self.crossover.methods,
            [{
                "method": "nPoint",
                "parameters": {"n": 20}
            }]
        )

    def test_all_settings(self):
        self.crossover.setHypercubeCrossover(30, 0.0, 1.0, 0.05)
        self.crossover.setNPointCrossover(5)
        self.crossover.setSBXCrossover(30, 0.0, 1.0, 1.15)
        self.crossover.setSegmentCrossover(30, 0.0, 1.0, 0.95)
        self.crossover.setUniformCrossover(0.5)


class TestStopCriteria(unittest.TestCase):
    def setUp(self):
        self.sc = knnga_util.SerializableStopCriteria()

    def tearDown(self):
        self.sc = None

    def test_to_json(self):
        # These should be combined
        self.sc.setMaxGenerations(20)
        self.sc.setMaxFitnessEvals()
        self.assertEqual(
            json.loads(self.sc.toJSON()),
            sorted([{
                "method": "maxGenerations",
                "parameters": {"n": 20}
            }, {
                "method": "maxFitnessEvals",
                "parameters": {"n": 5000}
            }])
        )

    def test_from_json(self):
        self.sc.setSteadyStateStop()
        testJSON = self.sc.toJSON()
        test = knnga_util.SerializableStopCriteria.fromJSON(testJSON)
        self.assertEqual(self.sc, test)

    def test_overwrite_same(self):
        self.sc.setMaxGenerations(100)
        self.sc.setMaxGenerations(150)
        self.assertEqual(len(self.sc.methods), 1)
        self.assertEqual(
            self.sc.methods,
            [{
                "method": "maxGenerations",
                "parameters": {"n": 150}
            }]
        )

    def test_all_settings(self):
        self.sc.setBestFitnessStop(1.0)
        self.sc.setMaxFitnessEvals(6000)
        self.sc.setMaxGenerations(102)
        self.sc.setSteadyStateStop(40, 15)


class TestBaseSetting(unittest.TestCase):
    def test_to_json(self):
        base = knnga.GABaseSetting()
        self.assertEqual(
            json.loads(knnga_util.base_to_json(base)),
            {
                "opMode": knnga.GA_SELECTION,
                "popSize": 75,
                "crossRate": 0.95,
                "mutRate": 0.05
            }
        )

    def test_from_json(self):
        default = knnga.GABaseSetting()
        default.popSize = 80
        default.mutRate = 0.06
        loaded = knnga_util.json_to_base(
            json.dumps({
                "opMode": knnga.GA_SELECTION,
                "popSize": 80,
                "crossRate": 0.95,
                "mutRate": 0.06
            })
        )
        self.assertEqual(default.opMode, loaded.opMode)
        self.assertEqual(default.popSize, loaded.popSize)
        self.assertEqual(default.crossRate, loaded.crossRate)
        self.assertEqual(default.mutRate, loaded.mutRate)
