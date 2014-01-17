# this python file will load up the dataframe 
# created by MXrank.py.  it will calculate some
# fun stats, show you a pretty graph, 
# and then show you stats on top songs 
# for artists you click on.  it assumes
# that MXrank was run, but if you ran it on a friends'
# library, you can manually enter the path there
# as an option 

import pandas as pd
import numpy as np
import networkx as nx
import time
import pickle
import glob
import getpass
import matplotlib.pyplot as plt
from Tkinter import * 
global top_ten_artists, top_ten_artist_ids, df, DG,plt, button_pressed


#def graphs(id=[]):

# for macs
userid = getpass.getuser()	
tunedir = '/Users/' + userid + '/Documents/tuneGraphs/'

#if len(id) == 0:
	# point to the data
tuneGraph = tunedir + userid + '_DGtracks.gpickle'
tuneDataframe = tunedir + userid + '_Dataframe.pickle'
#else:
#	tuneGraph = tunedir + id + '_DGtracks.gpickle'
#	tuneDataframe = tunedir + id + '_Dataframe.pickle'

# read in the data frame	
df = pd.read_pickle(tuneDataframe)

# analyze the dataframe.  top ten most played artists
user_artist_plays = []
fm_artist_plays = []
uartists = []

# for each of the artists ...
for a in df.artist.unique():
	# get the total number of plays of any track by that artist
	user_artist_plays.append(np.sum(df.plays[df.artist == a]))
	# get the same from the last.fm community
	fm_artist_plays.append(np.sum(df.lastfm_plays[df.artist == a]))
	uartists.append(a)

# sort by the users plays 
playsXartist = zip(user_artist_plays,uartists)
playsXartist.sort(reverse=True)
sorted_plays, sorted_artists = zip(*playsXartist)

# just in case we need it later, sort 
# by the lastfm heat as well
lastplaysXartist = zip(fm_artist_plays,uartists)
lastplaysXartist.sort(reverse=True)
sorted_last_plays, sorted_last_artists = zip(*lastplaysXartist)

# get list
top_ten_artists = sorted_artists[:10]

# read in the graph
DG = nx.read_gpickle(tuneGraph)

# now let's plot
global artist_graphs

root = Tk()
# mod root window
root.title("top ten artists")
#root.geometry("1000,8000")

app = Frame(root)
app.grid()

# make ten buttons, each with the name of one of the top most played
# artist by the user
for b in range(10):
	exec('button' + str(b) + ' = Button(app,text=\"' + top_ten_artists[b] + 
		'\",command=lambda: button_pressed(' + str(b) + '))') in globals(), locals()
	exec('button' + str(b) + '.grid()') in globals(), locals()

def button_pressed(which):
	plt.close('all')
		
	this_artist = top_ten_artists[which]
	temp = df.track[df.artist == this_artist]
	tlist = temp.tolist()

	if len(tlist) > 10:
		tlist = tlist[:10]

	bar_vals = []
	for t in tlist:
		 p = df.plays[df.track == t]
		 bar_vals.append(p)

	bar_vals = np.asarray(bar_vals)	 

	fmheat_vals = []
	for t in tlist:
		 p = df.lastfm_plays[df.track == t]
		 fmheat_vals.append(p)

	fmheat_vals = np.asarray(fmheat_vals)	 

	page_rank_vals = []
	for t in tlist:
		 p = df.page_rank[df.track == t]
		 page_rank_vals.append(p)

	page_rank_vals = np.asarray(page_rank_vals)	 

	in_degree_vals = []
	for t in tlist:
		 p = df.in_degree[df.track == t]
		 in_degree_vals.append(p)

	bar_vals = np.asarray(bar_vals)	 
	fmheat_vals = np.asarray(fmheat_vals)	 
	page_rank_vals = np.asarray(page_rank_vals)
	in_degree_vals = np.asarray(in_degree_vals)	 

	nbars = range(len(tlist))
	 	
	#plt.figure()
	plt.subplot(2, 2, 1)
	plt.bar(nbars,bar_vals)
	plt.ylabel('users plays')

	plt.subplot(2, 2, 2)
	plt.bar(nbars,fmheat_vals)
	plt.ylabel('lastfm plays')

	ax = plt.subplot(2, 2, 3)
	plt.bar(nbars,page_rank_vals)
	plt.ylabel('page rank')
	ind = np.arange(len(tlist))
	width = 0.1
	XTickMarks = tlist
	ax.set_xticks(ind+width)
	xtickNames = ax.set_xticklabels(XTickMarks)
	plt.setp(xtickNames, rotation=45, fontsize=16)

	plt.subplot(2, 2, 4)
	plt.bar(nbars,in_degree_vals)
	plt.ylabel('in degree')

	plt.suptitle(this_artist, fontsize=24)
	plt.show()

		### also make a subgraph of connections to this song
	x = df.lastfm_ids[df.artist == this_artist] 
	x = x.tolist()

	connections = []
	for node in x:
		edgs = DG.edge[node]

		for target in edgs.keys():
			connections.append(target)

	nbunch = x + connections		
	G = nx.Graph(DG.subgraph(nbunch))

	# edge width is proportional to weight
	edgewidth=[]
	for (u,v,d) in G.edges(data=True):
	    edgewidth.append(len(G.get_edge_data(u,v)))

	pos=nx.spring_layout(G,iterations=20)
	plt.figure(figsize=(8,8))
	nodesize = df['plays'][df['lastfm_ids'].isin(G.nodes())] * 300
	labels = dict((n,d['track']) for n,d in G.nodes(data=True))
	nx.draw_networkx_edges(G,pos,alpha=0.4,node_size=0,width=1,edge_color='k')
	nx.draw_networkx_nodes(G,pos,labels=labels,fontize=12,node_size=nodesize,node_color='b',alpha=0.4)
	nx.draw_networkx_labels(G,pos, labels)
	
	
	#nx.draw(G,labels=labels,node_size=1000)
	plt.suptitle(this_artist, fontsize=24)
	plt.show()


root.mainloop()
