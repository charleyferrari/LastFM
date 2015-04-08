"""
First, I had to connect to the api. I set the nartsts variable to control how many artists I'm searching in the getartists method.
"""

import json
import urllib2
import numpy as np
import copy


API_KEY = '85b96ff3cfc98fcc574b640d8adae011'
API_SECRET = 'bb39ddc28d39c40060c00d51fb5a7f85'

def try_utf8(data):
    "Returns a Unicode object on success, or None on failure"
    try:
       return data.decode('utf-8')
    except UnicodeEncodeError:
       return None
    
nartists = 1000

artistraw = json.load(urllib2.urlopen('http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key=85b96ff3cfc98fcc574b640d8adae011&format=json&limit=' + str(nartists)))

"""
Next, I began scraping data. The data was a bit messy, so there were a few tests I had to run in order to get the data in a proper format. In some cases, like the MBID, fields would just be blank. In other cases, I just had to make sure the fields existed (with tags and toptags.) I also had to verify that the strings coming in were valid unicode.
The data structure I chose for this assignment was a nested list of dicts. Because the tags being brought in had to be associated with the top n artists, my first structure included one dict for each artist, with each dict containing the artists' tags. Below is a schema of this structure:

[
    {
        'Name' : artistname,
        'ID' : artist MBID,
        'tags' : [
                    {
                        'TagName' : tagname,
                        'TagCount' : tagcount
                    },...
                 ]
    },...
]

"""


datalist = []

for artist in artistraw[u'artists'][u'artist']:
    tagurl = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&mbid=' + str(artist[u'mbid']) + '&api_key=85b96ff3cfc98fcc574b640d8adae011&format=json'
    tagraw = json.load(urllib2.urlopen(tagurl))
    taglist = []


    if  artist[u'mbid'] != u'' and u'toptags' in tagraw.keys() and u'tag' in tagraw[u'toptags'].keys() and not(try_utf8(artist[u'name']) is None):
        #print artist[u'name']
        if type(tagraw[u'toptags'][u'tag']) == list:
            for tag in tagraw[u'toptags'][u'tag']:
                if tag[u'count'] != u'0':
                    taglist.append({'TagName' : tag[u'name'], 'TagCount' : int(tag[u'count'])})
                elif type(tagraw[u'toptags'][u'tag']) == dict:
                    if tagraw[u'toptags'][u'tag'][u'count'] != u'0':
                        taglist.append({'TagName' : tagraw[u'toptags'][u'tag'][u'name'], 'TagCount' : int(tagraw[u'toptags'][u'tag'][u'count'])})

    dictadd = {'Name' : artist[u'name'], 'ID' : str(artist[u'mbid']), 'Tags' : taglist}

    datalist.append(dictadd.copy())


"""

Once I have the data in memory, I can change the format to be tag centric rather than artist centric. In order to find out how tags are related, instead of viewing a list of artists and their tags, I'd rather see a list of tags and the artists they're associated with. The below code flips the data into this new format:

[
    {
        'Name' : tagname,
        'Artists' : [
                        {
                            'ArtistName' : artistname,
                            'ArtistID' : artistmbID
                        },...
                    ]
    },...
]

"""


masterTagList = []
for item in datalist:
    for tag in item['Tags']:
        if not tag['TagName'] in masterTagList:
            masterTagList.append(tag['TagName'])

tagsByArtist = []
for tag in masterTagList:
    #print tag
    artistlist = []
    for artist in datalist:
        for artisttag in artist['Tags']:
            if artisttag['TagName'] == tag:
                artistlist.append({'ArtistName' : artist['Name'], 'ArtistID' : artist['ID']})
    tagsByArtist.append({'Name' : tag, 'Artists' : artistlist})


"""

The question of how related tags were was a surprisingly difficult one. I used the below cell as a practice ground, 
testing out various types of measures. I took the first 50 tags, took every two tag combination, and inserted my measure 
into a pandas dataframe to get an idea of what was going on. Originally I was looking at the shared or divergent artists for each tag,
and attempted to create my measure based solely on these measures. I was thinking of the tags solely as nodes, viewing the shared artists 
as connections, and the divergent artists as loose branches when considering two tags. Thinking in this way, I was concerned with how the 
raw number of associated artists affects my measures. If I'm simply looking at the # shared artists divided by the # of total artists the 
tags are associated with, it's easier for tags with small numbers of associated artists to show high measures of connectivity. This was 
indeed what I would see in scatter charts looking at tag totals versus my measures: with low totals, the variance of the measures was higher.
I then had an insight to instead look at the tags throughout the entire "artist space". Instead of viewing a tag as only a tag with two 
artists, I would include the fact that it is NOT associated with the other 998 artists. Using a trivial example below with 10 artists, consider 
the two lists. The lists are ordered by artists. 0 means the tag is not associated with the artist, while 1 means it is:

TagA = [0,0,0,1,0,0,1,0,0,0]
TagB = [0,0,1,1,0,0,0,0,0,0]

In this case, the tag can be thought of as having a "distribution" among the artists. At first this seemed counterintuitive; two tags would
become more related as the number of artists in the sample increased. But, this can be seen as a useful expression of similarity. If I add a 
marginal artist, that artist is further evidence of the similarity of Tag A and Tag B by not being associated with either one of them.
Using this information, I could create a similarity measure by counting the numbers of shared 1's and 0's and dividing that by the total number 
of artists. In my program, the numerator is calculated by subtracting the number of divergent artists Tag A or B are associated with from the 
total number of artists, while the denominator remains the total number of artists. The real probem with this measure alone becomes apparent 
when considering the case of two tags with different numbers of shared artists, like the below set:

TagA = [0,0,0,1,0,0,1,0,0,0]
TagB = [0,0,0,1,0,0,1,0,0,0]
 
TagC = [0,0,0,1,0,0,1,1,1,0]
TagD = [0,0,0,1,0,0,1,1,1,0]

According to my similarity measure, Tags A and B are just as related as tags C and D. They both share the same distribution. But, one would 
intuitively think that tags C and D are more related, since they share more connections. To account for this, I created a connectivity measure. 
Here, I would just take the number of shared artists as my numerator and keep my denominator as the total number of artists.
These two measures can be multiplied together to come up with a total relatedness measure, but I think it's important to keep the two separate 
measures of similarity and connectedness handy as well. Intuitively, one can see what ends up happening here. Both connectivity and similarity 
vary between 0 and 1. Two tags with 0 artists each would be a 1 in similarity, but would produce a 0 in connectivity, and hence would have a 
relatednesss measure of 0. As the number of artists each tag is associated with increases, the connectivity increases. There's a greater chance 
with a greater number of artists that they will be divergent, but this is taken into account by using the similarity score. Finally, a perfect 
relatedness score of 1 would be acheived if two tags were associated with every single artist. The cell directly below this one shows my pandas 
test dataframe which I used to create and test differnt measures. Below that is a few of the test graphs I was originally using to judge my 
scores, and then finally there is a cell including two functions to calculated these two separate measures (all you need to do is multiply them 
together to get a total relatedness measure.) The first two cells aren't necessary for the measure, I just kept them in to show my thought 
process. I ended up doing some quick googling, and saw this was a very rich topic of research. While I didn't get as in depth as other researchers 
had, what I found helped shape how I was looking at things conceptually. This paper in particular made me think of tags as being distributed 
across artists, rather than just looking at the connections that were present.

"""

import pandas as pd

frame = pd.DataFrame(columns = ['Tag A', 'Tag B', 'Shared', 'Total'])

tagsByArtist2 = tagsByArtist[0:50]

for idx,atag in enumerate(tagsByArtist2):
    for btag in tagsByArtist2[idx+1:]:
        #frame.append(pd.DataFrame({'Tag A' : [atag], 'Tag B' : [btag], 'Shared': 12, 'Total' : 100}))
        artistlista = []
        for artist in atag['Artists']:
            artistlista.append(artist['ArtistID'])
        artistlistb = []
        for artist in btag['Artists']:
            artistlistb.append(artist['ArtistID'])
        
        countunique = len(artistlista + list(set(artistlistb) - set(artistlista)))
        countshared = len(set(artistlista) & set(artistlistb))
        countdiverg = len(set(artistlista) ^ set(artistlistb))
        counta = len(artistlista)
        countb = len(artistlistb)
        #print atag['Name']
        #print btag['Name']
        #print countshared
        #print countunique
        frame = frame.append(pd.DataFrame({'Tag A' : [atag['Name']], 'Tag B' : [btag['Name']], 'Different' : countdiverg,
                                           'Shared' : countshared, 'Total' : countunique, 
                                           'Tag A Total' : counta, 'Tag B Total' : countb}))



frame = frame.reset_index(drop=True)

############################################################################################################

#frame = frameorig

#frame['Measure'] = frame['Shared'] / frame['Total'] #4/6
#frame['Measure'] = frame['Shared'] / (frame['Tag A Total'] + frame['Tag B Total']) #4/10
frame['Similarity'] = (nartists - frame['Different']) / nartists
frame['Connectedness'] = frame['Shared'] / nartists

#frame = frame[frame['Tag A Total'].lt(5)]
#frame = frame[frame['Measure'].lt(1)]

############################################################################################################

def similarityScore(tagA, tagB, nartists):
    "Calculates the similarity between these two tag objects, pulled from the tagsByArtist Dict."
    artistlista = []
    for artist in tagA['Artists']:
        artistlista.append(artist['ArtistID'])
    
    artistlistb = []
    for artist in tagB['Artists']:
        artistlistb.append(artist['ArtistID'])
         
    countdiverg = len(set(artistlista) ^ set(artistlistb))
    
    return (float(nartists) - float(countdiverg)) / float(nartists)

def connectivityScore(tagA, tagB, nartists):
    "Calculates the connectedness between two tag objects, pulled from the tagsByArtist Dict."
    artistlista = []
    for artist in tagA['Artists']:
        artistlista.append(artist['ArtistID'])
    
    artistlistb = []
    for artist in tagB['Artists']:
        artistlistb.append(artist['ArtistID'])    
 
    countshared = len(set(artistlista) & set(artistlistb))
    
    return float(countshared) / float(nartists)

############################################################################################################

"""

Instead of using tag relatedness to measure the relatedness of artists, I'd probably use a very similar method to what I used 
with the tags. My model can be thought of as a table, with tags on one axes and artists on the other. This table is populated 
with 1's and 0's: 1 if the tag and artist are associated, and 0 if they are not. Using this model, I can use the exact same data 
structure in calculated artist relatedness. In this case, I'd have lists of 1's and 0's for my artists, with each 1 and 0 representing 
the artist's distribution in "tagspace":

Artist A = [0,0,0,1,1,0,0]
Artist B = [1,0,0,0,1,0,0]


To bring this data in, I started with an artist list, and associated tags. I'd use members of this list in my functions to calculated 
artist relatedness:

"""

ntags = len(tagsByArtist)

def similarityScoreArtist(artistA, artistB, ntags):
    "Calculates the similarity between these two artist objects, pulled from the datalist Dict."
    taglista = []
    for tag in artistA['Tags']:
        taglista.append(tag['TagName'])
    
    taglistb = []
    for tag in artistB['Artists']:
        taglistb.append(tag['TagName'])
         
    countdiverg = len(set(taglista) ^ set(taglistb))
    
    return (float(ntags) - float(countdiverg)) / float(ntags)

def connectivityScoreArtist(artistA, artistB, nartists):
    "Calculates the connectedness between two tag objects, pulled from the datalist Dict."
    taglista = []
    for tag in artistA['Tags']:
        taglista.append(tag['TagName'])
    
    taglistb = []
    for tag in artistB['Artists']:
        taglistb.append(tag['TagName'])    
 
    countshared = len(set(artistlista) & set(artistlistb))
    
    return float(countshared) / float(ntags)

############################################################################################################

"""
For this analysis I was able to do everything in memory. I think this sort of many to many data structure lends itself to a 
nosql database. You could create tag and artist reference tables, and then relate them to a mapping table in a SQL database, but the 
"list of dicts" structure lends itself perfectly to MongoDB. The only drawback is that I would need to use two collections: one showing 
tags nested in artists, and the other showing artists nested in tags. In working with this data, I thought a graph database like Neo4J might 
be an interesting choice. I could imagine both artists and tags becoming nodes, and I'd be able to view both artists by tags and tags by artists 
at the same time. While this would be interesting, and worth a look for a holistic picture of the data, I think the dict structure being so close 
makes MongoDB the best choice.

"""


import pymongo

client = pymongo.MongoClient()

db = client.lastfm

artistcollection = db.artists
tagcollection = db.tags

artistcollection.insert(datalist)
tagcollection.insert(tagsByArtist)

client.disconnect()