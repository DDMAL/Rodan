# ================================================================
# MEI2couchdb.py
#
# Usage: python MEI2couchdb directory shortest_gram longest_gram dotext
# where directory is the path to the directory containing MEI files to munge in to the couch
#       shortest_gram and longest_gram are integers in the range 2--10 defining which dbs to add to
#       dotext is 0 if you don't want to process text
# 
# Given a directory containing MEI files, this script iterates through all the MEI files
# and saves a new CouchDB document for each location (bounding box) on the page that we might want to 
# highlight in our web application. We consider all pitch sequences 2--10 notes long. Pitch
# sequences of different lengths are stored in separate CouchDB databases. Originally we were
# storing one document per n-gram and then adding to a growing array of locations (box coordinates)
# as instances of the same pitch sequence were found. To allow for page range filtering (and improved data access), we 
# modified our organization to store a separate doocument for each location. This means that
# several documents can have the same pitch sequence, but with different locations. If a pitch sequence 
# spans two systems, two seperate bounding boxes are stored in the same document.
#
# Throughout this script, ulx and uly stand for upper left x and y coordinates respectively and lrx and lry stand for lower right coordinates. 
# These values define the pixels on the original page image that should be highlighted for a given item (sequence of neumes, line of text, etc.)
#
# Author: Jessica Thompson
# Last modified June 2011
#
# ================================================================
import pymei
import sys
import os
import solr
import uuid
import copy
from math import *
from music21.pitch import convertStepToPs
from music21.interval import convertSemitoneToSpecifierGeneric
#import time
# from pymei.Import import convert
from pymei import XmlImport

import logging

logging.basicConfig(filename='errors.log', format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
lg = logging.getLogger('meisearch')
lg.setLevel(logging.DEBUG)


import pdb

systemcache = {}
idcache = {}

#*****************************FUNCTIONS*******************************
def findbyID(llist, mid, meifile):
    """ Returns the object in llist that has the given id. Used for finding zone.
        pymei function get_by_facs can be used instead, but this one is faster.
    """
    if mid in idcache:
        return idcache[mid]
    else:
        # idcache[mid] = llist[(i for i, obj in enumerate(llist) if obj.id == mid).next()]
        idcache[mid] = meifile.getElementById(mid)
        return idcache[mid]

def getLocation(seq, meifile, zones):
    """ Given a sequence of notes and the corresponding MEI Document, calculates and returns the json formatted list of 
        locations (box coordinates) to be stored for an instance of a pitch sequence in our CouchDB. 
        If the sequence is contained in a single system, only one location will be stored. If the sequence
        spans two systems, a list of two locations will be stored.
    """
    ulys = []
    lrys = []
    twosystems=0
    endofsystem = len(seq)-1
    if seq[0].getId() not in systemcache:
        systemcache[seq[0].getId()] = meifile.lookBack(seq[0], "sb")
        # systemcache[seq[0]] = meifile.get_system(seq[0])
    if seq[endofsystem].getId() not in systemcache:
        systemcache[seq[endofsystem].getId()] = meifile.lookBack(seq[endofsystem], "sb")
        # systemcache[seq[endofsystem]] = meifile.get_system(seq[endofsystem])

    if systemcache[seq[0].getId()] != systemcache[seq[endofsystem].getId()]: #then the sequence spans two systems and we must store two seperate locations to highlight
        twosystems=1
        for i in range(1,len(seq)):
            if seq[i-1].getId() not in systemcache:
                systemcache[seq[i-1].getId()] = meifile.lookBack(seq[i-1], "sb")
            if seq[i] not in systemcache:
                systemcache[seq[i].getId()] = meifile.lookBack(seq[i], "sb")

            # find the last note on the first system and the first note on the second system
            if systemcache[seq[i-1].getId()] != systemcache[seq[i].getId()]: 
                endofsystem = i # this will be the index of the first note on second system
                # ulx1 = int(meifile.get_by_facs(seq[0].parent.parent.facs)[0].ulx)
                # lrx1 = int(meifile.get_by_facs(seq[i-1].parent.parent.facs)[0].lrx)
                # ulx2 = int(meifile.get_by_facs(seq[i].parent.parent.facs)[0].ulx)
                # lrx2 = int(meifile.get_by_facs(seq[-1].parent.parent.facs)[0].lrx)
                ulx1 =  int(findbyID(zones, seq[0].parent.parent.getAttribute("facs").value, meifile).getAttribute("ulx").value)
                lrx1 =  int(findbyID(zones, seq[i-1].parent.parent.getAttribute("facs").value, meifile).getAttribute("lrx").value)
                ulx2 =  int(findbyID(zones, seq[i].parent.parent.getAttribute("facs").value, meifile).getAttribute("ulx").value)
                lrx2 =  int(findbyID(zones, seq[-1].parent.parent.getAttribute("facs").value, meifile).getAttribute("lrx").value)
    else: # the sequence is contained in one system and only one box needs to be highlighted
        ulx =  int(findbyID(zones, seq[0].parent.parent.getAttribute("facs").value, meifile).getAttribute("ulx").value)
        lrx =  int(findbyID(zones, seq[-1].parent.parent.getAttribute("facs").value, meifile).getAttribute("lrx").value)
        # ulx = int(meifile.get_by_facs(seq[0].parent.parent.facs)[0].ulx)
        # lrx = int(meifile.get_by_facs(seq[-1].parent.parent.facs)[0].lrx)
    
    for note in seq:
        ulys.append(int(findbyID(zones, note.parent.parent.getAttribute("facs").value, meifile).getAttribute("uly").value))
        lrys.append(int(findbyID(zones, note.parent.parent.getAttribute("facs").value, meifile).getAttribute("lry").value))

    if twosystems:
        uly1 = min(ulys[:endofsystem])
        uly2 = min(ulys[endofsystem:])
        lry1 = max(lrys[:endofsystem])
        lry2 = max(lrys[endofsystem:])
        return [{"ulx": int(ulx1) ,"uly": int(uly1), "height": abs(uly1 - lry1), "width": abs(ulx1 - lrx1)},{"ulx": int(ulx2) ,"uly": int(uly2), "height": abs(uly2 - lry2), "width": abs(ulx2 - lrx2)}]      
    else:
        uly =  min(ulys)
        lry = max(lrys)
        return [{"ulx": int(ulx) ,"uly": int(uly), "height": abs(uly - lry), "width": abs(ulx - lrx)}]

def getNeumes(seq, counter):
    """ Given a list of MEI note elements, return a string of the names of the neumes seperated by underscores.
    """
    neumes = str(seq[0].parent.parent.getAttribute('name').value)
    for k in range(1, counter):
        if seq[k].parent.parent.id != seq[k-1].parent.parent.id:
            neumes = neumes + '_' + str(seq[k].parent.parent.getAttribute('name').value)
    return neumes

def getPitchNames(seq):
    """ Given a list of MEI note elements, return the tuple [pnames, midipitch] where pnames is a string of the 
    pitch names of the given notes (no octave information) and midipitch is a list of the midi values for those 
    same pitches. Music21's convertStepToPs function is used to get midi pitch values.
    """
    pnames = []
    midipitch = []
    for note in seq:
        pnames.append(note.getAttribute("pname").value[0]) # a string of pitch names e.g. 'gbd'
        midipitch.append(int(convertStepToPs(str(note.getAttribute("pname").value[0]), int(note.getAttribute("oct").value))))
    return [str("".join(pnames)), midipitch]
    
def getIntervals(semitones, pnames):
    """ Get quality (major, minor, etc.) invariant interval name and direction for example, an ascending 
        major second and an ascending minor second will both be encoded as 'u2'. the only tritone to occur is between 
        b and f, in the context of this application we will assume that the b will always be sung as b 
        flat. So a tritone found in the music is never encoded as a tritone in our database; it will instead always be 
        represented as either a fifth or a fourth, depending on inversion. If the one wishes to search for tritones, 
        they may use the semitones field.
    """
    intervals = []
    for z,interval in enumerate(semitones):
        if interval == 0:
            intervals.append('r')
        else:
            if interval > 0:
                direction = 'u'
            else:
                direction = 'd'
            if interval == 6:
                if pnames[z] == 'b':
                    size = 5
                else:
                    size = 4
            elif interval == -6:
                if pnames[z] == 'b':
                    size = 4
                else:
                    size = 5
            else: 
                size = abs(int(convertSemitoneToSpecifierGeneric(interval)[1]))

            intervals.append("{0}{1}".format(direction, str(size)))

    return "_".join(intervals)

def getContour(semitones):
    """ Given a list of integers defining the size and direction of a series of musical intervals in semitones, 
        this function encodes the contour of the melody with Parsons code for musical contour where u=up, d=down, r=repeat.
    """
    contour = ''
    for p in semitones:
       if p == 0:
           contour = contour + 'r' # repeated 
       elif p > 0:
           contour = contour + 'u' # up
       elif p < 0:
           contour = contour + 'd' # down
    return contour
        
def storeText(lines, zones, textdb):
    """ For each line of text in the list "lines", this function gets the corresponding box coordinates and saves the 
    line as a doc in the "text" database.
    """
    for line in lines:
        text = line.value
        facs = str(line.getAttribute('facs').value)
        zone = findbyID(zones, facs)
        ulx = int(zone.ulx)
        uly = int(zone.uly)
        lrx = int(zone.lrx)
        lry = int(zone.lry)
        textdb.save({'pagen': pagen, 'text': text, 'location': {"ulx": ulx ,"uly": uly, "height": abs(uly - lry), "width": abs(ulx - lrx)}})
    return 1


def processMeiFile(ffile, solr_server, longest_gram, shortest_gram):
    solrconn = solr.SolrConnection("%s/liber-search" % solr_server)
    print '\nProcessing ' + str(ffile) + '...'
    try:
        meifile = XmlImport.documentFromFile(str(ffile))
    except Exception, e:
        print "E: ",e
        lg.debug("Could not process file {0}. Threw exception: {1}".format(ffile, e))
        print "Whoops!"

    page = meifile.getElementsByName('page')
    pagen = int(page[0].getAttribute('n').value)

    notes = meifile.getElementsByName('note')
    zones = meifile.getElementsByName('zone')
    nnotes = len(notes) # number of notes in file
    #print str(nnotes) + 'notes\n'
    
    # get and store text
    # if dotext:
        # lines = meifile.search('l')
        # storeText(lines, zones, textdb)
    
    #Set these to control which databases you access
    #shortest_gram = 2
    #longest_gram = 10
    mydocs = []

    for i in range(shortest_gram,longest_gram+1):
        # dbname = 'notegrams_'+str(i)
        # db = couch[dbname] #existing db
 
        # uncomment the lines below if you want to process only files that aren't already in the couch
        # only proceed with the rest of the script if a query for pagen returns 0 hits
        # map_fun = '''function(doc) {
        #            emit(doc.pagen, null)
        #        }'''
        # rows = db.query(map_fun, key=pagen)
        # lrows = len(rows)
        lrows = 0 #comment out this line if you want to process files that aren't already in the couch
        if lrows == 0:
          #*******************TEST************************
          # for note in notes:
          #             s = meifile.get_system(note)
          #             neume = str(note.parent.parent.attribute_by_name('name').value)
          #             print 'pitch: '+ str(note.pitch[0])+ ' neume: ' + neume + " system: " +str(s)
          #***********************************************

            print "Processing pitch sequences... "
            # for j,note in enumerate(notes):
            for j in range(0,nnotes-i):
                seq = notes[j:j+i]
                # get box coordinates of sequence
                # if ffile == "/Volumes/Copland/Users/ahankins/Documents/code/testing/Liber_Usualis_Final_Output/0012/0012_corr.mei":
                #     pdb.set_trace()

                location = getLocation(seq, meifile, zones)
                #print 'location: ' + str(location)

                # get neumes
                neumes = getNeumes(seq, i)

        #         # get pitch names
                [pnames, midipitch] = getPitchNames(seq)

        #         # get semitones
        #         # calculate difference between each adjacent entry in midipitch list
                semitones = [m-n for n, m in zip(midipitch[:-1], midipitch[1:])]
                str_semitones = str(semitones)[1:-1] # string will be stored instead of array for easy searching
                str_semitones = str_semitones.replace(', ', '_')

        #         # get quality invariant interval name and direction
        #         # for example, an ascending major second and an ascending minor second will both be encoded as 'u2' 
        #         # the only tritone to occur would be between b and f, in the context of this application we will assume that the be will always be sung as b flat
        #         # thus the tritone is never encoded as such and will always be represented as either a fifth or a fourth, depending on inversion
                intervals = getIntervals(semitones, pnames)

        #         # get contour - encode with Parsons code for musical contour
                contour = getContour(semitones)
        #         # save new document
                mydocs.append({'id': str(uuid.uuid4()), 'pagen': int(pagen), 'pnames': pnames, 'neumes': neumes, 'contour': contour, 'semitones': str_semitones, 'intervals': intervals, 'location': str(location)})
        else:
          print 'page ' + str(pagen) +  ' already processed\n'
        # solrconn.add_many(mydocs)
    solrconn.commit()
    systemcache.clear()
    idcache.clear()
