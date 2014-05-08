'''
Created on 2012-08-23

@author: skardan
'''
from BasicParticipant import *
from Participant import export_features_all, write_features_tsv
from ValidityProcessing import output_Validity_info_Segments, output_percent_discarded, output_Validity_info_Participants

ul =        [61, 62]    # list of user recordings (files extracted for one participant from Tobii studio)
uids =      [61, 62]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

alogoffset =[ 3,  2]    # the time sifference between the eye tracker logs and the external log


ul =        [525330]    # list of user recordings (files extracted for one participant from Tobii studio)
uids =      [525330]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)

alogoffset =[0 ]    # the time difference between the eye tracker logs and the external log


####### Testing error handling
#ul =        [61, 62, 63]    # list of user recordings (files extracted for one participant from Tobii studio)
#uids =      [61, 62, 63]    # User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)
#
#alogoffset =[ 3,  2, 2]    # the time sifference between the eye tracker logs and the external log

###### Read participants
ps = read_participants_Basic(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir=params.EYELOGDATAFOLDER, 
                           prune_length = None, 
                           # aoifile = "./sampledata/general.aoi",
                           aoifile = "./brdata/aois_reduced_test_radar.tsv",
#                           aoifile = "./sampledata/Dynamic_1.aoi",
                           require_valid_segs = False, auto_partition_low_quality_segments = True
                           # rpsfile = "./sampledata/all_rest_pupil_sizes.tsv"
                           )
print
######

#explore_validation_threshold_segments(ps, auto_partition_low_quality_segments = False)
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 3)
output_percent_discarded(ps,'./outputfolder/radar_disc.csv')
output_Validity_info_Segments(ps, auto_partition_low_quality_segments_flag = False, validity_method = 2, threshold_gaps_list = [100, 200, 250, 300],output_file = "./outputfolder/radar_Seg_val.csv")
output_Validity_info_Participants(ps, include_restored_samples =True, auto_partition_low_quality_segments_flag = False)


##### WRITE features to file
print
# aoi_feat_names = (map(lambda x:"Test"+'_'+x, params.aoigeneralfeat))
aoi_feat_names = (map(lambda x:x, params.aoigeneralfeat))
print "exporting:", params.featurelist, "\n", aoi_feat_names
# write_features_tsv(ps, './outputfolder/sample_features.tsv',featurelist = params.featurelist, aoifeaturelabels=aoi_feat_names, id_prefix = False)
write_features_tsv(ps, './outputfolder/sample_sequences.tsv',featurelist = params.aoisequencefeat, aoifeaturelabels=aoi_feat_names, id_prefix = False)


# write_features_tsv(ps, './outputfolder/radar_features.tsv',featurelist = params.featurelist, aoifeaturelist=aoi_feat_names, id_prefix = False)
write_features_tsv(ps, './outputfolder/radar_sequences.tsv',featurelist = params.aoisequencefeat, aoifeaturelabels=aoi_feat_names, id_prefix = False)

#### Export pupil dilations for each scene to a separate file
# print "exporting: pupil dilatoin trends" 
# plot_pupil_dilation_all(ps, params.DIR + 'outputfolder\\pupilsizes\\', "problem1")
# plot_pupil_dilation_all(ps, params.DIR + 'outputfolder\\pupilsizes\\', "problem2")
