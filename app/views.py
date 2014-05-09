from app import app, render_template
import os
import requests
from BeautifulSoup import BeautifulSoup

@app.route('/')
@app.route('/list/<peer_seeds>/<tv_movies>')
def listBy(peer_seeds=None, tv_movies=None):
	if peer_seeds and tv_movies:
		return render_template("list.html", 
			urls=listTorrents(peer_seeds,tv_movies, None), 
			title=getPageTitle(peer_seeds, tv_movies, None)
		)
	return render_template("list.html", 
		urls=listTorrents('P', 'tv', None), 
		title=getPageTitle('P', 'tv', None)
	)

@app.route('/recent')
def recent():
	return render_template("list.html", 
		urls=listTorrents(None, None, 'added:7d'), 
		title=getPageTitle(None, None, 'added:7d')
	)

@app.route('/magnet/<url>')
def magnet(url):
	return render_template("magnet.html", 
		link=downloadTorrent(url),
		title='Download'
	)

@app.route('/search/<query>')
def search(query):
	return render_template("list.html", 
		urls=listTorrents(None, None, query), 
		title=getPageTitle(None, None, query)
	)

@app.route('/cloud')
def cloud():
	return render_template("cloud.html",
		urls=getTagCloud(),
		title='Tag Cloud'
	)

def getPageTitle(peer_seeds=None, tv_movies=None, query=None):
	options = {
	'N':{'tv':'TV sorted by Rating','movies':'Movies sorted by Rating'},
	'D':{'tv':'TV sorted by Date','movies':'Movies sorted by Date'},
	'S':{'tv':'TV sorted by Size','movies':'Movies sorted by Size'},
	'P':{'tv':'TV sorted by Peers','movies':'Movies sorted by Peers'}
	}
	if peer_seeds and tv_movies:
		return options[peer_seeds][tv_movies]
	elif query != 'added:7d': return 'Search results for %s' % query
	elif query == 'added:7d': return 'Last week\'s favorites'
	else: return 'Torrents'

def listTorrents(peer_seeds=None, tv_movies=None, query=None):
	if peer_seeds and tv_movies:
		r = requests.get('http://torrentz.eu/verified'+peer_seeds+'?f='+tv_movies)
	elif query:
		r = requests.get('http://torrentz.eu/search?f='+query)
	else: return
	soup = BeautifulSoup(r.text)
	dt = soup.findAll('a', attrs={'title':None, 'rel':None})
	urllist = []
	for x in dt:
		if len(x['href']) > 40: 
			tor = Torrent()
			tor.url = 'http://torrentz.eu'
			tor.torrenthash = x['href']
			tor.title = x.text
			urllist.append(tor)
	return urllist

def downloadTorrent(h):
	r = requests.get('http://torrentz.eu/'+h)
	soup = BeautifulSoup(r.text)
	dt = soup.findAll('a', attrs={'rel':'e'})
	for x in dt:
		if '1337x' in x['href']:
			magnet = extractMagnet('1337x',x['href'])
			if magnet and magnet['href']:
				link = Link()
				link.url = magnet['href']
				link.mirror = '1337x.to'
				return link
		if 'kickass' in x['href']:
			magnet = extractMagnet('kickass',x['href'])
			if magnet and magnet['href']:
				link = Link()
				link.url = magnet['href']
				link.mirror = 'kickass.to'
				return link
		if 'katproxy' in x['href']:
			magnet = extractMagnet('kickass',x['href'])
			if magnet and magnet['href']:
				link = Link()
				link.url = magnet['href']
				link.mirror = 'katproxy.com'
				return link
	return None

def extractMagnet(site,x):
	if site == '1337x':
		r = requests.get(x)
		soup = BeautifulSoup(r.text)
		magnet = soup.find('a', attrs={'class':'magnetDw'})
		return magnet
	if site == 'kickass' or site == 'katproxy':
		r = requests.get(x)
		soup = BeautifulSoup(r.text)
		magnet = soup.find('a', attrs={'class':'magnetlinkButton'})
		return magnet

def getTagCloud():
	r = requests.get('http://torrentz.eu/i')
	soup = BeautifulSoup(r.text)
	dt = soup.findAll('div',attrs={'class':'cloud'})
	urllist = []
	for div in dt:
		links = div.findAll('a')
		for link in links:
			lnk = TagCloudLink()
			lnk.url = link['href'].rsplit('/',1)[1]
			lnk.name = link.text
			lnk.font_size = link['style']
			urllist.append(lnk)
	return urllist

class TagCloudLink(object):
	def __init__(self,url=None, name=None, font_size=None):
		if url:
			self.url = url
		if name:
			self.name = name
		if font_size:
			self.font_size = font_size

class Link(object):
	def __init__(self,url=None, mirror=None):
		if url:
			self.url = url
		if mirror:
			self.mirror = mirror

class Torrent(object):
	def __init__(self,url=None, torrenthash=None, title=None):
		if url:
			self.url = url
		if torrenthash:
			self.torrenthash = torrenthash
		if title:
			self.title = title