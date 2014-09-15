from app import app, render_template
import requests
from BeautifulSoup import BeautifulSoup

@app.route('/')
@app.route('/list/<peer_seeds>/<tv_movies>')
@app.route('/list/<peer_seeds>/<tv_movies>/<page>')
def listBy(peer_seeds=None, tv_movies=None, page=None):
	if peer_seeds is None: peer_seeds = 'P'
	if tv_movies is None: tv_movies = 'tv'
	data = listTorrents(peer_seeds,tv_movies, None, page)
	return render_template("list.html", 
		urls=data['urls'],
		title=getPageTitle(peer_seeds, tv_movies, None),
		pagination=data['pagination']
	)

@app.route('/recent')
@app.route('/recent/<page>')
def recent(page=None):
	data = listTorrents(None, None, 'added:7d', page)
	return render_template("list.html", 
		urls=data['urls'],
		title=getPageTitle(None, None, 'added:7d'),
		pagination=data['pagination']
	)

@app.route('/magnet/<url>')
def magnet(url):
	return render_template("magnet.html", 
		link=getMagnetLink(url),
		title='Download'
	)

@app.route('/search/<query>')
@app.route('/search/<query>/<page>')
def search(query, page=None):
	data = listTorrents(None, None, query, page)
	return render_template("list.html", 
		urls=data['urls'],
		title=getPageTitle(None, None, query),
		pagination=data['pagination']
	)

@app.route('/cloud')
def cloud():
	return render_template("cloud.html",
		urls=getTagCloud(),
		title='Tag Cloud'
	)

def getHeaders():
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'
	}
	return headers

def listTorrents(peer_seeds=None, tv_movies=None, query=None, page=None):
	if peer_seeds and tv_movies and not page:
		r = requests.get('http://torrentz.eu/verified'+peer_seeds+'?f='+tv_movies,headers=getHeaders())
	elif peer_seeds and tv_movies and page:
		r = requests.get('http://torrentz.eu/verified'+peer_seeds+'?f='+tv_movies+'&p='+page,headers=getHeaders())
		print r.url
	elif query and not page:
		r = requests.get('http://torrentz.eu/search?f='+query,headers=getHeaders())
	elif query and page:
		r = requests.get('http://torrentz.eu/search?f='+query+'&p='+page,headers=getHeaders())
	else: return []

	print 'listTorrents - %f' % r.elapsed.total_seconds()
	
	data = getPaginatedList(r,query)
	return data

def getPageTitle(peer_seeds=None, tv_movies=None, query=None):
	options = {
		'N':{'tv':'TV sorted by Rating','movies':'Movies sorted by Rating'},
		'D':{'tv':'TV sorted by Date','movies':'Movies sorted by Date'},
		'S':{'tv':'TV sorted by Size','movies':'Movies sorted by Size'},
		'P':{'tv':'TV sorted by Peers','movies':'Movies sorted by Peers'},
		'True':'Search results for %s' % query,
		'False':'Last week\'s favorites'
	}
	if peer_seeds and tv_movies:
		return options[peer_seeds][tv_movies]
	if query:
		return options[str(query != 'added:7d')]
	else: return 'Torrents'

def getMagnetLink(h):
	options = {
		'1337x':'1337x.to',
		'kickass':'kickass.to',
		'katproxy':'katproxy.com'
	}
	r = requests.get('http://torrentz.eu/'+h, headers=getHeaders())

	print 'getMagnetLink - %f' % r.elapsed.total_seconds()

	soup = BeautifulSoup(r.text)
	dt = soup.findAll('a', attrs={'rel':'e'})
	for x in dt:
		for option in options:
			if option in x['href']:
				magnet = extractMagnet(option,x['href'])
				if magnet:
					link = Link()
					link.url = magnet['href']
					link.mirror = options[option]
					return link
	return None

def getTagCloud():
	r = requests.get('http://torrentz.eu/i', headers=getHeaders())

	print 'getTagCloud - %f' % r.elapsed.total_seconds()

	soup = BeautifulSoup(r.text)
	dt = soup.find('div',attrs={'class':'cloud'})
	urllist = []
	links = dt.findAll('a')
	for link in links:
		lnk = TagCloudLink()
		lnk.url = link['href'].rsplit('/',1)[1]
		lnk.name = link.text
		lnk.font_size = link['style']
		urllist.append(lnk)
	return urllist

def getPaginatedList(r,query):
	urllist = []
	soup = BeautifulSoup(r.text)
	if query:
		pagination = getPagination(soup,query)
	else: pagination = getPagination(soup)
	dls = soup.findAll('dl')
	for dl in dls:
		a = dl.find('a')
		if a and len(a['href']) > 40 and a.text:
			dd = dl.find('dd')
			if dd:
				mb = dd.find('span', attrs={'class':'s'}).string
				seeds = dd.find('span', attrs={'class':'u'}).string
				leechers = dd.find('span', attrs={'class':'d'}).string
				date = dd.find('span', attrs={'class':'a'}).find('span').string
				tor = Torrent()
				tor.url = 'http://torrentz.eu'
				tor.torrenthash = a['href']
				tor.title = a.text
				if date:
					tor.date = date
				if mb:
					tor.mb = mb
				if seeds:
					tor.seeds = seeds
				if leechers:
					tor.leechers = leechers
				urllist.append(tor)
	data = {'pagination':pagination,'urls':urllist}
	return data

def extractMagnet(site,x):
	options = {
		'1337x':{'attr':'class','name':'magnetDw'},
		'kickass':{'attr':'title','name':'Magnet link'},
		'katproxy':{'attr':'title','name':'Magnet link'}
	}
	r = requests.get(x)

	print 'extractMagnet - %f' % r.elapsed.total_seconds()
	
	soup = BeautifulSoup(r.text)
	magnet = soup.find('a', attrs={options[site]['attr']:options[site]['name']})
	return magnet

def getPagination(soup, query=None):
	div = soup.find('div',attrs={'class':'results'})
	links = div.findAll('a')
	lastindex = len(links) - 1
	next = None
	prev = None
	if 'p=' in links[1]['href']: prev = links[1]
	if 'p=' in links[lastindex]['href']: next = links[lastindex]
	pagination_links = {'next':'','prev':''}
	if next: pagination_links['next'] = getPaginationLink(query,next)
	if prev: pagination_links['prev'] = getPaginationLink(query,prev)
	return pagination_links

def getPaginationLink(query, soup_part):
	q = None
	link = None
	
	options = {
		'verifiedP?':'/list/P',
		'verifiedS?':'/list/S',
		'verifiedD?':'/list/D',
		'verifiedN?':'/list/N',
		'search?f=added':'/recent',
		'nested': {
			'f=tv':'tv',
			'f=movies':'movies',
			'f=added':'added:7d'
		}
	}

	page = soup_part['href'].rsplit('p=',1)[1]
	if query and query != 'added:7d':
		q = "f={0}".format(query)
		options[q] = query
	for option in options:
		if option in soup_part['href']:
			if options[option] == '/recent':
				link = '/recent/'+page
			elif q and option is q:
				link = '/search/'+options[option]+'/'+page
			else:
				for optiontwo in options['nested']:
					if optiontwo in soup_part['href']:
						link = options[option]+'/'+options['nested'][optiontwo]+'/'+page
	return link

class TagCloudLink(object):
	def __init__(self):
		self.url = None
		self.name = None
		self.font_size = None

class Link(object):
	def __init__(self):
		self.url = None
		self.mirror = None

class Torrent(object):
	def __init__(self):
		self.url = None
		self.torrenthash = None
		self.title = None
		self.mb = None
		self.leechers = None
		self.seeds = None
		self.date = None