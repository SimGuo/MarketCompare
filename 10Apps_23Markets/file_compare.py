from constant import *
import pymysql, os, glob, hashlib

def get_dex_sha256(dexfile):
	try:
		myhash = hashlib.sha256()
		f = open(dexfile, 'rb')
		while True:
			b = f.read(8096)
			if not b :
				break
			myhash.update(b)
		f.close()
		return myhash.hexdigest()
	except:
		return ""

if __name__ == "__main__":
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android_10app', charset='utf8')
	cursor = conn.cursor()
	result = []
	for package in package_list:
		package_result = []
		rsa_result = []
		dex_result = []
		for i in range(len(market_list)):
			market = market_list[i]
			package_market_result = [None, None]
			ifexists = cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_result.append([None, None])
				print ('Not Found '+package+' In '+market_name[market_list[i]])
			else:
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select MD5, SHA256 from Market_APK_Metadata where ID="+str(apk_id))
				info = cursor.fetchall()[0]
				md5 = info[0]
				sha256 = info[1]
				lst = glob.glob(root+market_dir[market_list[i]]+"/"+package+'/{'+md5+'-'+sha256+'}/META-INF/*.RSA')
				if len(lst) != 1:
					print ('Not Found the Only RSA of '+package+' In '+market_name[market_list[i]])
				else:
					rsa = os.popen('keytool -printcert -file '+lst[0]).read()
					if not rsa in rsa_result:
						rsa_result.append(rsa)
					package_market_result[0] = rsa_result.index(rsa)
				lst = glob.glob(root+market_dir[market_list[i]]+"/"+package+'/{'+md5+'-'+sha256+'}/*.dex')
				dex = set()
				for dexfile in lst:
					dex.add(get_dex_sha256(dexfile))
				if not dex in dex_result:
					dex_result.append(dex)
				package_market_result[1] = dex_result.index(dex)
				package_result.append(package_market_result)
				print ('Finish '+package+' In '+market_name[market_list[i]])
		result.append(package_result)
	cursor.close()
	conn.close()
	fout = open("RSA_Statistics.csv", "w")
	for j in range(len(market_list)):
		fout.write(','+market_name[market_list[j]])
	fout.write("\n")
	for i in range(len(package_list)):
		fout.write(package_list[i])
		for j in range(len(market_list)):
			if result[i][j][0] == None:
				fout.write(",")
			else:
				fout.write(","+str(result[i][j][0]))
		fout.write("\n")
	fout.close()
	fout = open("DEX_Statistics.csv", "w")
	for j in range(len(market_list)):
		fout.write(','+market_name[market_list[j]])
	fout.write("\n")
	for i in range(len(package_list)):
		fout.write(package_list[i])
		for j in range(len(market_list)):
			if result[i][j][1] == None:
				fout.write(",")
			else:
				fout.write(","+str(result[i][j][1]))
		fout.write("\n")
	fout.close()