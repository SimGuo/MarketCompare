import pymysql, os, codecs, datetime

package_list = (
	'cn.com.sina.finance',
	'com.baidu.BaiduMap',
	'com.fenbi.android.gaozhong',
	'com.moji.mjweather',
	'com.mt.mtxx.mtxx',
	'com.taobao.ju.android',
	'com.tencent.pb',
	'com.umetrip.android.msky.app',
	'com.yibasan.lizhifm',
	'com.yixia.xiaokaxiu'
)

market_list = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24)

market_name = {
	0: 'Google Play',
	2: '应用宝',
	3: '百度手机助手',
	4: '360手机助手',
	5: '华为应用市场',
	6: '小米应用商店',
	7: '豌豆荚',
	8: '安卓市场',
	9: '安智市场',
	10: '91应用中心',
	11: 'OPPO软件商店',
	12: 'PP助手',
	13: '搜狗手机助手',
	14: '机锋网',
	15: '魅族应用商店',
	16: '新浪应用中心',
	17: '当乐网',
	18: '历趣市场',
	19: '应用汇',
	20: '移动应用商场',
	21: '乐商店',
	22: 'ZOL手机软件',
	23: 'N多市场',
	24: '手机中国',
	25: '太平洋下载中心',
	26: '应用酷'
}

stat_item = ('Download', 'Rating', 'Rating_Num', 'Edition', 'Update_Time')

if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	result = []
	for package in package_list:
		package_result = []
		for market in market_list:
			ifexists = cursor.execute("select ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_market_result = {
					'Download': None,
					'Rating': None,
					'Rating_Num': None,
					'Edition': None,
					'Update_Time': None
				}
				package_result.append(package_market_result)
				print("Not Found "+package+" In "+market_name[market])
			else:
				cursor.execute("select ID from Market_Time_Metadata where Package_Name = '"+package+"' and MarketID="+str(market)+" and Time = (select max(Time) from Market_Time_Metadata where Package_Name = '"+package+"' and MarketID="+str(market)+")")
				time_id = cursor.fetchall()[0][0]
				cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select Downloads, Avg_rating, Total_rating from Market_Time_Metadata where ID="+str(time_id))
				time_metadata = cursor.fetchall()[0]
				cursor.execute("select Version, UpTime from Market_APK_Metadata where ID="+str(apk_id))
				apk_metadata = cursor.fetchall()[0]
				package_market_result = {
					'Download': time_metadata[0],
					'Rating': time_metadata[1],
					'Rating_Num': time_metadata[2],
					'Edition': apk_metadata[0],
					'Update_Time': None
				}
				if apk_metadata[1] != None:
					package_market_result['Update_Time'] = datetime.datetime.fromtimestamp(float(apk_metadata[1])).strftime('%Y-%m-%d %H:%M:%S')[:10]
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
