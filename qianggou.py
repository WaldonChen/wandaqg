#/usr/bin/env python
# -*- coding: utf-8 -*-

import os, logging, urllib
import httplib2
import lxml

from lxml import html
from forms.loginform import GetVerifycode

# Create logger with 'WandaQG'
logger = logging.getLogger(name = 'WandaQG')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug message
fh = logging.FileHandler('wandaqg.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

## URLs
host_url = 'http://app.wandafilm.com'
login_url = 'http://app.wandafilm.com/wandaFilm/login.action'
get_verifycode_image_url = 'http://app.wandafilm.com/wandaFilm/verifyCodeServlet?uuid='
query_city_url = 'http://app.wandafilm.com/wandaFilm/doqueryCitys.action?userId='

## Files used in QiangGou
FILE_HTTP_CACHE = '.cache'
FILE_VERIFY_CODE_IMG = '.verifycode.jpg'

user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'

class QiangGou:
	def __init__(self, city):
		self._logger = logging.getLogger('WandaQG.QiangGou')
		self._http = httplib2.Http(FILE_HTTP_CACHE)
		self._city = city

	def goto_login_page(self):
		cookie = 'JSESSIONID=E94CC014054C82D5DE11FE9473CD1072'
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'User-Agent': user_agent,
				# 'Cookie': cookie
				}
		response, content = self._http.request(login_url, 'GET',
												headers = headers)
		if response['status'] != '200':
			self._logger.error('goto_login_page(): load login page failure...')
			return False
		# self._logger.info("Response: " + str(response))
		self._cookies = response['set-cookie']
		tree = lxml.html.fromstring(content)
		uuids = tree.xpath("//input[@id='uuid']/@value")
		if len(uuids) > 0:
			self._uuid = uuids[0]
			self._logger.info("Get UUID: " + self._uuid)
			return True
		self._logger.warn("Can not get UUID!")
		return False

	def get_verifycode_image(self):
		url = get_verifycode_image_url + self._uuid
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cookie': self._cookies,
				'User-Agent': user_agent }
		response, content = self._http.request(url, 'GET',
												headers = headers)
		if response['status'] != '200':
			self._logger.error('get_verifycode_image(): '
								+ 'load verify code image failure...')
			return False
		# self._logger.info("Response: " + str(response))
		verify_imgfile = open(FILE_VERIFY_CODE_IMG, 'w')
		verify_imgfile.write(content)
		verify_imgfile.close()
		self._verifycode = GetVerifycode(FILE_VERIFY_CODE_IMG)
		return True

	def login(self):
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cache-Control': 'max-age=0',
				'Content-Type': 'application/x-www-form-urlencoded',
				'User-Agent': user_agent }
		body = {'userName': 'cjshappy@163.com',
				'userPass': 'harrypotter',
				'uuid': self._uuid,
				'verifyCode': self._verifycode }
		response, content = self._http.request(login_url, 'POST',
												headers = headers,
												body = urllib.urlencode(body))
		if response['status'] != '200':
			self._logger.error('login(): '
								+ 'login request failure...')
			return False
		# self._logger.info("Response: " + str(response))
		tree = lxml.html.fromstring(content)
		userIds = tree.xpath("//input[@id='userId']/@value")
		if len(userIds) > 0:
			self._userId = userIds[0]
			self._cookies = response['set-cookie']
			self._logger.info("Login Success! Get userid: " + self._userId)
			return True
		else:
			self._logger.error("Can not get userid in html, login failed!")
			return False

	def query_city(self):
		query_url = query_city_url + self._userId
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cookie': self._cookies,
				'User-Agent': user_agent }
		response, content = self._http.request(query_url, 'GET',
												headers = headers)
		if response['status'] != '200':
			self._logger.error('query_city(): '
								+ 'query_city request failure...')
			return False
		# self._logger.info("Response: " + str(response))
		tree = lxml.html.fromstring(content)
		cities = tree.xpath("//a[@class='city']")
		if len(cities) > 0:
			for item in cities:
				if item.text == self._city:
					self._ticketUrl = host_url + item.attrib['href']
					self._logger.info("Get rush buy url: " + self._ticketUrl)
					return True
		self._logger.error("Do not get the rush-buy url!")
		return False

	def qianggou(self):
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cookie': self._cookies,
				'User-Agent': user_agent }
		response, content = self._http.request(self._ticketUrl, 'GET',
												headers = headers)
		if response['status'] != '200':
			self._logger.error('qianggou(): '
								+ 'qiang gou failure...')
			return False
		# self._logger.info("Response: " + str(response))
		tree = lxml.html.fromstring(content)
		result = tree.xpath("//section/p/strong/span")
		if len(result) > 0:
			for item in result:
				self._logger.info(item.text)
				print item.text

if __name__ == '__main__':
	qg = QiangGou('合肥')
	qg.goto_login_page()
	qg.get_verifycode_image()
	if qg.login():
		print "Login success......"
	else:
		print "Login failure......"
	if qg.query_city():
		qg.qianggou()
