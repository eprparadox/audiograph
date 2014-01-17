import pandas as pd
import numpy as np
import networkx as nx
import random
import getpass

def create_sims():

	# for macs
	userid = getpass.getuser()	
	tunedir = '/Users/' + userid + '/Documents/tuneGraphs/'

	# point to the data
	tuneGraph = tunedir + userid + '_DGtracks.gpickle'
	tuneDataframe = tunedir + userid + '_Dataframe.pickle'
		
	# read in the data frame	
	df = pd.read_pickle(tuneDataframe)

	# analyze the dataframe.  top ten most played artists
	user_artist_plays = []
	fm_artist_plays = []
	uartists = []
	pagerank = []
	# for each of the artists ...
	for a in df.artist.unique():
		# get the total number of plays of any track by that artist
		user_artist_plays.append(np.sum(df.plays[df.artist == a]))
		# get the same from the last.fm community
		fm_artist_plays.append(np.sum(df.lastfm_plays[df.artist == a]))
		uartists.append(a)
		pagerank.append(df.page_rank[df.artist ==a])

	# sort by the users plays 
	playsXartist = zip(user_artist_plays,uartists)
	playsXartist.sort(reverse=True)
	sorted_plays, sorted_artists = zip(*playsXartist)

	# sort by the lastfm heat 
	lastplaysXartist = zip(fm_artist_plays,uartists)
	lastplaysXartist.sort(reverse=True)
	sorted_last_plays, sorted_last_artists = zip(*lastplaysXartist)

	# sort by pagerank
	# just in case we need it later, sort 
	# by the lastfm heat as well
	pagerankXartist = zip(pagerank,uartists)
	pagerankXartist.sort(reverse=True)
	sorted_page_ranks, sorted_PR_artists = zip(*pagerankXartist)

	# get lists
	top_ten_artists = sorted_artists[:10]
	top_ten_last_artists = sorted_last_plays[:10]
	top_ten_page_ranks = sorted_page_ranks[:10]

	# stim list 
	stim_list = top_ten_artists + top_ten_page_ranks + top_ten_last_artists
	stim_list = random.shuffle(thelist)

	prime_list = 'Please quickly say the first song out loud when you hear:' * len(stim_list)

	df = pd.DataFrame({'the_prime':prime_list,'the_text':stim_list})
	stimfile = tunedir + userid + '_ctrial.xls'
	df.to_excel(stimfile, sheet_name='sheet1', index=False)
