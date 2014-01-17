# audiograph


import audiograph
audiograph.MXrank.MXrank()
audiograph.graphs.graphs()

This module consists of two scripts which do rudimentary analysis 
of a users itunes library.  pyItunes is used to parse the xml
from a users itunes library (a .xml file may be specified or 
the users library will be found and used automatically).  

The data is moved from xml to a pandas dataframe. 

The average number of plays (times a given track is played) 
per track is calculated and a threshold is set for analysis.
This is only as a time saver .... the user may specify a lower
or higher threshold in order to analyze more or less of 
their itunes library.

The last.fm API is then leveraged in order to get information
on similarity data.  Each track in the user's library is 
sent in a quiery to last.fm's database (the artist and track
is usually sufficient to get a unique result).  The API 
returns data on all the tracks similar to the user's track.

Since there are a potentially large number of similar tracks
to any given track, similiar tracks are returned as long as 
they have a 'similarity value' (this is a normalized number 
between 0 and 1 that reflects how coincident the target 
track is with the source track based on how often users of 
last.fm who play the latter also play the former) above 0.2
or until ten similar tracks have been recorded.  These 
numbers can also be altered by the user via optional 
arugments to the function.

Data returned from last.fm are added to the dataframe 
and also built into a graph using networkx.  Networkx also
calculated pagerank and indegree. At the end of the 
extraction, these files are all saved in a folder
in the Documents directory (this exists on all macs).

In addition to the pickled graph, a .gepx file is saved.  This 
is handy to open in gephi, which is a really nice graph 
visualization package.

The second script loads the analyed data and calcualtes the 
top ten artists the user listens to overall.  For these 
artists, buttons are created which the user can click on to 
get play data along with pagerank and indegree data for the 
same tracks.  

In addition,  subgraph is displayed, showing the similar tracks 
for the top ten tracks of the artist selected via button press.
This graph has weighted edges tied to the degree of similarity.
The nodes are scaled according to the play counts.

The setup file will pull pyiTunes and pylast and run their 
respective setups.  The module is called audiograph.
audiograph.MXrank() followed by audiograph.graph()
