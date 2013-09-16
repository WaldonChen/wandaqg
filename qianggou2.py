# -*- coding: utf-8 -*-
import os, logging
import httplib2, urllib, lxml

from lxml import html
from forms.loginform import GetVerifycode

# Create logger with 'WandaQG'
logger = logging.getLogger(name = 'WandaQG')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug message
fh = logging.FileHandler('wandaqg.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
LOG_LVL_PROMPT = logging.CRITICAL + 10
logging.addLevelName(LOG_LVL_PROMPT, 'PROMPT')
ch.setLevel(LOG_LVL_PROMPT)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

host_url = 'http://app.wandafilm.com'
login_url = 'http://app.wandafilm.com/wandaFilm/login.action'
start_url = 'http://app.wandafilm.com/wandaFilm/start.action'
verifycode_image_url = 'http://app.wandafilm.com/wandaFilm/verifyCodeServlet?uuid='
query_city_url = 'http://app.wandafilm.com/wandaFilm/doqueryCitys.action?userId='

user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'

## Files used in QiangGou
FILE_VERIFY_CODE_IMG = '.verifycode.jpg'

class WandaQG:

	def __init__(self, username, password, user_id, city = '合肥'):
		self.__username = username
		self.__password = password
		self.__userId = user_id
		self.__city = city
		self.__cookie = ''
		self.__query_city_fail_time = 0
		self.__http = httplib2.Http('.cache')
		self.__logger = logging.getLogger('WandaQG')

	def __get_uuid(self):
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'User-Agent': user_agent,
				}
		response, content = self.__http.request(login_url, 'GET',
												headers = headers)
		if response['status'] != '200':
			return None

		self._cookies = response['set-cookie']
		if response['content-location'] != login_url:
			return None
		tree = lxml.html.fromstring(content)
		uuids = tree.xpath("//input[@id='uuid']/@value")
		if len(uuids) > 0:
			uuid = uuids[0]
			if len(uuid) == 36:
				return uuid
			else:
				return None
		return None

	def __get_verifycode(self):
		uuid = self.__get_uuid()
		if uuid is None:
			return None
		url = verifycode_image_url + uuid
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cookie': self.__cookie,
				'User-Agent': user_agent }
		response, content = self.__http.request(url, 'GET',
												headers = headers)
		if response['status'] != '200':
			self._logger.error('get_verifycode_image(): '
								+ 'load verify code image failure...')
			return False
		verify_imgfile = open(FILE_VERIFY_CODE_IMG, 'w')
		verify_imgfile.write(content)
		verify_imgfile.close()
		verifycode = GetVerifycode(FILE_VERIFY_CODE_IMG)
		if len(verifycode) != 4:
			return None
		return verifycode, uuid

	def __login(self):
		verifycode, uuid = self.__get_verifycode()
		if verifycode is None:
			return False
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'Cache-Control': 'max-age=0',
				'Content-Type': 'application/x-www-form-urlencoded',
				'User-Agent': user_agent }
		body = {'userName': self.__username,
				'userPass': self.__password,
				'uuid': uuid,
				'verifyCode': verifycode }
		response, content = self.__http.request(login_url, 'POST',
												headers = headers,
												body = urllib.urlencode(body))
		if response['status'] != '200':
			return False

		if 'content-location' not in response.keys():
			return False

		if response['content-location'] == start_url:
			if 'set-cookie' in response.keys():
				self.__cookie = response['set-cookie']
			return True
		else:
			return False

	def login(self):
		i = 0
		max_req_times = 5
		while i < max_req_times:
			if self.__login():
				return True;
		return False

	def get_qg_url(self):
		'''Returns qg_url, next operation
		0 : Success, 1 : request again, 2 : need login
		'''
		query_url = query_city_url + self.__userId
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
					'Connection': 'keep-alive',
					'User-Agent': user_agent }
		response, content = self.__http.request(query_url, 'GET',
												headers = headers)
		if response['status'] != '200':
			print 'query_city(): ' + 'query_city request failure...'
			return None, 1

		# self._logger.info("Response: " + str(response))
		if response['content-location'] == login_url:
			return None, 2

		if response['content-location'] != query_url:
			return None, 1

		if 'set-cookie' in response.keys():
			self.__cookie = response['set-cookie']
		tree = lxml.html.fromstring(content)
		cities = tree.xpath("//a[@class='city']")
		if len(cities) > 0:
			for item in cities:
				if item.text == self.__city:
					qg_url = host_url + item.attrib['href']
					# self._logger.info("Get rush buy url: " + self._ticketUrl)
					return qg_url, 0
		# self._logger.error("Do not get the rush-buy url!")
		return None, 1

	def rush(self, url):
		'''Return Result, next operation
		1 : request again, 2 : stop
		'''
		headers = {'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
				'Connection': 'keep-alive',
				'User-Agent': user_agent }
		if len(self.__cookie) != 0:
			headers['Cookie'] = self.__cookie
		response, content = self.__http.request(url, 'GET',
												headers = headers)
		if response['status'] != '200':
			# self._logger.error('qianggou(): '
			#					+ 'qiang gou failure...')
			return False, 1

		if response['content-location'] == start_url:
			return False, 1

		if response['content-location'] == url:
			# self._logger.info("Response" + str(response))
			# self._logger.info("Content: " + content)
			tree = lxml.html.fromstring(content)
			result = tree.xpath("//section/p/strong/span")
			if len(result) > 0:
				for item in result:
					# self._logger.info(item.text)
					print item.text
					return False, 2
		else:
			return False, 1

	def qianggou(self):
		i = 0
		max_req_times = 10
		while i < max_req_times:
			qg_url, next_op = self.get_qg_url()
			if qg_url:
				result, next_op2 = self.rush(qg_url)
				if next_op2 == 1:
					continue
				elif next_op2 == 2:
					break
			if next_op == 1:
				continue
			if next_op == 2:
				if not self.login():
					break
		if i == max_req_times:
			self.__logger.log(LOG_LVL_PROMPT, '超过最大请求次数: %d' % max_req_times)

if __name__ == '__main__':
	httplib2.debuglevel = 4
	qg = WandaQG('cjshappy@163.com', 'harrypotter', '20121108183437971694')
	qg.qianggou()
