from rodan.jobs.base import RodanTask
from rodan.jobs.interactive_classifier.interactive_classifier import *

class InteractiveClassifier(RodanTask):
    #############
    # Description
    #############

    name = 'Interactive Classifier'
    author = 'Andrew Fogarty'
    description = 'A GUI for Gamera interactive kNN classification.'
    settings = {'job_queue': 'Python3'}
    enabled = True
    category = 'Gamera - Classification'
    interactive = True
    input_port_types = [
        {
            'name': 'PNG (includes RGB, 1-Bit, and Greyscale) - Preview Image',
            # 'resource_types': ['image/onebit+png', 'image/rgb+png', 'image/greyscale+png'],

            'resource_types': lambda mime: mime.endswith('png'),
            # Possible resource types include:
            #   'resource_types': ['image/rgb+png', 'image/rgba+png', 'image/png', 'image/onebit+png', 'image/greyscale+png', 'image/grey16+png']
            'minimum': 1,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'GameraXML - Training Data',
            'resource_types': ['application/gamera+xml'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'GameraXML - Connected Components',
            'resource_types': ['application/gamera+xml'],
            'minimum': 1,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'GameraXML - Feature Selection',
            'resource_types': ['application/gamera+xml'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
        	'name': 'Plain Text - Class Names',
        	'resource_types': ['text/plain'],
        	'minimum': 0,
        	'maximum': 1,
        	'is_list': False
        }
    ]
    output_port_types = [
        {
            'name': 'GameraXML - Training Data',
            'resource_types': ['application/gamera+xml'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'GameraXML - Classified Glyphs',
            'resource_types': ['application/gamera+xml'],
            'minimum': 1,
            'maximum': 1,
            'is_list': False
        },
        {
            'name': 'Plain Text - Class Names',
            'resource_types': ['text/plain'],
            'minimum': 0,
            'maximum': 1,
            'is_list': False
        }
    ]


    ##################
    # Required Methods
    ##################

    def my_error_information(self, exc, traceback):
        pass

    def get_my_interface(self, inputs, settings):
        staffless_image_path = inputs['PNG (includes RGB, 1-Bit, and Greyscale) - Preview Image'][0][
            'resource_path']
        # We need to figure out the best way to include the data in the template

        data = {
            'glyphs': settings['glyphs_json'],
            'image_path': media_file_path_to_public_url(
                staffless_image_path),
            'class_names': settings['class_names_json'],
            'training_glyphs': settings['training_json']
        }

        return 'interfaces/interactive_classifier.html', data

    def run_my_task(self, inputs, settings, outputs):
        # Initialize a gamera classifier
        classifier_path = inputs['GameraXML - Connected Components'][0][
            'resource_path']
        if 'GameraXML - Feature Selection' in inputs:
            features = inputs['GameraXML - Feature Selection'][0][
                'resource_path']
        else:
            features = None

        # Set the initial state
        if '@state' not in settings:
            settings['@state'] = ClassifierStateEnum.IMPORT_XML
            settings['glyphs'] = []

        # Execute import state, classifying state, or output state
        if settings['@state'] == ClassifierStateEnum.IMPORT_XML:
            # IMPORT_XML Stage

            # Handle importing the optional training classifier
            if 'GameraXML - Training Data' in inputs:
                classifier_glyphs = GameraXML(inputs['GameraXML - Training Data'][0]['resource_path']).get_glyphs()
                # Discard glyphs that were not classified manually
                classifier_glyphs = [c for c in classifier_glyphs if c['id_state_manual'] == True]
                classifier_glyphs = [c for c in classifier_glyphs if c['class_name'] != "UNCLASSIFIED" and c['class_name'] != "_delete"]

                for c in classifier_glyphs:
                    c['is_training'] = True
            else:
                classifier_glyphs = []


            # Handle importing optional class names from text file
            if 'Plain Text - Class Names' in inputs:
                class_set = set()
                classes_path = inputs['Plain Text - Class Names'][0]['resource_path']
                with open(classes_path) as f:
                    for line in f:
                        class_set.add(line.strip())
            else:
                class_set = set()

            settings['imported_class_names'] = list(class_set)
            settings['training_glyphs'] = classifier_glyphs
            settings['glyphs'] = GameraXML(classifier_path).get_glyphs()
            settings['@state'] = ClassifierStateEnum.CLASSIFYING

            # Run a first classification if training data in input port
            if 'GameraXML - Training Data' in inputs:
                run_correction_stage(settings['glyphs'],
                                     settings['training_glyphs'],
                                     features)

            serialize_data(settings)

            return self.WAITING_FOR_INPUT()

        if settings['@state'] == ClassifierStateEnum.CLASSIFYING:
            # CLASSIFYING STAGE

            # Update any changed glyphs
            add_grouped_glyphs(settings)
            update_changed_glyphs(settings)
            remove_deleted_glyphs(settings, inputs)

            # Update any changed class names
            remove_deleted_classes(settings)
            update_renamed_classes(settings)

            # Takes out _group._parts glyphs and split glyphs TODO: save split glyphs for automatic splitting
            filter_parts(settings)

            # Automatically classify the glyphs
            run_correction_stage(settings['glyphs'],
                                 settings['training_glyphs'],
                                 features)

            # Filter any remaining parts
            filter_parts(settings)

            serialize_data(settings)
            return self.WAITING_FOR_INPUT()

        # Automatic grouping and reclassifying
        elif settings['@state'] == ClassifierStateEnum.GROUP_AND_CLASSIFY:
            # GROUP AND CLASSIFY STAGE

            # Update any changed glyphs
            add_grouped_glyphs(settings)
            update_changed_glyphs(settings)
            remove_deleted_glyphs(settings, inputs)

            # Update any changed class names
            remove_deleted_classes(settings)
            update_renamed_classes(settings)

            # Takes out _group._parts glyphs
            filter_parts(settings)
            # grouping and reclassifying
            group_and_correct(settings['glyphs'],
                              settings['@user_options'],
                              settings['training_glyphs'],
                              features)
            filter_parts(settings)
            serialize_data(settings)
            return self.WAITING_FOR_INPUT()

        # Save all changes
        elif settings['@state'] == ClassifierStateEnum.SAVE:
            # Update any changed glyphs
            add_grouped_glyphs(settings)
            update_changed_glyphs(settings)
            remove_deleted_glyphs(settings, inputs)

            # Update any changed class names
            remove_deleted_classes(settings)
            update_renamed_classes(settings)

            # Takes out _group._parts glyphs and split glyphs
            filter_parts(settings)
            serialize_data(settings)
            return self.WAITING_FOR_INPUT()

        else:
            # EXPORT_XML STAGE

            # Takes out _group._parts glyphs
            filter_parts(settings)

            # Update changed glyphs
            add_grouped_glyphs(settings)
            update_changed_glyphs(settings)
            remove_deleted_glyphs(settings, inputs)

            # Update any changed class names
            remove_deleted_classes(settings)
            update_renamed_classes(settings)

            cknn = prepare_classifier(settings['training_glyphs'], settings['glyphs'], features)

            filter_parts(settings)
            serialize_data(settings)

            # No more corrections are required.  We can now output the data
            run_output_stage(cknn, settings['glyphs'], inputs, outputs, settings['class_names'])
            # Remove the cached JSON from the settings
            settings['glyphs_json'] = None
            settings['class_names_json'] = None

    # Grouping the glyphs manually
    def manual_group(self, glyphs, settings, class_name):
        gamera_glyphs=[]

        # Finding the glyphs that match the incoming ids
        # TODO: this should be more efficient
        for glyph_c in glyphs:
            glyph={}
            for g in settings['glyphs']:
                if glyph_c['id']==g['id']:
                    glyph = g

            # No glyph with this id exists
            # This means its a split glyph
            # A new glyph needs to be created temporarily
            if glyph == {} :
                glyph = GameraGlyph(
                        gid = glyph_c["id"],
                        class_name = glyph_c['class_name'],
                        rle_image = glyph_c['rle_image'],
                        ncols = glyph_c['ncols'],
                        nrows = glyph_c['nrows'],
                        ulx = glyph_c['ulx'],
                        uly = glyph_c['uly'],
                        id_state_manual = glyph_c['id_state_manual'],
                        confidence = glyph_c['confidence']
                        ).to_dict()

            gamera_glyph = RunLengthImage(
            glyph['ulx'],
            glyph['uly'],
            glyph['ncols'],
            glyph['nrows'],
            glyph['image']
            ).get_gamera_image()

            gamera_glyphs.append(gamera_glyph)

        # creating the new grouped glyph image
        grouped = image_utilities.union_images(gamera_glyphs)

        # turning the grouped image into a new glyph
        new_glyph = GameraGlyph(
            class_name = class_name,
            rle_image = grouped.to_rle(),
            ncols = grouped.ncols,
            nrows = grouped.nrows,
            ulx = grouped.ul.x,
            uly = grouped.ul.y,
            id_state_manual = True,
            confidence = 1
            ).to_dict()

        # turning the new glyph into a dictionary that can be returned
        g = {
            'class_name': class_name,
            'id': new_glyph['id'],
            'image': new_glyph['image_b64'],
            'rle_image': new_glyph['image'],
            'ncols': new_glyph['ncols'],
            'nrows': new_glyph['nrows'],
            'ulx': new_glyph['ulx'],
            'uly': new_glyph['uly'],
            'id_state_manual': new_glyph['id_state_manual'],
            'confidence': new_glyph['confidence']
            }

        return g

    def manual_split(self, glyph_to_split, split_type, settings):
        import segmentation
        # Finding the glyphs that match the incoming ids
        glyph={}
        for g in settings['glyphs']:
            if(glyph_to_split['id']==g['id']):
                glyph = g

        # No glyph matches the id so the glyph that is being split is also a split glyph
        # A new glyph must be created temporarily so it can be split again
        if glyph == {}:
            glyph = GameraGlyph(
                    gid = glyph_to_split["id"],
                    class_name = glyph_to_split['class_name'],
                    rle_image = glyph_to_split['rle_image'],
                    ncols = glyph_to_split['ncols'],
                    nrows = glyph_to_split['nrows'],
                    ulx = glyph_to_split['ulx'],
                    uly = glyph_to_split['uly'],
                    id_state_manual = glyph_to_split['id_state_manual'],
                    confidence = glyph_to_split['confidence']
                    ).to_dict()
        # Getting the image of the glyph
        gamera_glyph=RunLengthImage(
            glyph['ulx'],
            glyph['uly'],
            glyph['ncols'],
            glyph['nrows'],
            glyph['image'],
            ).get_gamera_image()

        # Splitting the glyph into numerous image segments
        splits = getattr(segmentation, split_type).__call__(gamera_glyph)

        # Turning the images into a glyph
        glyphs = []
        for split in splits:
            new_glyph = GameraGlyph(
                class_name = "UNCLASSIFIED",
                rle_image = split.to_rle(),
                ncols = split.ncols,
                nrows = split.nrows,
                ulx = split.ul.x,
                uly = split.ul.y,
                id_state_manual = False,
                confidence = 0
                ).to_dict()
            # Transforming the glyph into a dictionary so it can be returned
            g={
                'class_name': "UNCLASSIFIED",
                'id': new_glyph['id'],
                'image': new_glyph['image_b64'],
                'rle_image': new_glyph['image'],
                'ncols': new_glyph['ncols'],
                'nrows': new_glyph['nrows'],
                'ulx': new_glyph['ulx'],
                'uly': new_glyph['uly'],
                'id_state_manual': new_glyph['id_state_manual'],
                'confidence': new_glyph['confidence']
                }

            glyphs.append(g)

        return glyphs

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'complete' in user_input:
            # We are complete.  Advance to the final stage
            return {
                '@state': ClassifierStateEnum.EXPORT_XML,
                '@changed_glyphs': user_input['glyphs'],
                '@grouped_glyphs': user_input['grouped_glyphs'],
                '@changed_training_glyphs': user_input['changed_training_glyphs'],
                '@deleted_glyphs': user_input['deleted_glyphs'],
                '@deleted_training_glyphs': user_input['deleted_training_glyphs'],
                '@deleted_classes': user_input['deleted_classes'],
                '@renamed_classes': user_input['renamed_classes']
            }

        # If the user wants to group, group the glyphs and return the new glyph
        elif 'group' in user_input:
            new_glyph = self.manual_group(user_input['glyphs'], settings, user_input['class_name'])

            data = {
            'manual': True,
            'glyph': new_glyph
            }
            return data

        elif 'split' in user_input:
            glyphs = self.manual_split(user_input['glyph'], user_input['split_type'], settings)
            data = {
            'manual': True,
            'glyphs' : glyphs
            }

            return data

        elif 'auto_group' in user_input:
            return{
            '@state': ClassifierStateEnum.GROUP_AND_CLASSIFY,
            '@user_options': user_input['user_options'],
            '@changed_glyphs': user_input['glyphs'],
            '@grouped_glyphs': user_input['grouped_glyphs'],
            '@changed_training_glyphs': user_input['changed_training_glyphs'],
            '@deleted_glyphs': user_input['deleted_glyphs'],
            '@deleted_training_glyphs': user_input['deleted_training_glyphs'],
            '@deleted_classes': user_input['deleted_classes'],
            '@renamed_classes': user_input['renamed_classes']
            }

        elif 'delete' in user_input:
            glyphs = user_input['glyphs']

            for g in glyphs:
                g['class_name'] = "_delete"

            data = {
            'manual': True,
            'glyphs': glyphs
            }
            return data

        elif 'save' in user_input:
            return {
                '@state': ClassifierStateEnum.SAVE,
                '@changed_glyphs': user_input['glyphs'],
                '@grouped_glyphs': user_input['grouped_glyphs'],
                '@changed_training_glyphs': user_input['changed_training_glyphs'],
                '@deleted_glyphs': user_input['deleted_glyphs'],
                '@deleted_training_glyphs': user_input['deleted_training_glyphs'],
                '@deleted_classes': user_input['deleted_classes'],
                '@renamed_classes': user_input['renamed_classes']
            }

        elif 'undo' in user_input:
            return {
                '@state': ClassifierStateEnum.IMPORT_XML
            }

        else:
            # We are not complete.  Run another correction stage
            changed_glyphs = user_input['glyphs']
            grouped_glyphs = user_input['grouped_glyphs']
            return {
                '@changed_glyphs': changed_glyphs,
                '@grouped_glyphs': grouped_glyphs,
                '@changed_training_glyphs': user_input['changed_training_glyphs'],
                '@deleted_glyphs': user_input['deleted_glyphs'],
                '@deleted_training_glyphs': user_input['deleted_training_glyphs'],
                '@deleted_classes': user_input['deleted_classes'],
                '@renamed_classes': user_input['renamed_classes']
            }
