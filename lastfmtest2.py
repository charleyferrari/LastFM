"""

datalist = []

for artist in artistraw[u'artists'][u'artist']:
	print artist[u'name']
	artistname = copy.copy(artistraw[u'artists'][u'artist'][i][u'name'])

	print artistname

	artistid = copy.copy(str(artistraw[u'artists'][u'artist'][i][u'mbid']))
	tagurl = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&mbid=' + str(artistraw[u'artists'][u'artist'][i][u'mbid']) + '&api_key=85b96ff3cfc98fcc574b640d8adae011&format=json'
	tagraw = json.load(urllib2.urlopen(copy.copy(tagurl)))
	taglist = []

	for j in np.arange(0,len(tagraw[u'toptags'][u'tag'])):
		if tagraw[u'toptags'][u'tag'][j][u'count'] != u'0':
			taglist.append({'tagname' : tagraw[u'toptags'][u'tag'][j][u'name'], 'tagcount' : tagraw[u'toptags'][u'tag'][j][u'count']}.copy())

	dictadd = {'Name' : artistname,
			   'ID' : artistid,
			   'Tags' : copy.copy(taglist)}
	print dictadd['Name']

	datalist.append(dictadd.copy())




datalist = []

for artist in artistraw[u'artists'][u'artist']:
	tagurl = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&mbid=' + str(artist[u'mbid']) + '&api_key=85b96ff3cfc98fcc574b640d8adae011&format=json'
	tagraw = json.load(urllib2.urlopen(tagurl))
	taglist = []

	for tag in tagraw[u'toptags'][u'tag']:
		if tag[u'count'] != u'0':
			taglist.append({'TagName' : tag[u'name'], 'TagCount' : int(tag[u'count'])})

	dictadd = {'Name' : artist[u'name'], 'ID' : str(artist[u'mbid']), 'Tags' : taglist}

	datalist.append(dictadd.copy())


for artist in artistraw[u'artists'][u'artist']:
	tagurl = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&mbid=' + str(artist[u'mbid']) + '&api_key=85b96ff3cfc98fcc574b640d8adae011&format=json'
	tagraw = json.load(urllib2.urlopen(tagurl))
	taglist = []

	for tag in tagraw[u'toptags'][u'tag']:
		if tag[u'count'] != u'0':
			taglist.append({'TagName' : tag[u'name'], 'TagCount' : int(tag[u'count'])})

	dictadd = {'Name' : artist[u'name'], 'ID' : str(artist[u'mbid']), 'Tags' : taglist}

	datalist.append(dictadd.copy())




	"""

import pandas as pd

#sharedArtists = []
#totalArtists = []

frame = pd.DataFrame(columns = ['Tag A', 'Tag B', 'Shared', 'Total'])

"""

for atag in tagsByArtist:
	for btag in tagsByArtist:
		aartistlist = []
		bartistlist = []
		for artist in atag['Artists']:
			aartistlist.append(artist['ArtistID'])
		for artist in btag['Artists']:
			bartistlist.append(artist['ArtistID'])
		shared = len(set(aartistlist) & set(bartistlist))
		total = len(aartistlist + list(set(bartistlist) - set(aartistlist)))
		frame = frame.append(pd.DataFrame({'Tag A' : [atag], 'Tag B' : [btag], 'Shared' : shared, 'total' : total}))

"""

for idx,val in enumerate(tagsByArtist2):
	for btag in tagsByArtist2[idx+1:]:
		#frame.append(pd.DataFrame({'Tag A' : [val], 'Tag B' : [btag], 'Shared': 12, 'Total' : 100}))
		artistlista = []
		for artist in val['Artists']:
			artistlista.append(artist['ArtistID'])
		artistlistb = []
		for artist in btag['Artists']:
			artistlistb.append(artist['ArtistID'])

		countunique = len(artistlista + list(set(artistlistb) - set(artistlista)))
		countshared = len(set(artistlista) & set(artistlistb))
		counta = len(artistlista)
		countb = len(artistlistb)
		print val['Name']
		print btag['Name']
		print countshared
		print countunique
		frame = frame.append(pd.DataFrame({'Tag A' : [val['Name']], 'Tag B' : [btag['Name']], 'Shared' : countshared, 'Total' : countunique, 
			'Tag A Total' : counta, 'Tag B Total' : countb}))



frame = frame.reset_index(drop=True)