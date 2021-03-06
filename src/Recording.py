"""
UBC Eye Movement Data Analysis Toolkit
Recording class

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
Modified by: Samad Kardan to a general class independent of the study
Modified by: Mike Wu to an abstract class to be extended for each type of eye tracker

Class to hold all the data from one recording (i.e, one complete experiment session)
for one participant

"""

from abc import ABCMeta, abstractmethod
from data_structures import Datapoint, Fixation, Event
from Scene import *
from AOI import *
from utils import *


class Recording:
    __metaclass__ = ABCMeta

    def __init__(self, all_file, fixation_file, event_file=None, media_offset=(0, 0)):
        """
        :param all_file: path to file that contains all gaze points
        :param fixation_file :path to file that contains all gaze points
        :param event_file :path to file that contains all events
        :param media_offset: the coordinates of the top left corner of the window showing the interface under study.
        (0,0) if the interface was in full screen (default value).
        """
        self.media_offset = media_offset

        self.all_data = self.read_all_data(all_file)
        if len(self.all_data) == 0:
            raise Exception("The file '" + all_file + "' has no samples!")

        self.fix_data = self.read_fixation_data(fixation_file)
        if len(self.fix_data) == 0:
            raise Exception("The file '" + fixation_file + "' has no fixations!")

        if event_file is not None:
            self.event_data = self.read_event_data(event_file)
            if len(self.event_data) == 0:
                raise Exception("The file '" + event_file + "' has no events!")
        else:
            self.event_data = None

    @abstractmethod
    def read_all_data(self, all_file):
        """ Read the data file that contains all gaze points.

        :param all_file: path to file that contains all gaze points
        :return: a list of Datapoints
        :rtype: list[Datapoint]
        """
        pass

    @abstractmethod
    def read_fixation_data(self, fixation_file):
        """ Read the data file that contains all fixations.

        :param fixation_file :path to file that contains all gaze points
        :return: a list of Fixations
        :rtype: list[Fixation]
        """
        pass

    @abstractmethod
    def read_event_data(self, event_file):
        """ Read the data file that contains all events.

        :param event_file :path to file that contains all events
        :return: a list of Events
        :rtype: list[Event]
        """
        pass

    def process_rec(self, segfile=None, scenelist=None, aoifile=None,
                    aoilist=None, prune_length=None, require_valid_segs=True,
                    auto_partition_low_quality_segments=False, rpsdata=None, export_pupilinfo=False):
        """Processes the data for one recording (i.e, one complete experiment session)

        Args:
            segfile: If not None, a string containing the name of the segfile 
                with segment definitions in following format:
                Scene_ID<tab>Segment_ID<tab>start time<tab>end time<newline>
                e.g.:
                s1    seg1    0    5988013
                With one segment definition per line
            scenelist: If not None, a list of Scene objects
            *Note: At least one of segfile and scenelist should be not None
                
            aoifile: If not None, a string containing the name of the aoifile 
                with definitions of the "AOI"s.
            aoilist: If not None, a list of "AOI"s.
            *Note:  if aoifile is not None, aoilist will be ignored
                    if both aoifile and aoilist are none AOIs are ignored
             
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the beginning of each Segment in which
                samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
            
            require_valid_segs: a boolean determining whether invalid "Segment"s
                will be ignored when calculating the features or not. default = True 
            
            auto_partition_low_quality_segments: a boolean flag determining whether
                EMDAT should automatically split the "Segment"s which have low sample quality
                into two new sub "Segment"s discarding the largest invalid sample gap in 
                the "Segment". default = False
                
            rpsdata: a dictionary with rest pupil sizes: (scene name is a key, rest pupil size is a value)
        Returns:
            a list of Scene objects for this Recording
            a list of Segment objects for this recording. This is an aggregated list
            of the "Segment"s of all "Scene"s in the Recording 
        """

        if segfile is not None:
            scenelist = read_segs(segfile)
            print "Done reading the segments!"
        elif scenelist is None:
            print "Error in scene file"

        if aoifile is not None:
            aoilist = read_aois(aoifile)
            print "Done reading the AOIs!"
        elif aoilist is None:
            aoilist = []
            print "No AOIs defined!"

        scenes = []
        for scid, sc in scenelist.iteritems():
            print "Preparing scene:" + str(scid)
            if params.DEBUG:
                print "len(all_data)", len(self.all_data)
            try:
                # get rest pupil size data
                if rpsdata is not None:
                    if scid in rpsdata.keys():
                        scrpsdata = rpsdata[scid]
                    else:
                        scrpsdata = 0
                        print rpsdata.keys()
                        if params.DEBUG:
                            raise Exception(
                                "Scene ID " + scid + " is not in the dictionary with rest pupil sizes. rpsdata is set to 0")
                        else:
                            print "Scene ID " + scid + " is not in the dictionary with rest pupil sizes. rpsdata is set to 0"
                            pass
                else:
                    scrpsdata = 0
                new_scene = Scene(scid, sc, self.all_data, self.fix_data, event_data=self.event_data, aoilist=aoilist,
                                  prune_length=prune_length,
                                  require_valid=require_valid_segs,
                                  auto_partition=auto_partition_low_quality_segments, rest_pupil_size=scrpsdata,
                                  export_pupilinfo=export_pupilinfo)
            except Exception as e:
                warn(str(e))
                new_scene = None
                if params.DEBUG:
                    raise
                else:
                    pass
            if new_scene:
                scenes.append(new_scene)
        segs = []
        for sc in scenes:
            segs.extend(sc.segments)
        return segs, scenes


def read_segs(segfile):
    """Returns a dict with scid as the key and segments as value from a '.seg' file.

    A '.seg' file consists of a set of lines with the following format:
    scene_name[\t]segment_name[\t]start_time[\t]end_time[\n]

    scene_name is the id of the Scene that this Segment belongs to,
    segment_name is the id of the Segement,
    and start_time and end_time determines the time interval for the Segment

    Args:
        segfile: A string containing the name of the '.seg' file

    Returns:
        a dict with scid as the key and segments as value
    """
    scenes = {}
    with open(segfile, 'r') as f:
        seglines = f.readlines()

    for l in seglines:
        l = l.strip()
        l = l.split('\t')
        if l[0] in scenes:
            scenes[l[0]].append((l[1], int(l[2]), int(l[3])))
        else:
            scenes[l[0]] = [(l[1], int(l[2]), int(l[3]))]
    return scenes


def read_aois(aoifile):
    """Returns a list of "AOI"s read from a '.aoi' file.

    The '.aoi' files have pairs of lines of the form:
    aoiname[tab]point1x,point1y[tab]point2x,point2y[tab]...[new line]
    #[tab]start1,end1[tab]...[new line]

    The first line determines name of the AOI and the coordinates of each vertex of
    the polygon that determines the boundaries of the AOI.
    The second line which starts with a '#' is optional and determines the time
    intervals when the AOI is active. If the second line does not exist the AOI will
    be active throughout the whole session (global AOI).
    *Note: If the AOIs are exported from Tobii software the '.aoi' file will only have the
    first line for each AOI and you need to override this method to generate AOIs that are
    active only at certain times (non-global AOI).

    Args:
        aoifile: A string containing the name of the '.aoi' file

    Returns:
        a list of "AOI"s
    """
    with open(aoifile, 'r') as f:
        aoilines = f.readlines()

    return read_aoilines(aoilines)


def read_aoilines(aoilines):
    """
    Args:
        aoilines: List of lines from a '.aoi' file

    Returns:
        list of AOIs
    """
    aoilist = []
    polyin = []
    last_aid = ''

    for line in aoilines:
        chunks = line.strip().split('\t')
        if chunks[0].startswith('#'):  # second line
            if polyin:
                seq = []
                for v in chunks[1:]:
                    seq.append((eval(v)))

                aoi = AOI(last_aid, polyin, [], seq)
                aoilist.append(aoi)
                polyin = []
            else:
                raise Exception('error in the AOI file')
        else:
            if polyin:  # global AOI
                aoi = AOI(last_aid, polyin, [], [])
                aoilist.append(aoi)
                polyin = []

            last_aid = chunks[0]  # first line
            for v in chunks[1:]:
                polyin.append((eval(v)))

    if polyin:  # last (global) AOI
        aoi = AOI(last_aid, polyin, [], [])
        aoilist.append(aoi)

    return aoilist


def get_pupil_size(pupilleft, pupilright):
    if pupilleft is None and pupilright is None:
        return -1
    if pupilleft is None:
        return pupilright
    if pupilright is None:
        return pupilleft
    return (pupilleft + pupilright) / 2.0


def get_distance(distanceleft, distanceright):
    if distanceleft is None and distanceright is None:
        return -1
    if distanceleft is None:
        return distanceright
    if distanceright is None:
        return distanceleft
    return (distanceleft + distanceright) / 2.0