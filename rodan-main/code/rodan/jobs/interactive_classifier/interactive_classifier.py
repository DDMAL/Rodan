import os
import copy
import json
import gamera.classify
import gamera.core
import gamera.gamera_xml
import gamera.knn
import image_utilities
from celery import uuid
from gamera.plugins.image_utilities import union_images
import gamera.plugins.segmentation
from gamera.gamera_xml import glyphs_from_xml
from gamera.gamera_xml import LoadXML
from rodan.jobs.interactive_classifier.intermediary.gamera_glyph import GameraGlyph
from rodan.jobs.interactive_classifier.intermediary.gamera_xml import GameraXML
from rodan.jobs.interactive_classifier.intermediary.run_length_image import \
    RunLengthImage
from rodan.settings import MEDIA_URL, MEDIA_ROOT
from django.http import HttpResponse

class ClassifierStateEnum:
    IMPORT_XML = 0
    CLASSIFYING = 1
    EXPORT_XML = 2
    GROUP_AND_CLASSIFY = 3
    GROUP = 4
    SAVE = 5


def media_file_path_to_public_url(media_file_path):
    chars_to_remove = len(MEDIA_ROOT)
    return os.path.join(MEDIA_URL, media_file_path[chars_to_remove:])

def convert_to_gamera_image(glyph):
    return RunLengthImage(
        glyph['ulx'],
        glyph['uly'],
        glyph['ncols'],
        glyph['nrows'],
        glyph['image']
    ).get_gamera_image()


def get_manual_glyphs(glyphs):
    """
    From the glyph list, extract the Gamera ImageList of manual glyphs.
    """
    # Prepare the training glyphs
    training_glyphs = []
    for glyph in glyphs:
        if glyph['id_state_manual']:
            # Get the gamera image
            gamera_image = convert_to_gamera_image(glyph)
            # It's a training glyph!
            gamera_image.classify_manual(glyph['class_name'])
            training_glyphs.append(gamera_image)
    return training_glyphs


def output_corrected_glyphs(cknn, glyphs, inputs, output_path):
    """
    Output the corrected data to disk.  This includes both the manually
    corrected and the automatically corrected glyphs.
    """
    output_images = []
    for glyph in glyphs:
        gamera_image = RunLengthImage(
            glyph['ulx'],
            glyph['uly'],
            glyph['ncols'],
            glyph['nrows'],
            glyph['image']
        ).get_gamera_image()
        if glyph['id_state_manual']:
            gamera_image.classify_manual(glyph['class_name'])
        else:
            if 'GameraXML - Training Data' in inputs:
                if (glyph['class_name'] != "UNCLASSIFIED"):
                    gamera_image.classification_state = gamera.core.AUTOMATIC
                    gamera_image.id_name = [(glyph['confidence'],glyph['class_name'])]
                if gamera_image.classification_state == gamera.core.UNCLASSIFIED:
                    cknn.classify_glyph_automatic(gamera_image)
            else:
                if (glyph['class_name'] != "UNCLASSIFIED"):
                    cknn.classify_glyph_automatic(gamera_image)
        output_images.append(gamera_image)
        # Dump all the glyphs to disk
    cknn.generate_features_on_glyphs(output_images)
    output_xml = gamera.gamera_xml.WriteXMLFile(glyphs=output_images,
                                                with_features=True)
    output_xml.write_filename(output_path)


def run_output_stage(cknn, glyphs, inputs, outputs, class_names):
    """
    The job is complete, so save the results to disk.
    """
    if 'GameraXML - Training Data' in outputs:
        output_training_classifier_path = outputs['GameraXML - Training Data'][0][
            'resource_path']
        # Save the training data to disk
        cknn.to_xml_filename(output_training_classifier_path)

    if 'Plain Text - Class Names' in outputs:
        output_classes_path = outputs['Plain Text - Class Names'][0]['resource_path']
        class_names = [n for n in class_names if not n == "UNCLASSIFIED"]
        reverse_names = sorted(class_names)
        outfile = open(output_classes_path, "w")
        for name in reverse_names:
            outfile.write(name + '\n')
        outfile.close()


    output_classified_data_path = outputs['GameraXML - Classified Glyphs'][0][
        'resource_path']
    # Save the rest of the glyphs
    output_corrected_glyphs(cknn, glyphs, inputs, output_classified_data_path)


def prepare_classifier(training_database, glyphs, features_file_path):
    """
    Given a training database and a list of glyph dicts, train the classifier
    """
    # Prepare the training glyphs
    database = get_manual_glyphs(glyphs)

    # The database is a mixture of the original database plus all
    # our manual corrections that we've done in the GUI.
    for g in training_database:
        glyph = convert_to_gamera_image(g)

        if g['id_state_manual']:
            glyph.classify_manual(g['class_name'])
        else:
            glyph.classify_automatic(g['class_name'])
        database.append(glyph)

    # Train the classifier
    classifier = gamera.knn.kNNInteractive(database=database,
                                           perform_splits=True,
                                           num_k=1)
    # Load features document if applicable
    if features_file_path:
        classifier.load_settings(features_file_path)
    return classifier

def group_and_correct(glyphs, user_options, training_database, features_file_path):
    """
    Run the automatic correction stage of the Rodan job.
    """
    # Train a classifier
    cknn = prepare_classifier(training_database,
                              glyphs,
                              features_file_path)
    # The automatic classifications
    manual =[]
    gamera_glyphs = []

    for glyph in glyphs:
        if not glyph['id_state_manual']:
            # It's a glyph to be classified
            gamera_glyph = RunLengthImage(
                glyph['ulx'],
                glyph['uly'],
                glyph['ncols'],
                glyph['nrows'],
                glyph['image']
            ).get_gamera_image()

            gamera_glyphs.append(gamera_glyph)
        else:
            manual.append(glyph)

    distance = int(user_options['distance'])
    parts = int(user_options['parts'])
    graph = int(user_options['graph'])
    criterion = user_options['criterion']
    if(user_options['func'] == "Shaped"):
        func = gamera.classify.ShapedGroupingFunction(distance)
    else:
        func = gamera.classify.BoundingBoxGroupingFunction(distance)


    # Group and reclassify
    add, remove = cknn.group_list_automatic(gamera_glyphs, grouping_function=func,
                                                        max_parts_per_group=parts,
                                                        max_graph_size=graph,
                                                        criterion = criterion)

    # Taking out the manual glyphs so that the indices of the two lists will match
    for g in manual:
        glyphs.remove(g)

    # Removing
    for elem in remove:
        index = gamera_glyphs.index(elem)
        gamera_glyphs.remove(elem)
        glyphs.remove(glyphs[index])

    # Reassigning values after classification
    for i in range(len(gamera_glyphs)):
        glyphs[i]['class_name'] = gamera_glyphs[i].get_main_id().decode()
        glyphs[i]['confidence'] = gamera_glyphs[i].get_confidence().decode()

    # Adding new glyphs
    for elem in add:
        new_glyph = GameraGlyph(
            class_name = elem.get_main_id(),
            rle_image = elem.to_rle(),
            ncols = elem.ncols,
            nrows = elem.nrows,
            ulx = elem.ul.x,
            uly = elem.ul.y,
            id_state_manual = False,
            confidence = elem.get_confidence()).to_dict()

        glyphs.append(new_glyph)

    # Put the manual glyphs back
    for g in manual:
        glyphs.append(g)

    return cknn

def run_correction_stage(glyphs, training_database, features_file_path):
    """
    Run the automatic correction stage of the Rodan job.
    """
    # Train a classifier
    cknn = prepare_classifier(training_database,
                              glyphs,
                              features_file_path)
    # The automatic classifications
    for glyph in glyphs:
        if not glyph['id_state_manual']:
            # It's a glyph to be classified
            gamera_glyph = RunLengthImage(
                glyph['ulx'],
                glyph['uly'],
                glyph['ncols'],
                glyph['nrows'],
                glyph['image']
            ).get_gamera_image()
            # Classify it!

            cknn.classify_glyph_automatic(gamera_glyph)
            # Save the classification back into memory
            result, confidence = cknn.guess_glyph_automatic(gamera_glyph)
            glyph['class_name'] = result[0][1]
            if confidence:
                glyph['confidence'] = confidence[0]
            else:
                glyph['confidence'] = 0
    return cknn



def serialize_glyphs_to_json(glyphs):
    """
    Serialize the glyphs as a JSON dict grouped by short code
    """
    output = {}
    for glyph in glyphs:
        for k in glyph.keys():
            if type(glyph[k]) is bytes:
                glyph[k]=glyph[k].decode()
        class_name = glyph['class_name']
        if class_name not in output:
            output[class_name] = []
        output[class_name].append(glyph)
    # Sort the glyphs by confidence
    for class_name in output.keys():
        output[class_name] = sorted(output[class_name],
                                    key=lambda g: g["confidence"])
    return json.dumps(output)


def serialize_class_names_to_json(settings):
    """
    Get JSON representing the list of all class names in the classifier.
    """
    glyphs = settings['glyphs']
    training_database = settings['training_glyphs']
    imported_class_names = settings['imported_class_names']

    name_set = set()
    database = glyphs + training_database
    # Add the glyph short codes
    for image in database:
        name_set.add(image['class_name'])

    for name in imported_class_names:
        name_set.add(name)

    settings['class_names'] = list(name_set)

    return json.dumps(sorted(list(name_set)))


def serialize_data(settings):
    """
    Serialize the short codes and glyphs to JSON and store them in settings.
    """

    # Make sure the manual glyphs get put in the same view as training glyphs
    manual = []
    for glyph in settings['glyphs']:
        if glyph['id_state_manual']:
            manual.append(glyph)

    settings['class_names_json'] = serialize_class_names_to_json(settings)
    settings['glyphs_json'] = serialize_glyphs_to_json(settings['glyphs'])
    settings['training_json'] = serialize_glyphs_to_json(settings['training_glyphs'] + manual)


def filter_parts(settings):
    """
    Remove grouped components and glyphs that have been deleted or split.
    """
    parts = []
    temp = copy.copy(settings['glyphs'])
    for glyph in settings['glyphs']:
        name = glyph['class_name']
        if name.startswith("_split") or name.startswith("_group") or name.startswith("_delete"):
            parts.append(glyph)
            temp.remove(glyph)
    settings['glyphs'] = temp
    # Remove from the training glyphs as well
    temp2 = copy.copy(settings['training_glyphs'])
    for glyph in settings['training_glyphs']:
        name = glyph['class_name']
        if name.startswith("_split") or name.startswith("_group") or name.startswith("_delete"):
            temp2.remove(glyph)
    settings['training_glyphs'] = temp2
    return parts


def add_grouped_glyphs(settings):
    """
    Add new glyphs that have been grouped to the glyph dictionary.
    """
    grouped_glyphs = settings['@grouped_glyphs']

    for glyph in grouped_glyphs:
        new_glyph = GameraGlyph(
        gid = glyph["id"],
        class_name = glyph['class_name'],
        rle_image = glyph['rle_image'],
        ncols = glyph['ncols'],
        nrows = glyph['nrows'],
        ulx = glyph['ulx'],
        uly = glyph['uly'],
        id_state_manual = glyph['id_state_manual'],
        confidence = glyph['confidence']
        ).to_dict()

        settings['glyphs'].append(new_glyph)

    settings['@grouped_glyphs'] = []

def update_changed_glyphs(settings):
    """
    Update the glyph objects that have been changed since the last round of classification
    """
    # Build a hash of the changed glyphs by their id
    changed_glyph_hash = {g['id']: g for g in settings['@changed_glyphs']}
    changed_training_hash = {g['id']: g for g in settings['@changed_training_glyphs']}
    deleted_glyph_hash = {g['id']: g for g in settings['@deleted_glyphs']}
    deleted_training_hash = {g['id']: g for g in settings['@deleted_training_glyphs']}

    changed_glyph_hash.update(deleted_glyph_hash)
    changed_training_hash.update(deleted_training_hash)

    # Loop through all glyphs.  Update if changed.
    for glyph in settings['glyphs']:
        if not changed_glyph_hash:
            # No more changed glyphs, so break
            break
        else:
            # There are still glyphs to update
            key = glyph['id']
            # Grab the changed glyph
            if key in changed_glyph_hash:
                changed_glyph = changed_glyph_hash[key]
                # Update the Glyph proper
                glyph['class_name'] = changed_glyph['class_name']
                glyph['id_state_manual'] = changed_glyph['id_state_manual']
                glyph['confidence'] = changed_glyph['confidence']
                # Pop the changed glyph from the hash
                changed_glyph_hash.pop(key, None)

    # We do the same for the changed training glyphs
    for glyph in settings['training_glyphs']:

        if not changed_training_hash:
            # No more changed glyphs, so break
            break
        else:
            # There are still glyphs to update
            key = glyph['id']
            # Grab the changed glyph
            if key in changed_training_hash:
                changed_glyph = changed_training_hash[key]
                # Update the Glyph proper
                glyph['class_name'] = changed_glyph['class_name']
                glyph['id_state_manual'] = changed_glyph['id_state_manual']
                glyph['confidence'] = changed_glyph['confidence']
                # Pop the changed glyph from the hash
                changed_training_hash.pop(key, None)

    # Clear out the @changed_glyphs from the settings...
    settings['@changed_glyphs'] = []
    settings['@changed_training_glyphs'] = []
    settings['@deleted_glyphs'] = []
    settings['@deleted_training_glyphs'] = []

def remove_deleted_glyphs(settings, inputs):
    """
    Filter out training glyphs that have been deleted or have the class UNCLASSIFIED.
    """
    copy_training= settings['training_glyphs']
    filter_training = [g for g in copy_training if not g['class_name'] == "UNCLASSIFIED"]
    valid_training = [g for g in filter_training if not g['class_name'].startswith("_delete")]
    settings['training_glyphs'] = valid_training

    copy_list = settings['glyphs']
    valid_glyphs = [g for g in copy_list if not g['class_name'].startswith("_delete")]
    settings['glyphs'] = valid_glyphs

def remove_deleted_classes(settings):
    """
    Filter out the class names that have been deleted.
    """
    valid_classes = settings['imported_class_names']
    deleted_classes = settings['@deleted_classes']
    for deleted_name in deleted_classes:
        valid_classes = [c for c in valid_classes if not c == deleted_name]
        valid_classes = [c for c in valid_classes if not c.startswith(deleted_name + ".")]
    settings['imported_class_names'] = valid_classes
    settings['@deleted_classes'] = []

def update_renamed_classes(settings):
    """
    Update the class names if they have been renamed.
    """
    classes = settings['imported_class_names']
    renamed_classes = settings['@renamed_classes']
    updated_classes = []
    added_classes = []
    for c in classes:
        for r in renamed_classes:
            if c == r or c.startswith(r + "."):
                added_classes.append(c)
                updated_classes.append(c.replace(r, renamed_classes[r], 1))
    for c in classes:
        if not c in added_classes:
            updated_classes.append(c)

    settings['imported_class_names'] = updated_classes
    updated_classes = []
    settings['@renamed_classes'] = []
