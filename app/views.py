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
		urls=listTorrents(None, None, 'added:7d'), 
		title=getPageTitle(None, None, 'added:7d')
	)

@app.route('/magnet/<url>')
def magnet(url):
	return render_template("magnet.html", url=downloadTorrent(url))

@app.route('/search/<query>')
def search(query):
	return render_template("list.html", 
		urls=listTorrents(None, None, query), 
		title=getPageTitle(None, None, query)
	)

def getPageTitle(peer_seeds=None, tv_movies=None, query=None):
	if peer_seeds and tv_movies:
		if peer_seeds == 'N':
			if tv_movies == 'tv': return 'TV sorted by Rating'
			else: return 'Movies sorted by Rating'
		elif peer_seeds == 'D':
			if tv_movies == 'tv': return 'TV sorted by Date'
			else: return 'Movies sorted by Date'
		elif peer_seeds == 'S':
			if tv_movies == 'tv': return 'TV sorted by Size'
			else: return 'Movies sorted by Size'
		elif peer_seeds == 'P':
			if tv_movies == 'tv': return 'TV sorted by Peers'
			else: return 'Movies sorted by Peers'
	elif query != 'added:7d': return 'Search results for %s' % query
	elif query == 'added:7d': return '	Last week\'s favorites'
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
			if magnet and magnet['href']: return magnet['href']		
		if 'kickass' in x['href']:
			magnet = extractMagnet('kickass',x['href'])
			if magnet and magnet['href']: return magnet['href']
		if 'katproxy' in x['href']:
			magnet = extractMagnet('kickass',x['href'])
			if magnet and magnet['href']: return magnet['href']
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

class Torrent(object):
	def __init__(self,url=None, torrenthash=None, title=None):
		if url:
			self.url = url
		if torrenthash:
			self.torrenthash = torrenthash
		if title:
			self.title = title