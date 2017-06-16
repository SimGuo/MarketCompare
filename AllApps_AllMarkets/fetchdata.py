import codecs, pymysql, json, os

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

config = read_config()
conn = pymysql.connect(host=config['MYSQL_HOST'], port=int(config['MYSQL_PORT']), user=config['MYSQL_USER'], password=config['MYSQL_PASSWORD'], db=config['MYSQL_DB'], charset=config['MYSQL_CHARSET'])
cursor = conn.cursor()

cursor.execute("select Package_Name,MarketID from Market_APP_Metadata where MarketID <> 1 and MarketID<>16")
data = cursor.fetchall()
with codecs.open('data.txt', 'w', 'utf-8') as fout:
	for pkg in data:
		ifexists = cursor.execute("select Downloads, Avg_rating, Total_rating from Market_Time_Metadata where Package_Name='"+pkg[0]+"' and MarketID="+str(pkg[1])+" and Time = (select max(Time) from Market_Time_Metadata where Package_Name='"+pkg[0]+"' and MarketID="+str(pkg[1])+")")
		if ifexists > 0:
			r = cursor.fetchall()[0]
			s = ["None", "None", "None"]
			for i in range(3):
				if r[i] != None: s[i] = str(r[i])
			fout.write(pkg[0]+'\t'+str(pkg[1])+'\t'+str(s[0])+'\t'+str(s[1])+'\t'+str(s[2])+'\n')	

cursor.close()
conn.close()
