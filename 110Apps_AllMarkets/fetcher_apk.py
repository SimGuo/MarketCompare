import oss2, os, shutil, json, hashlib, time

def read_config():
	result = {}
	result['ACCESS_KEY_ID'] = None
	result['ACCESS_KEY_SECRET'] = None
	result['ENDPOINT'] = None
	try:
		if os.path.isfile("config.json"):
			with open("config.json") as jsonfile:
				config_dict = json.load(jsonfile)
			for key in result.keys():
				if key in config_dict:
					result[key] = config_dict[key]
			return result
		else:
			return None
	except:
		return None

def get_apk_md5(apkfile):
	try:
		myhash = hashlib.md5()
		f = open(apkfile, 'rb')
		while True:
			b = f.read(8096)
			if not b :
				break
			myhash.update(b)
		f.close()
		return myhash.hexdigest()
	except:
		return ""
		
def get_apk_sha256(apkfile):
	try:
		myhash = hashlib.sha256()
		f = open(apkfile, 'rb')
		while True:
			b = f.read(8096)
			if not b :
				break
			myhash.update(b)
		f.close()
		return myhash.hexdigest()
	except:
		return ""

if __name__ == '__main__':
	config = read_config()
	pkg_list = []
	pkg_md5_mkt = {}
	fin = open('Download_List.txt', 'r')
	for line in fin:
		pkg = line.split(' ')[0]
		mkt = line.split(' ')[1]
		md5 = line.split(' ')[3]
		sha256 = line.split(' ')[4].replace('\n', "")
		if not os.path.exists('Apps/'+pkg):
			os.makedirs('Apps/'+pkg)
		if not pkg in pkg_md5_mkt:
			pkg_md5_mkt[pkg] = {}
			pkg_list.append(pkg)
		if not md5+'-'+sha256 in pkg_md5_mkt[pkg]:
			pkg_md5_mkt[pkg][md5+'-'+sha256] = []
		pkg_md5_mkt[pkg][md5+'-'+sha256].append(mkt)
	root = '/StorageSrv/'
	key_id = config['ACCESS_KEY_ID']
	key_secret = config['ACCESS_KEY_SECRET']
	endpoint = config['ENDPOINT']
	for pkg in pkg_list:
		for key, val in pkg_md5_mkt[pkg].items():
			md5 = key.split('-')[0]
			sha256 = key.split('-')[1]
			success_copy = False
			for mkt in val:
				if os.path.isfile(root+mkt+"/"+pkg+"/{"+key+"}/"+pkg+'.apk'):
					try:
						shutil.copyfile(root+mkt+"/"+pkg+"/{"+key+"}/"+pkg+'.apk', 'Apps/'+pkg+'/'+key+'.apk')
						if get_apk_md5('Apps/'+pkg+'/'+key+'.apk') == md5 and get_apk_sha256('Apps/'+pkg+'/'+key+'.apk') == sha256:
							success_copy = True
							print ('Copy From Local: '+pkg+' '+key)
							break
						elif os.path.isfile('Apps/'+pkg+'/'+key+'.apk'):
							os.remove('Apps/'+pkg+'/'+key+'.apk')
					except:
						pass
			if not success_copy:
				for mkt in val:
					if success_copy:
						break
					for i in range(1000):
						try:
							auth = oss2.Auth(key_id, key_secret)
							bucket = oss2.Bucket(auth, endpoint, 'lxapk')
							r = bucket.get_object_to_file(mkt+'/'+pkg+'/'+key+".apk", 'Apps/'+pkg+'/'+key+'.apk')
							if r.status == 200 and get_apk_md5('Apps/'+pkg+'/'+key+'.apk') == md5 and get_apk_sha256('Apps/'+pkg+'/'+key+'.apk') == sha256:
								success_copy = True
								print ('Download From OSS: '+pkg+' '+key)
								break
						except:
							pass
						time.sleep(5)
			if not success_copy:
				print ('Failed: '+pkg+' '+key)
