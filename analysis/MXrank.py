import pylast
from pyItunes import *
import getpass
import glob
import pandas as pd
import numpy as np
import networkx as nx
import time
import pickle
import os

def MXrank(path_to_xml=[],id=[],stdM=1,simthresh=0.2,maxsimtracks=10):
    #
    """
    this python file takes metadata from itunes, spotify,
    rdio, et cetera and creates a graph of the most
    played tracks using similarity data from last.fm.
    this graph is supplemented with 'hotness' data from
    the echo nest, if it exists (and maybe last.fm if 
    it doesn't exist on echonest)

    these data are analyzed for the set of tracks most 
    likely to be able to distinguish between a frequency 
    based model of popular music memory or a page rank 
    model.  the stimuli are saved in a format that can
    be read by psychopy to perform the priming exeperiment.  

    if you enter a path to an iTunes xml file as an argument,
    it will be used.  otherwise, MXrank will detect the current 
    users itunes libarary and analyze that

    stdM means standard deviation multiplier.  that is, there are 
    diminishing returns on getting graph information for the whole 
    library since last.fm must be queried for each track.  therefore
    we'll check what the average number of plays for each track
    in the library is and only analyze tracks that have been played 
    more times than 1 standard deviation from the mean.  if the user
    wants to analyze even less of their library (and get it done 
    more quickly) they can just augment this number
    """
    # for macs
    userid = getpass.getuser()

    # enter my api key
    API_KEY = "187cdf1efbcb39ab5ac931d0f655937d" 
    API_SECRET = "e0fb8188d443ee0958a099140dac8893"

    # authenticate
    username = "eprparadox"
    password_hash = pylast.md5("pylast31415")

    # the 'network' object will be connected to last.fm
    network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = 
        API_SECRET, username = username, password_hash = password_hash)

    # for itunes
    # read the iTunes library 
    if len(path_to_xml) == 0:
        tunepath = '/Users/' + userid + '/Music/iTunes/*.xml'
    else:
        tunepath = path_to_xml
    tunelib = glob.glob(tunepath)

    if len(id) == 0:
        userid2 = id
    else:
        userid2 = userid
        
    # read in the library
    pl = XMLLibraryParser(tunelib[0])
    tune_library = Library(pl.dictionary)

    # read the library and convert to pandas data frame
    # ('I' will prepend variables recorded from iTunes)
    Iplaycount = np.zeros(len(tune_library.songs)) # to record play counts
    Itrack_title = [] # songs
    Iartist = []

    print 'reading itunes data ...'
    # for each song get the artist and title 
    # (sufficient for last.fm to get a unique identifier 
    # in most cases)
    for ind, song in enumerate(tune_library.songs):
    	Itrack_title.append(song.name)
    	Iartist.append(song.artist)
        # and also record how frequently the user
        # has played this track    
    	if song.play_count is not None:
    		Iplaycount[ind] = song.play_count
    	

    # put into dataframe (not sure if this is going to be worthwhile or not)
    data = {'track':Itrack_title,'artist':Iartist,'plays':Iplaycount}
    df = pd.DataFrame(data,columns = ['track','artist','plays'])	

    # sort by plays 
    df = df.sort(columns='plays',ascending=False)
    # dumb
    df['relx'] = range(len(Itrack_title))
    df = df.set_index(['relx'])

    print 'complete'
    print '\n\n'

    # too much.  too much. last.fm is too slow.  we'll use 
    # track that it's reasonable to assume users are 
    # more familiar with
    mean_plays = np.mean(df.plays[df.plays > 0])
    std_plays = np.std(df.plays[df.plays > 0])
    dfFamiliar = df[df.plays > mean_plays + stdM*std_plays]

    # store data 
    # start building a graph
    # (un)directed
    DG = nx.DiGraph()
    gtracks = []; gartists = [];
    gplays = []; gfmplays = []; fmidx = [];


    # get some data on the number and values of similars
    num_similars = []; mean_sim_vals = [];

    print 'building graph with last.fm data ...'
    lstart = time.time()

    # track rows not in last.fm
    rows_to_drop = [];

    #for artist, track in zip(df.track,df.artist):
    for ind in range(len(dfFamiliar)):
    #for ind in range(78):
        artist_name = dfFamiliar.artist[ind]; 
        track_name = dfFamiliar.track[ind]; 
        plys = dfFamiliar.plays[ind]; 

        # get last.fm info
        # changed so i don't add data about this track 
        # till i'm sure it's on last.fm
        try: 
            curr_track = network.get_track(artist_name,track_name)
            fmplays = curr_track.get_playcount()
            fidx = curr_track.get_id()
            

            # it's there, add to the lists
            gartists.append(artist_name)
            gtracks.append(track_name)
            gplays.append(plys)
            gfmplays.append(fmplays)

            # add this node to the graph as is.
            DG.add_node(fidx,track=track_name,artist=artist_name,plays=int(plys),fmheat=int(fmplays))
            fmidx.append(fidx)
            print 'user track added ----- ' + track_name
            #try:
            similars = curr_track.get_similar
            sim_data = similars()
            
            # record all the similars
            stracks = []; sartists = []
            sfmids = []; sfmlplays = []
            sim_vals = []

            nsims_counter = 0   
            nsims_val_total = 0

            for i,s in enumerate(sim_data):
                sim_val = s[-1] 
                
                
                if sim_val > simthresh and i < maxsimtracks: 
                    print 'lastFM similar TB added ----- ' + s[0].get_name()  
                    #sim_vals.append(sim_val)
                    nsims_counter += 1
                    nsims_val_total += sim_val

                    # add meta data for similars
                    stemp = s[0].get_name
                    strack = stemp(0)
                    sartist_dat = s[0].get_artist()
                    sartist = sartist_dat.get_name()
                    sfmid = s[0].get_id()
                    sfmplay = s[0].get_playcount()
                    DG.add_node(sfmid,track=strack,artist=sartist,fmheat=int(sfmplay))
                    DG.add_edge(fidx,sfmid,weight=sim_val)

            if (nsims_counter > 0):
                num_similars.append(nsims_counter)
                mean_sim_vals.append(nsims_val_total/nsims_counter) 
                #print '\n'
            else:
                num_similars.append(0)
                mean_sim_vals.append(0) 
                #print '\n'
        
            print '\n'
        except:
            print 'track ' + str(track_name) + ' is not in the last.fm database'
            #dfFamiliar = dfFamiliar.drop(dfFamiliar.index[[ind]])
            rows_to_drop.append(ind)
            print'\n'        

    # pull tracks we couldn't identify
    dfFamiliar = dfFamiliar.drop(dfFamiliar.index[rows_to_drop])
    dfFamiliar.reset_index(drop=True)

    # add last.fm ids to dataframe
    dfFamiliar['lastfm_ids'] = fmidx

    # add last.fm ids to dataframe
    dfFamiliar['lastfm_plays'] = gfmplays

    # add indegree to graph
    indegree_list = list(DG.in_degree_iter(weight='weight'))
    for n,ind in indegree_list:
        DG.node[n]['in_degree'] = ind

    # add pagerank to graph.
    pdict = nx.pagerank(DG)    
    for n in pdict:
        DG.node[n]['pagerank'] = np.double(pdict[n])


    # kinda backwards but add PR and IND 
    # to dataframe
    page_ranks = []; in_degrees = [];
    for n in dfFamiliar['lastfm_ids']:
        page_ranks.append(DG.node[n]['pagerank'])
        in_degrees.append(DG.node[n]['in_degree'])

    dfFamiliar['page_rank'] = page_ranks
    dfFamiliar['in_degree'] = in_degrees        

    lend = time.time()
    print '*'*80
    print '** similarity graph created in ' + str((lend-lstart)/60) +  ' minuets' + ' '*25 + ' **'
    print '** pickeling similarity graph ... ' +  ' '*44 + '**'

    # make an output directory
    tunedir = '/Users/' + userid + '/Documents/tuneGraphs/'
    if not os.path.isdir(tunedir):
        os.mkdir(tunedir)

    # pickle the graph
    gfile_name = tunedir + userid2 + '_DGtracks.gpickle'
    pickle.dump(DG,open(gfile_name,"wb"))

    # save for gephi
    gfile_name = tunedir + userid2 + '_DGtracks.gexf'
    nx.write_gexf(DG,gfile_name)

    # add data about the number of similars and 
    # mean similarity value to the dataFrame
    dfFamiliar['num_sims'] = np.array(num_similars)
    dfFamiliar['sim_vals'] = np.array(mean_sim_vals)

    # pickle the dataFrame
    dffilename = tunedir + userid2 + '_Dataframe.pickle'
    dfFamiliar.to_pickle(dffilename)
    print '** graphs and data have been stored in ' + tunedir + ' **'
    print '*'*80

    return DG, df