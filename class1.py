
from flask import Flask
from flask.ext.classy import FlaskView
#from random import choice
from os import walk, path
import dominate
from dominate.tags import *
import time
import operator
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)


app = Flask(__name__)

#here's how we need to seperate things:
class Page(object):
	def __init__(self):
		self.paged = None
		self.route = None

	def new(self, route = '/',
				 title = 'Classy Domination',
				 css = 'static/css', js = 'static/js'):
		page = dominate.document(title)
		with page.head:
			for  i in walk(css):
				link(rel='stylesheet', href='/%s/%s' % (css,i[2][0]))
			for i in walk(js): 
				script(type="text/javascript", src='/%s/%s' % (js,i[2][0]))
		self.paged = page
		self.route = route
		return self

	def build(self, page, fst = None):
		pp.pprint(page)
		if fst is None:
			fst = 0
		if str(type(page)) == '<type \'dict\'>':
			for a, b  in page.items():
				for t in self.build(b,0):
					a += t
				if fst == 1:
					self.paged += a
				else:
					return a
		elif str(type(page)) == '<type \'list\'>':
			ret = []
			for i in page:
				ret.append(self.build(i,0))
			return ret
		else:
			return [page]



class Blog(object):
#	has private methods for interacting with the models
#	as well as the structure of all of the bits used
	route = 'blogroll'
	def __init__(self):
		self.blogs = None
		self.menu_items = None

	def new(self):
		blog_file = 'blogs'
		blogs = {}
		files = list(walk(blog_file))[0][2]
		for fn in files:
			loc = '%s/%s' % (blog_file, fn)
			with open(loc, 'rb') as f:
				cc = f.readlines()
			blogs[''.join(fn.split('.')[:-1])] = {
				'header': ''.join(fn.split('.')[:-1]),
				'content': cc,
				'time': time.ctime(path.getctime(loc))
			}
		self.blogs = blogs
		self.menu_items = [
			'newest',
			'random',
			'about',
			'list',
			'submit'
		]

	def get_blog(self,title):
		return self.blogs[title]

	def get_blogs(self):
		return self.blogs

	def menu(self, items = None):
		return [a(item.title(), href = '/%s/%s' % (self.route,item)) for item in items or self.menu_items]

	def section(self, plain_text):
		stuff = plain_text.split('\n')
		rr = div(h1(stuff[0]))
		rr.add(stuff[1:])
		return {div(id=stuff[0]): rr}

	def sections(self, plain_blog):
		return [self.section(i) for i in plain_blog]


class BlogRollView(FlaskView):
	def _page(self, contentin, headerin, menuin):
		container = div(id='container')
		content =div(id='content')
		main = div(id='main')
		menu=div(id='menu')
		header =  div(id='header')	
		rets = {container: {
				header: h1(headerin),
				content: {
					menu: menuin,
					main: contentin
				}
			}	}
		return dict([(div(id='container'), 
					dict([
						(div(id='header'),h1(headerin)),
						(div(id='main'), dict([
							(div(id='menu'), menuin),
							(div(id='content'), contentin)
							]))
					]))
				])
		cc = dict(menu = menuin, main = contentin)
		cont = dict(header=h1(headerin), content = cc)
		return ret

	def newest(self):
		blog = Blog()
		blog.new()
		new = sorted(blog.get_blogs().iteritems(), key = lambda x: x[1]['time'])[::-1][0][1]
		content = blog.sections(new['content'])
		menu = blog.menu()
		header = new['header']
		page = self._page(content, header, menu)
		ret = Page()
		ret.new()
		ret.build(page, 1)
		print ret.paged
		return str(ret.paged)

BlogRollView.register(app)

if __name__ == '__main__':
	app.debug = True
	app.run()


if __name__ == '__maiedvn__':
	g = Page(route = '/blog', title = 'test')
	stuff = {div(id = 'testdiv'): [b('poop'),p('flib')],
			 div(id = 'secondtest') : {
			 	div(id='inner'):[b('helllooo'),b('goodvye'),'flib<br/>']
			 	}
			 }
	g.build(stuff, 1)
	print g.page
