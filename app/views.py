from app import app, render_template
import os
import requests
from BeautifulSoup import BeautifulSoup

@app.route('/')
@app.route('/list/<peer_seeds>/<tv_movies>')
def listBy(peer_seeds=None, tv_movies=None):
	if peer_seeds and tv_movies:
		return render_template("list.html", urls=listTorrents(peer_seeds,tv_movies))
	return render_template("index.html")

@app.route('/magnet/<url>')
def magnet(url):
	return render_template("magnet.html", url=downloadTorrent(url))

def listTorrents(sort,media):
	r = requests.get('http://torrentz.eu/verified'+sort+'?f='+media)
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
			magnet = extractMagnet(x['href'])
			if magnet: 
				return magnet['href']
		# TODO:
		# support more mirrors..

def extractMagnet(x):
	r = requests.get(x)
	soup = BeautifulSoup(r.text)
	magnet = soup.find('a', attrs={'class':'magnetDw'})
	return magnet

class Torrent(object):
	def __init__(self,url=None,torrenthash=None,title=None):
		if url:
			self.url = url
		if torrenthash:
			self.torrenthash = torrenthash
		if title:
			self.title = title