import os, json, logging

config_logger = logging.getLogger('WandaQG.config')

accounts_file = 'accounts.json'

def add_account(account):
	try:
		accounts = json.loads(open(accounts_file, 'r').read())
	except (IOError, ValueError), e:
		config_logger.warn(str(e))
		accounts = []
	acc = {'username': account['username'],
			'password': account['password'],
			'city': account['city']
		}
	for item in accounts:
		if item['username'] == acc['username']:
			config_logger.warn("Account '" + acc['username']
						+ "' already exist!")
			return False
	accounts.append(acc)
	try:
		if os.path.exists(accounts_file) and os.path.isfile(accounts_file):
			os.remove(accounts_file)
		f2 = open(accounts_file, 'w')
	except IOError, e:
		config_logger.warn(str(e))
		return False
	f2.write(json.dumps(accounts))
	f2.close()
	return True

if __name__ == '__main__':
	fh = logging.FileHandler('config.log')
	fh.setLevel(logging.DEBUG)
	config_logger.addHandler(fh)
	add_account({'username': 'adc', 'password': 'sdf', 'city': 's3'})
