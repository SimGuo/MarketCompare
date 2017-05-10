import pymysql, os, json, codecs

market_id_dict = {
	'googleplay': '0',
	'yingyongbao': '2',
	'baidu': '3',
	'360': '4',
	'huawei': '5',
	'xiaomi': '6',
	'wandoujia': '7',
	'hiapk': '8',
	'anzhi': '9',
	'91': '10',
	'oppo': '11',
	'pp': '12',
	'sogou': '13',
	'gfan': '14',
	'meizu': '15',
	'dcn': '17',
	'liqucn': '18',
	'appchina': '19',
	'10086': '20',
	'lenovo': '21',
	'zol': '22',
	'nduo': '23',
	'cnmo': '24',
	'pconline': '25',
	'appcool': '26'
}

def read_config():
	result = {}
	result['MYSQL_HOST'] = ""
	result['MYSQL_PORT'] = "3306"
	result['MYSQL_USER'] = ""
	result['MYSQL_PASSWORD'] = ""
	result['MYSQL_DB'] = ""
	result['MYSQL_CHARSET'] = "utf8"
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

def connect_mysql(config):
	try:
		conn = pymysql.connect(host=config['MYSQL_HOST'], port=int(config['MYSQL_PORT']), user=config['MYSQL_USER'], password=config['MYSQL_PASSWORD'], db=config['MYSQL_DB'], charset=config['MYSQL_CHARSET'])
		return conn
	except:
		print ("数据库连接失败 - "+time.asctime(time.localtime(time.time())))
		time.sleep(10)
		return None

if __name__ == '__main__':
	config = read_config()
	conn = connect_mysql(config)
	cursor = conn.cursor()
	fin = open('Download_List.txt', 'r')
	for line in fin:
		pkg = line.split(' ')[0]
		mkt = line.split(' ')[1]
		timestr = line.split(' ')[2]
		md5 = line.split(' ')[3]
		sha256 = line.split(' ')[4].replace('\n', "")
		if not os.path.isdir('Metadata/'+pkg):
			os.makedirs('Metadata/'+pkg)
		if not os.path.isdir('Metadata/'+pkg+'/'+mkt+'['+timestr+']'):
			os.makedirs('Metadata/'+pkg+'/'+mkt+'['+timestr+']')
		metadata = {}
		description = ""
		release_note = ""
		cursor.execute("select App_Name, Developer from Market_APP_Metadata where Package_Name = '"+pkg+"' and MarketID = "+str(market_id_dict[mkt]))
		data = cursor.fetchall()[0]
		if data[0] != None: metadata['Name'] = data[0]
		if data[1] != None: metadata['Developer'] = data[1]
		cursor.execute("select Version, Category, Tag, Description, UpTime, ReleaseNote from Market_APK_Metadata where Package_Name = '"+pkg+"' and MarketID = "+str(market_id_dict[mkt])+" and MD5 = '"+md5+"' and SHA256 = '"+sha256+"'")
		data = cursor.fetchall()[0]
		if data[0] != None: metadata['Version'] = data[0]
		if data[1] != None: metadata['Category'] = data[1]
		if data[2] != None: metadata['Tag'] = data[2]
		if data[3] != None: description = data[3]
		if data[4] != None: metadata['Update_Time'] = data[4]
		if data[5] != None: release_note = data[5]
		cursor.execute("select Avg_rating, Downloads, Total_rating, Stars from Market_Time_Metadata where Package_Name = '"+pkg+"' and MarketID = "+str(market_id_dict[mkt])+" and Time = '"+timestr+"'")
		data = cursor.fetchall()[0]
		if data[0] != None: metadata['Rating'] = data[0]
		if data[1] != None: metadata['Downloads'] = data[1]
		if data[2] != None: metadata['Rating_Num'] = data[2]
		if data[3] != None: metadata['Stars'] = data[3]
		json.dump(metadata, codecs.open('Metadata/'+pkg+'/'+mkt+'['+timestr+']/Metadata.json', 'w', 'utf-8'))
		if len(description):
			open('Metadata/'+pkg+'/'+mkt+'['+timestr+']/Description.txt', 'w').write(description)
		if len(release_note):
			open('Metadata/'+pkg+'/'+mkt+'['+timestr+']/Release_Note.txt', 'w').write(release_note)
		print (line)
