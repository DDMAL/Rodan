from pymei import MeiElement, XmlImport, XmlExport

class ModifyDocument:
    
    def __init__(self, filename):
        self.mei = XmlImport.read(filename)
        self.filename = filename

    def write_doc(self, **kwargs):
        '''
        Write the modified MEI document out to a file,
        clobbering the input file, if no filename parameter
        is provided.
        '''

        if 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = self.filename

        XmlExport.write(self.mei, filename)

    def insert_punctum(self, before_id, pname, oct, dot_form, ulx, uly, lrx, lry):
        '''
        Insert a punctum before the given element. There is one case where
        there is no element to insert before, when there is no subsequent staff.
        In this case, the element is inserted at the end of the last system.
        Also sets the bounding box information of the new punctum.
        '''

        # create the punctum
        punctum = MeiElement("neume")
        punctum.addAttribute("name", "punctum")
        nc = MeiElement("nc")
        note = MeiElement("note")
        note.addAttribute("pname", pname)
        note.addAttribute("oct", oct)

        # add ornamentation
        if dot_form is not None:
            dot = MeiElement("dot")
            dot.addAttribute("form", str(dot_form))
            note.addChild(dot)

        punctum.addChild(nc)
        nc.addChild(note)

        # create bounding box
        self.update_or_add_zone(punctum, ulx, uly, lrx, lry)

        # perform the insertion
        if before_id is None:
            # get last layer
            layers = self.mei.getElementsByName("layer")
            if len(layers):
                layers[-1].addChild(punctum)
        else:
            before = self.mei.getElementById(before_id)

            # get layer element
            parent = before.getParent()

            if parent and before:
                parent.addChildBefore(before, punctum)

        # get the generated ID for the client
        result = {"id": punctum.getId()}
        return result

    def move_neume(self, id, before_id, pitch_info, ulx, uly, lrx, lry):
        '''
        Move the neume in the document. If the neume moves vertically
        perform a pitch shift. Update bounding box information.
        If the neume moves position relative to other elements, re-insert
        the neume before a given MeiElement.
        '''
        neume = self.mei.getElementById(id)

        # if the neume moves vertically, perform a pitch shift
        if pitch_info is not None:
            notes = neume.getDescendantsByName("note")
            if len(notes):
                for n, pinfo in zip(notes, pitch_info):
                    n.addAttribute("pname", str(pinfo["pname"]))
                    n.addAttribute("oct", str(pinfo["oct"]))

        # update the position of the neume in the document
        # first, remove the neume
        parent = neume.getParent()
        parent.removeChild(neume)

        # re-insert in the correct position
        if before_id is None:
            # get last layer
            layers = self.mei.getElementsByName("layer")
            if len(layers):
                layers[-1].addChild(neume)
        else:
            before = self.mei.getElementById(before_id)

            # get layer element
            parent = before.getParent()

            if parent and before:
                parent.addChildBefore(before, neume)

        self.update_or_add_zone(neume, ulx, uly, lrx, lry)

    def delete_neume(self, ids):
        for id in ids:
            element = self.mei.getElementById(id)
            
            # remove the bounding box attached to this element
            self.remove_zone(element)
            
            # remove the element
            element.getParent().removeChild(element)

    def neumify(self, ids, name, ulx, uly, lrx, lry):
        '''
        Neumify a group of neumes (with provided ids)
        and give it the given neume name. Also update
        bounding box information.
        '''
        
        # create the new neume from the provided notes
        new_neume = MeiElement("neume")
        new_neume.addAttribute("name", name)
        nc = MeiElement("nc")
        
        for id in ids:
            ref_neume = self.mei.getElementById(id)
            if ref_neume:
                # get underlying notes
                notes = ref_neume.getDescendantsByName("note")
                for n in notes:
                    nc.addChild(n)

        new_neume.addChild(nc)

        # insert the neume
        before = self.mei.getElementById(ids[0])
        parent = before.getParent()

        if before and parent:
            parent.addChildBefore(before, new_neume)

        # delete the old neumes
        for id in ids:
            old_neume = self.mei.getElementById(id)
            if old_neume:
                # remove bounding box information
                self.remove_zone(old_neume)
                
                # now remove the neume
                old_neume.getParent().removeChild(old_neume)

        # add the bounding box information for the new neume
        self.update_or_add_zone(new_neume, ulx, uly, lrx, lry)

        result = {"id": new_neume.getId()}
        return result

    def ungroup(self, ids, bboxes):
        '''
        Ungroup a neume with the provided ids into puncta.
        Create bounding box information for each punctum.
        '''

        newids = []
        for id, bbox in zip(ids, bboxes):
            ref_neume = self.mei.getElementById(id)
            parent = ref_neume.getParent()

            # get underlying notes
            notes = ref_neume.getDescendantsByName("note")
            nids = []
            for n, bb in zip(notes, bbox):
                punctum = MeiElement("neume")
                punctum.addAttribute("name", "punctum")
                nc = MeiElement("nc")
                nc.addChild(n)
                punctum.addChild(nc)

                # add generated punctum id to return to client
                nids.append(punctum.getId())

                # add facs data for the punctum
                self.update_or_add_zone(punctum, str(bb["ulx"]), str(bb["uly"]), str(bb["lrx"]), str(bb["lry"]))

                # insert the punctum before the reference neume
                parent.addChildBefore(ref_neume, punctum)

            newids.append(nids)

            # delete the old neume
            neume = self.mei.getElementById(id)
            if neume:
                # remove bounding box information
                self.remove_zone(neume)

                # now remove the neume
                neume.getParent().removeChild(neume)
        
        result = {"nids": newids}
        return result

    def insert_division(self, before_id, type, ulx, uly, lrx, lry):
        '''
        Insert a division before the given element. There is one case
        where there is no element to insert before, when there is no
        subsequent staff. In this case, the element is inserted at the end
        of the last system. Also sets the bounding box information of the new
        division.
        '''

        division = MeiElement("division")
        division.addAttribute("form", type)
        self.update_or_add_zone(division, ulx, uly, lrx, lry)

        before = self.mei.getElementById(before_id)

        # get layer element
        layer = before.getParent()

        if layer and before:
            layer.addChildBefore(before, division)

            if type == "final":
                # if final division, close layer and staff
                staff = layer.getParent()
                section_parent = staff.getParent()

                # create new staff and layer
                new_staff = MeiElement("staff")
                new_layer = MeiElement("layer")
                new_layer.addAttribute("n", "1")
                
                # get elements after "before element" to move
                element_peers = before.getPeers()
                e_ind = list(element_peers).index(before)
                for e in element_peers[e_ind:]:
                    # add element to the new staff/layer
                    new_layer.addChild(e)
                    # remove element from the current staff/layer
                    layer.removeChild(e)

                new_staff.addChild(new_layer)

                # insert new staff into the document
                staves = section_parent.getChildrenByName("staff")
                s_ind = list(staves).index(staff)
                before_staff = None
                if s_ind+1 < len(staves):
                    before_staff = staves[s_ind+1]

                # insert and update staff definitions
                staff_group = self.mei.getElementsByName("staffGrp")
                if len(staff_group):
                    staff_defs = staff_group[0].getChildrenByName("staffDef")
                    if len(staff_defs) == len(staves):
                        for i, sd in enumerate(staff_defs[s_ind+1:]):
                            sd.addAttribute("n", str(s_ind+i+3))
                        staff_def = MeiElement("staffDef")
                        staff_def.addAttribute("n", str(s_ind+2))
                        before_staff_def = None
                        if s_ind+1 < len(staff_defs):
                            before_staff_def = staff_defs[s_ind+1]

                if before_staff_def:
                    staff_group[0].addChildBefore(before_staff_def, staff_def)
                else:
                    staff_group[0].addChild(staff_def)

                # update staff numbers of subsequent staves
                for i, s in enumerate(staves[s_ind+1:]):
                    s.addAttribute("n", str(s_ind+i+3))

                new_staff.addAttribute("n", str(s_ind+2))

                # insert the new staff
                if before_staff:
                    section_parent.addChildBefore(before_staff, new_staff)
                else:
                    section_parent.addChild(staff)
    
        result = {"id": division.getId()}
        return result

    def move_division(self, id, before_id, ulx, uly, lrx, lry):
        '''
        Move a division before the given element. There is no
        element to insert before when there is no subsequent
        staff. In this case, the element is inserted at the end
        of the last system. Also sets the bounding box information
        of the new division placement. All of the complexity here 
        comes from final divisions, where elements have to be shifted.
        '''

        division = self.mei.getElementById(id)
        self.update_or_add_zone(division, ulx, uly, lrx, lry)

        # move the position of the division in the document
        layer = division.getParent()

        final_division = False
        if division.getAttribute("form").getValue() == "final":
            final_division = True

        if final_division:
            # if final division, close layer and staff
            staff = layer.getParent()
            section = staff.getParent()
            staves = section.getChildrenByName("staff")
            s_ind = list(staves).index(staff)

            if s_ind+1 < len(staves):
                next_staff = staves[s_ind+1]
                next_staff_layer = next_staff.getChildrenByName("layer")
                if len(next_staff_layer):
                    # add elements from subsequent staff/layer to this staff/layer
                    next_staff_elements = next_staff_layer[0].getChildren()

                    # remove the next staff/layer from the MEI document
                    section.removeChild(next_staff)

                    for e in next_staff_elements:
                        layer.addChild(e)

        # remove the division from the document
        layer.removeChild(division)
        
        before = self.mei.getElementById(before_id)
        # get layer element
        layer_before = before.getParent()

        if layer_before and before:
            layer_before.addChildBefore(before, division)

            if final_division:
                # if final division, close layer and staff
                staff = layer_before.getParent()
                section = staff.getParent()

                # create new staff and layer
                new_staff = MeiElement("staff")
                new_layer = MeiElement("layer")
                new_layer.addAttribute("n", "1")
                
                # get elements after "before element" to move
                element_peers = before.getPeers()
                e_ind = list(element_peers).index(before)
                for e in element_peers[e_ind:]:
                    # add element to the new staff/layer
                    new_layer.addChild(e)
                    # remove element from the current staff/layer
                    layer_before.removeChild(e)

                new_staff.addChild(new_layer)

                # insert new staff into the document
                staves = section.getChildrenByName("staff")
                s_ind = list(staves).index(staff)
                before_staff = None
                if s_ind+1 < len(staves):
                    before_staff = staves[s_ind+1]

                # update staff numbers of subsequent staves
                for i, s in enumerate(staves[s_ind+1:]):
                    s.addAttribute("n", str(s_ind+i+3))

                new_staff.addAttribute("n", str(s_ind+2))

                # insert the new staff
                if before_staff:
                    section.addChildBefore(before_staff, new_staff)
                else:
                    section.addChild(staff)

    def delete_division(self, ids):
        '''
        Delete a division from the MEI document. Special
        consideration is taken when deleting divisions of form
        "final"
        '''

        for id in ids:
            division = self.mei.getElementById(id)
            self.remove_zone(division)

            if division.getAttribute("form").getValue() == "final":
                layer = division.getParent()
                staff = layer.getParent()
                section = staff.getParent()

                staves = section.getChildrenByName("staff")
                s_ind = list(staves).index(staff)

                # get elements from next staff/layer, if any
                # and move them to the previous staff/layer
                next_layer = staves[s_ind+1].getChildrenByName("layer")
                if len(next_layer):
                    elements = next_layer[0].getChildren()

                    # remove the next staff/layer
                    section.removeChild(staves[s_ind+1])

                    # add these elements to the previous staff/layer
                    for e in elements:
                        layer.addChild(e)

                    # remove the staffDef for the removed layer
                    staff_group = self.mei.getElementsByName("staffGrp")
                    if len(staff_group):
                        staff_defs = staff_group[0].getChildrenByName("staffDef")
                        if len(staff_defs) == len(staves):
                            # renumber subsequent staff defs
                            for i, sd in enumerate(staff_defs[s_ind+2:]):
                                sd.addAttribute("n", str(s_ind+i+2))

                            staff_group[0].removeChild(staff_defs[s_ind+1])

                    # renumber subsequent staves
                    for i, s in enumerate(staves[s_ind+2:]):
                        s.addAttribute("n", str(s_ind+i+2))

            # delete the division
            division.getParent().removeChild(division)

    def add_dot(self, id, form, ulx, uly, lrx, lry):
        '''
        Add a dot ornament to a given element.
        '''

        punctum = self.mei.getElementById(id)
        # check that a punctum element was provided
        if punctum.getName() == "neume" and punctum.getAttribute("name").getValue() == "punctum":
            note = punctum.getDescendantsByName("note")
            if len(note):
                # if a dot does not already exist on the note
                if len(note[0].getChildrenByName("dot")) == 0:
                    dot = MeiElement("dot")
                    dot.addAttribute("form", form)
                    note[0].addChild(dot)

            self.update_or_add_zone(punctum, ulx, uly, lrx, lry)

    def delete_dot(self, id, ulx, uly, lrx, lry):
        '''
        Remove a dot ornament to a given element.
        '''

        punctum = self.mei.getElementById(id)
        # check that a punctum element was provided
        if punctum.getName() == "neume" and punctum.getAttribute("name").getValue() == "punctum":
            note = punctum.getDescendantsByName("note")
            if len(note):
                dot = note[0].getChildrenByName("dot")
                # if a dot exists
                if len(dot) == 1:
                    note[0].removeChild(dot[0])

            self.update_or_add_zone(punctum, ulx, uly, lrx, lry)

    def insert_clef(self, line, shape, pitch_info, before_id, ulx, uly, lrx, lry):
        '''
        Insert a doh or fah clef, with a given bounding box.
        Must also update pitched elements on the staff that
        affected by this clef being inserted.
        '''

        clef = MeiElement("clef")
        clef.addAttribute("shape", shape)
        clef.addAttribute("line", line)

        # perform clef insertion
        before = self.mei.getElementById(before_id)
        parent = before.getParent()

        if parent and before:
            parent.addChildBefore(before, clef)

        self.update_or_add_zone(clef, ulx, uly, lrx, lry)
        self.update_pitched_elements(pitch_info)

        result = {"id": clef.getId()}
        return result

    def move_clef(self, id, line, pitch_info, ulx, uly, lrx, lry):
        '''
        Move a clef on a staff (must not change staff).
        Updates the bounding box information of the clef
        and updates the pitch information (pitch name and
        octave) of all pitched elements on the affected staff.
        '''

        clef = self.mei.getElementById(id)

        # update staff line the clef is on
        clef.addAttribute("line", line)

        self.update_or_add_zone(clef, ulx, uly, lrx, lry)
        self.update_pitched_elements(pitch_info)

    def update_clef_shape(self, id, shape, pitch_info, ulx, uly, lrx, lry):
        '''
        Change the shape of a given clef. Must also update
        bounding box data since the glyphs for c and f clefs
        are different. Must also update pitched elements on the
        affected staff to correspond with the new clef shape.
        '''

        clef = self.mei.getElementById(id)

        # update clef shape
        clef.addAttribute("shape", shape.upper())

        self.update_or_add_zone(clef, ulx, uly, lrx, lry)
        self.update_pitched_elements(pitch_info)

    def delete_clef(self, clef_data):
        '''
        Delete a doh or fah clef.
        Must also update pitched elements on the staff
        that are affected by the deletion of this clef
        element.
        clef_data: [{id, pitch_info}, ...]
        '''

        for c in clef_data:
            clef = self.mei.getElementById(str(c["id"]))
            # remove the clef bounding box
            self.remove_zone(clef)
            # remove the clef
            clef.getParent().removeChild(clef)

            self.update_pitched_elements(c["pitchInfo"])

    def insert_custos(self, pname, oct, before_id, ulx, uly, lrx, lry):
        '''
        Insert a custos. Also add a bounding box
        for this element.
        '''

        # create custos
        custos = MeiElement("custos")
        custos.addAttribute("pname", pname)
        custos.addAttribute("oct", oct)

        # insert the custos
        before = self.mei.getElementById(before_id)

        # get layer element
        parent = before.getParent()

        if parent and before:
            parent.addChildBefore(before, custos)

        # update the bounding box
        self.update_or_add_zone(custos, ulx, uly, lrx, lry)

        result = {"id": custos.getId()}
        return result

    def move_custos(self, id, pname, oct, ulx, uly, lrx, lry):
        '''
        Move the given custos element.
        Also update the bounding box information.
        '''

        custos = self.mei.getElementById(id)
        if pname is not None and oct is not None:
            custos.addAttribute("pname", str(pname))
            custos.addAttribute("oct", str(oct))

        self.update_or_add_zone(custos, ulx, uly, lrx, lry)

    def delete_custos(self, id):
        '''
        Delete a given custos from the document.
        Also remove the element's bounding box information.
        '''

        custos = self.mei.getElementById(id)
        # remove the bounding box data
        self.remove_zone(custos)
        # remove the custos from the document
        custos.getParent().removeChild(custos)

    # HELPER FUNCTIONS
    def update_or_add_zone(self, element, ulx, uly, lrx, lry):
        '''
        Update the bounding box information attached to an element
        '''

        facsid = element.getAttribute("facs")
        if facsid:
            zone = self.mei.getElementById(facsid.getValue())
        else:
            zone = MeiElement("zone")
            element.addAttribute("facs", zone.getId())
            surfaces = self.mei.getElementsByName("surface")
            if len(surfaces):
                surfaces[0].addChild(zone)

        zone.addAttribute("ulx", ulx)
        zone.addAttribute("uly", uly)
        zone.addAttribute("lrx", lrx)
        zone.addAttribute("lry", lry)

    def remove_zone(self, element):
        '''
        Remove the bounding box information of the deleted element
        from the document
        '''

        facs_id = element.getAttribute("facs")
        if facs_id:
            zone = self.mei.getElementById(facs_id.getValue())
            zone.getParent().removeChild(zone)

    def update_pitched_elements(self, pitch_info):
        for ele in pitch_info:
            pitched_ele = self.mei.getElementById(str(ele["id"]))
            if pitched_ele.getName() == "custos":
                pitched_ele.addAttribute("pname", str(ele["noteInfo"]["pname"]))
                pitched_ele.addAttribute("oct", str(ele["noteInfo"]["oct"]))
            elif pitched_ele.getName() == "neume":
                notes = pitched_ele.getDescendantsByName("note")
                for n_info, n in zip(ele["noteInfo"], notes):
                    n.addAttribute("pname", str(n_info["pname"]))
                    n.addAttribute("oct", str(n_info["oct"]))
