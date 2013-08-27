import os
import tempfile
import shutil
from datetime import datetime

from celery import Task
from gamera.core import init_gamera
from gamera import knn, knnga
from django.core.files import File
from django.utils import timezone
from rodan.jobs.util import taskutil
from rodan.models.classifier import Classifier
from rodan.models.classifiersetting import ClassifierSetting
from rodan.helpers.dbmanagement import refetch_from_db
from rodan.helpers.exceptions import ObjectDeletedError


class OptimizeAllClassifiersTask(Task):

    def run(self, *args, **kwargs):
        """
        This runs the optimization on all the classifiers in the project.

        The optimization can be run with many different settings. For
        convenience, I've included all the settings in this script and
        commented out the ones that I'm not currently using. Feel free
        to tweak with them.

        For most of the arguments, I hope it is implicitly clear which
        ones are int and which ones are float/double. For example,
        arg_one=3 means arg_one should be an int, while arg_two=3.0 means
        arg_two should be a double/float.

        Later on, we can build a client interface to tweak all these settings.

        Detailed documentation can be found at http://gamera.sourceforge.net/doc/html/ga_optimization.html

        Code template taken from http://gamera.sourceforge.net/doc/html/ga_optimization.html#script-usage
        """
        init_gamera()

        classifiers = Classifier.objects.all()

        for classifier in classifiers:
            project = classifier.project

            optimization_start = timezone.now()
            print "Optimizing classifier {0}".format(classifier.name)

            cknn = knn.kNNNonInteractive(classifier.file_path,
                                               features = 'all',
                                               normalize = False)

            print "Setting base settings"
            baseSettings = knnga.GABaseSetting()
            baseSettings.opMode = knnga.GA_WEIGHTING  # Or knnga.GA_SELECTION
            baseSettings.popSize = 75
            baseSettings.crossRate = 0.95
            baseSettings.mutRate = 0.05

            print "Settings selection options"
            selection = knnga.GASelection()
            selection.setRoulettWheelScaled(2.0)
            #selection.setRoulettWheelScaled(double pressure=2.0)  # Pressure \in [1,2]
            #selection.setRandomSelection()
            #selection.setRankSelection(pressure=2.0, exponent=1.0)
            #selection.setStochUniSampling()
            #selection.setRoulettWheel()
            #selection.setTournamentSelection(tSize=3)

            print "Setting crossover settings"
            crossover = knnga.GACrossover()
            crossover.setUniformCrossover(0.5)
            #crossover.setUniformCrossover(double preference = 0.5)
            #crossover.setNPointCrossover(n=1)
            #crossover.setHypercubeCrossover(int numFeatures, double min, double max, alpha=0.0)
            #crossover.setSBXcrossover(int numFeatures, double min, double max, eta=0.0)
            #crossover.setSegmentCrossover(int numFeatures, double min, double max, alpha=0.0)

            print "Setting Mutation settings"
            mutation = knnga.GAMutation()
            #mutation.setShiftMutation()
            mutation.setSwapMutation()
            #mutation.setBinaryMutation(rate=0.05, normalize=False)
            mutation.setBinaryMutation(0.05, False)
            #mutation.setGaussMutation(int numFeatures, double min, double max, double sigma, double rate)
            #mutation.setInversionMutation()

            print "Setting replacement settings"
            replacement = knnga.GAReplacement()
            replacement.setSSGAdetTournament(3)
            #replacement.setSSGAdetTournament(int tSize=3)
            #replacement.setGenerationalReplacement()
            #replacement.setSSGAworse()

            print "Setting stop criteria"
            stop = knnga.GAStopCriteria()
            #stop.setSteadyStateStop(int minGens=100, int noChangeGens=20)
            stop.setSteadyStateStop(100, 20)
            #stop.setBestFitnessStop(optimum=1.0)
            #stop.setMaxFitnessEvals(n=5000)
            #stop.setMaxGenerations(100)

            print "Setting parallelization settings"
            parallel = knnga.GAParallelization()
            parallel.mode = True
            parallel.thredNum = 4

            # Combine each setting object into one main object
            ga = knnga.GAOptimization(cknn, baseSettings, selection,
                                      crossover, mutation, replacement,
                                      stop, parallel)

            print "Beginning calculation..."
            ga.startCalculation()

            print "Done! Saving the produced settings."

            optimization_end = timezone.now()

            # Choosing a name for the new classifier_setting
            date_string = datetime.now().strftime("%Y_%m_%d_%I%M%p")
            setting_name = "{0}:{1} Periodic Optimization".format(classifier.name[:200], date_string,)

            tdir = tempfile.mkdtemp()
            temp_xml_filepath = os.path.join(tdir, str(classifier.uuid) + '.xml')
            cknn.save_settings(temp_xml_filepath)

            try:
                classifier = refetch_from_db(classifier)
            except ObjectDeletedError:
                print "Sadly classifier {0} was deleted.".format(classifier.name)
                # Now this is a lonely setting file with no classifier to hang out with.
                classifier = None


            classifier_setting_instance = ClassifierSetting.objects.create(name=setting_name,
                                                                           project=project,
                                                                           fitness=ga.bestFitness,
                                                                           producer=classifier,
                                                                           optimization_started_at = optimization_start,
                                                                           optimization_finished_at = optimization_end)

            with open(temp_xml_filepath, 'rb') as f:
                taskutil.save_file_field(classifier_setting_instance.settings_file, 'settings_xml', File(f))

            shutil.rmtree(tdir)

