'''
UBC Eye Movement Data Analysys Toolkit
Generic Participant Class
Created on 2011-09-25

@author: skardan
'''
import os, string
from data_structures import *
import params



class Participant():
    def __init__(self, pid, eventfile, datafile, fixfile, aoifile = None, prune_length= None):

        raise Exception("you must override this and read and process the datafile and create the scenes and segments here!")
        self.id = pid

    def invalid_segments(self):
        return map(lambda y: y.segid, filter(lambda x: not x.is_valid, self.segments))

    def valid_segments(self):
        return map(lambda y: y.segid, filter(lambda x: x.is_valid, self.segments))

#    def export_features(self, featurelist=None, aoifeaturelist=None, aoifeaturelabels = None,
#                        id_prefix = False, require_valid = True):
#        data = []
#        featnames = []
#        if id_prefix:
#            featnames.append('part_id')
#        featnames.append('seg_id')
#        first = True
#        for t in self.segments:
#            if not t.is_valid and require_valid:
#                continue
#            seg_feats = []
#            if id_prefix:
#                seg_feats.append(self.id)
#            seg_feats.append(t.segid)
#            fnames, fvals = t.get_features(featurelist = featurelist,
#                                           aoifeaturelist = aoifeaturelist, 
#                                           aoifeaturelabels = aoifeaturelabels)
#            if first: featnames += fnames
#            seg_feats += fvals
#            first = False
#            data.append(seg_feats)            
#
#        return featnames, data

    def export_features(self, featurelist=None, aoifeaturelist=None, aoifeaturelabels = None,
                        id_prefix = False, require_valid = True):
        data = []
        featnames = []
        if id_prefix:
            featnames.append('Part_id')
        featnames.append('Sc_id')
        first = True
        for sc in self.scenes:
            if not sc.is_valid and require_valid:
                print "User %s:Scene %s dropped because of 'require_valid'" %(self.id,sc.scid)
                continue
            sc_feats = []
            if id_prefix:
                sc_feats.append(self.id)
            sc_feats.append(sc.scid)
            fnames, fvals = sc.get_features(featurelist = featurelist,
                                           aoifeaturelist = aoifeaturelist, 
                                           aoifeaturelabels = aoifeaturelabels)
            if first: featnames += fnames
            sc_feats += fvals
            first = False
            data.append(sc_feats)            

        return featnames, data

    def export_features_tsv(self, featurelist=None, aoifeaturelist=None, id_prefix = False, 
                            require_valid = True):
        featnames, data  = self.export_features(featurelist, aoifeaturelist = aoifeaturelist, 
                                                id_prefix = id_prefix, require_valid = require_valid)

        ret = string.join(featnames, '\t') + '\n'
        for t in data:
            ret += (string.join(map(str, t), '\t') + '\n')
        return ret
    
    def print_(self):       
        def format_list(list,leng=None):
            out=''
            if leng == None:
                maxlen=0
                for j in list:
                    st = repr(j)
                    if len(st) > maxlen:
                        maxlen = len(st)
                for j in list:
                    out+= repr(j).rjust(maxlen+1)
                return out,maxlen+1
            else:
                for j in list:
                    st = repr(j)
                    out+= st.rjust(leng)
                return out,leng
 
        print  "PID:",self.id
        
        for seg in self.segments:
            featnames = []
            if not seg.is_valid:
                continue
            seg_feats = []
            featnames.append('seg_id')
            seg_feats.append(seg.segid)
            fnames, fvals = seg.get_features()
            featnames += fnames
            seg_feats += fvals
            o,l= format_list(featnames)
            print o
            print format_list(seg_feats,l)
            
        for sc in self.scenes:
            featnames = []
            if not sc.is_valid:
                continue
            sc_feats = []
            featnames.append('sc_id')
            sc_feats.append(sc.scid)
            fnames, fvals = sc.get_features()
            featnames += fnames
            sc_feats += fvals
            o,l= format_list(featnames)
            print o
            print format_list(sc_feats,l)
    

def read_participants(segsdir, datadir, prune_length = None, aoifile = None):
    participants = []
    raise Exception("override read_participants")
    return participants

def export_features_all(participants, featurelist = None, aoifeaturelist = None, aoifeaturelabels=None,
                         id_prefix = False, require_valid = True):
    data = []
    for p in participants:
        if not(p.is_valid()):
            print "user",p.id,"was not valid"
            continue
        fnames, fvals = p.export_features(featurelist=featurelist, aoifeaturelist=aoifeaturelist, 
                                          aoifeaturelabels = aoifeaturelabels,
                                          id_prefix=id_prefix, require_valid = require_valid)
        featnames = fnames
        data += fvals
    return featnames, data

def write_features_tsv(participants, outfile, featurelist = None, aoifeaturelist =  None, 
                       aoifeaturelabels=None, id_prefix = False):
    '''
    participants, outfile, featurelist = None, aoifeaturelist =  None, aoifeaturelabels=None, id_prefix = False
    '''
    fnames, fvals = export_features_all(participants, featurelist =  featurelist, 
                                        aoifeaturelabels = aoifeaturelabels,
                                        aoifeaturelist = aoifeaturelist, id_prefix=id_prefix)
    
    with open(outfile, 'w') as f:
        f.write(string.join(fnames, '\t') + '\n')
        for l in fvals:
            f.write(string.join(map(str, l), '\t') + '\n')

def partition(eventfile):
    """
    Generates the scenes based on the events log
    """
    return

def test_validity():
    return

def read_events(evfile):
    """
    Returns an array of L{Datapoints<Datapoint.Datapoint>} read from the event
    file.

    @type all_file: str
    @param all_file: The filename of the 'Event-Data.tsv' file output by the
    Tobii software.
    """
    with open(evfile, 'r') as f:
        lines = f.readlines()

    return map(Event, lines[(params.EVENTSHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])