from constant import *
import pymysql, os, codecs, datetime

stat_item = ('Download', 'Rating', 'Rating_Num', 'Metadata_Version', 'Update_Time', 'MD5_SHA256')

if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	result = []
	for package in package_list:
		package_result = []
		md5_sha256_list = []
		for market in market_list:
			ifexists = cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_market_result = {
					'Download': None,
					'Rating': None,
					'Rating_Num': None,
					'Metadata_Version': None,
					'Update_Time': None,
					'MD5_SHA256': None
				}
				package_result.append(package_market_result)
				print("Not Found "+package+" In "+market_name[market])
			else:
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select Downloads, Avg_rating, Total_rating from Market_Time_Metadata where Package_Name = '"+package+"' and MarketID="+str(market)+" and Time = (select max(Time) from Market_Time_Metadata where Package_Name = '"+package+"' and MarketID="+str(market)+")")
				time_metadata = cursor.fetchall()[0]
				cursor.execute("select Version, UpTime, MD5, SHA256 from Market_APK_Metadata where ID="+str(apk_id))
				apk_metadata = cursor.fetchall()[0]
				package_market_result = {
					'Download': time_metadata[0],
					'Rating': time_metadata[1],
					'Rating_Num': time_metadata[2],
					'Metadata_Version': apk_metadata[0],
					'Update_Time': None,
					'MD5_SHA256': None
				}
				if apk_metadata[1] != None:
					package_market_result['Update_Time'] = datetime.datetime.fromtimestamp(float(apk_metadata[1])).strftime('%Y-%m-%d %H:%M:%S')[:10]
				md5_sha256 = apk_metadata[2]+'-'+apk_metadata[3]
				if not md5_sha256 in md5_sha256_list: md5_sha256_list.append(md5_sha256)
				package_market_result['MD5_SHA256'] = md5_sha256_list.index(md5_sha256)
				package_result.append(package_market_result)
				print("Finish "+package+" In "+market_name[market])
		result.append(package_result)
	cursor.close()
	conn.close()
	for item in stat_item:
		fout = open(item+"_Statistics.csv", "w")
		for j in range(len(market_list)):
			fout.write(','+market_name[market_list[j]])
		fout.write("\n")
		for i in range(len(package_list)):
			fout.write(package_list[i])
			for j in range(len(market_list)):
				if result[i][j][item] == None:
					fout.write(",")
				else:
					fout.write(","+str(result[i][j][item]))
			fout.write("\n")
		fout.close()
		print("Finish "+item+" Stat")
