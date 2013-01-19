import argparse
import datetime
import os

from pymei import XmlImport, XmlExport, MeiElement
import pymei

class MeiCombiner:
    '''
    Combines mei files created by the barline finding algorithm.
    '''

    def __init__(self, input_mei_paths):
        '''
        PARAMETERS
        ----------
        input_mei_paths {list}: list of mei paths to combine
        '''

        self._input_mei_paths = input_mei_paths
        if len(self._input_mei_paths):
            self._meidoc = pymei.read(self._input_mei_paths[0])
        else:
            self._meidoc = None

    def combine(self):
        if self._meidoc and len(self._input_mei_paths) > 1:
            base_facsimile = self._meidoc.getElementsByName('facsimile')[0]
            base_section = self._meidoc.getElementsByName('section')[0]
            for f in self._input_mei_paths[1:]:
                mei = pymei.read(f)

                # combine surface
                surface = mei.getElementsByName('surface')
                if len(surface):
                    # have to remove the child from the old document in memory
                    # or else pymei segfaults ...
                    surface[0].getParent().removeChild(surface[0])
                    base_facsimile.addChild(surface[0])

                # combine measures
                pb = MeiElement('pb')
                base_section.addChild(pb)

                # get last measure number
                measures = base_section.getChildrenByName('measure')
                last_measure_n = int(measures[-1].getAttribute('n').value)

                new_section = mei.getElementsByName('section')[0]
                music_elements = new_section.getChildren()

                for e in music_elements:
                    if e.getName() == 'measure':
                        last_measure_n += 1
                        e.addAttribute('n', str(last_measure_n))

                    base_section.addChild(e)

                # remove all musical elements from the old document or else pymei segfaults
                new_section.getParent().deleteAllChildren()

            self._add_revision()

    def _add_revision(self):
        # add a revision
        today = datetime.date.today().isoformat()
        change = MeiElement('change')

        # get last change number
        changes = self._meidoc.getElementsByName('change')
        if len(changes):
            last_change = int(changes[-1].getAttribute('n').value)

        change.addAttribute('n', str(last_change+1))
        resp_stmt = MeiElement('respStmt')
        corp_name = MeiElement('corpName')
        corp_name.setValue('Distributed Digital Music Archives and Libraries Lab (DDMAL)')
        change_desc = MeiElement('changeDesc')
        ref = MeiElement('ref')
        p = MeiElement('p')
        application = self._meidoc.getElementsByName('application')
        app_name = 'RODAN/barlineFinder'
        if len(application):
            ref.addAttribute('target', '#'+application[0].getId())
            ref.setValue(app_name)
            ref.setTail('.')
            p.addChild(ref)

        p.setValue('Combining individual page MEIs using ')
        date = MeiElement('date')
        date.setValue(today)

        revision_descs = self._meidoc.getElementsByName('revisionDesc')
        if len(revision_descs):
            revision_descs[0].addChild(change)
            change.addChild(resp_stmt)
            resp_stmt.addChild(corp_name)
            change.addChild(change_desc)
            change_desc.addChild(p)
            change.addChild(date)

    def write_mei(self, output_path):
        if self._meidoc:
            pymei.write(self._meidoc, output_path)

    def get_mei(self):
        return self._meidoc
