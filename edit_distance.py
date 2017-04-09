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

standard_market_id = 4

def edit_distance(str1, str2):
	if str1 == None or str2 == None:
		return None
	str1 = str1.replace('\r', "")
	str2 = str2.replace('\r', "")
	l1 = len(str1)
	l2 = len(str2)
	# f(x, y) = match(s1[x], s2[y])?f(x+1, y+1): 1+min(f(x+1, y), f(x, y+1), f(x+1, y+1))
	oldmem = [0] * (l2+1)
	newmem = [0] * (l2+1)
	oldmem[l2] = 0
	for j in range(l2-1, -1, -1):
		oldmem[j] = l2-j
	for i in range(l1-1, -1, -1):
		newmem[l2] = l1-i
		for j in range(l2-1, -1, -1):
			if str1[i] == str2[j] or (str1[i] in (' ', '\n', '\t') and str2[j] in (' ', '\n', '\t')):
				newmem[j] = oldmem[j+1]
			else:
				newmem[j] = 1+min(min(oldmem[j], oldmem[j+1]), newmem[j+1])
		tmpmem = oldmem
		oldmem = newmem
		newmem = tmpmem
	return oldmem[0]
	
if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	standard_description = []
	standard_release_note = []
	for package in package_list:
		ifexists = cursor.execute("select Description, ReleaseNote from Market_APK_Metadata where Package_Name = '"+package+"' and MarketID = "+str(standard_market_id))
		if ifexists == 0:
			standard_description.append(None)
			standard_release_note.append(None)
		else:
			info = cursor.fetchall()[0]
			standard_description.append(info[0])
			standard_release_note.append(info[1])
	result = []
	for i in range(package_list):
		package = package_list[i]
		package_result = []
		for market in market_list:
			ifexists = cursor.execute("select Description, ReleaseNote from Market_APK_Metadata where Package_Name = '"+package+"' and MarketID = "+str(market))
			if ifexists == 0:
				package_result.append((None, None))
			else:
				info = cursor.fetchall()[0]
				package_result.append((edit_distance(standard_description[i], info[0]), edit_distance(standard_release_note[i], info[1])))
		result.append(package_result)
	cursor.close()
	conn.close()
	fout = open('Description_Edit_Distance_With_'+str(standard_market_id)+'.csv')
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
	print("Finish Description Edit Distance - "+str(standard_market_id))
	fout = open('Release_Note_Edit_Distance_With_'+str(standard_market_id)+'.csv')
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
	print("Finish Release Note Edit Distance - "+str(standard_market_id))
