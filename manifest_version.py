import pymysql, os, codecs, datetime, re, xml.dom.minidom

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

market_dir = {
	0: 'googleplay',
	2: 'yingyongbao',
	3: 'baidu',
	4: '360',
	5: 'huawei',
	6: 'xiaomi',
	7: 'wandoujia',
	8: 'hiapk',
	9: 'anzhi',
	10: '91',
	11: 'oppo',
	12: 'pp',
	13: 'sogou',
	14: 'gfan',
	15: 'meizu',
	16: 'sina',
	17: 'dcn',
	18: 'liqucn',
	19: 'appchina',
	20: '10086',
	21: 'lenovo',
	22: 'zol',
	23: 'nduo',
	24: 'cnmo',
	25: 'pconline',
	26: 'appcool'
}

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

root = '/home/tzeho/Android_10app/'

def get_version(package, market, md5, sha256):
	if not os.path.isfile(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml'):
		return None
	try:
		dom = xml.dom.minidom.parse(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml')
		version = dom.documentElement.getAttribute("android:versionName")
		return version
	except:
		try:
			fin = codecs.open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'r', 'utf-8')
			data = fin.read()
			matcher = re.findall('android:versionName=".*?"', data)
			if len(matcher):
				return matcher[0].replace('android:versionName="', "").replace('"', "")
			return None
		except:
			try:
				fin = codecs.open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'r', 'gb2312')
				data = fin.read()
				matcher = re.findall('android:versionName=".*?"', data)
				if len(matcher):
					return matcher[0].replace('android:versionName="', "").replace('"', "")
				return None
			except:
				print ('IO Exception '+package+' In '+market)
				return None

if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	result = []
	for package in package_list:
		package_result = []
		for i in range(len(market_list)):
			market = market_list[i]
			ifexists = cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_result.append((None, None))
				#print("Not Found "+package+" In "+market_name[market])
			else:
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select Version, MD5, SHA256 from Market_APK_Metadata where ID="+str(apk_id))
				info = cursor.fetchall()[0]
				version_metadata = info[0]
				if version_metadata != None: version_metadata = version_metadata.replace('V', "")
				md5 = info[1]
				sha256 = info[2]
				version_manifest = get_version(package, market_dir[market_list[i]], md5, sha256)
				if version_metadata != version_manifest:
					version_metadata_str = version_metadata
					if version_metadata == None: version_metadata_str = 'None'
					version_manifest_str = version_manifest
					if version_manifest == None: version_manifest_str = 'None'
					print ("Version of "+package+" In "+market_name[market]+" Not Matched: "+version_metadata_str+" & "+version_manifest_str)
				package_result.append((version_metadata, version_manifest))
		result.append(package_result)
	cursor.close()
	conn.close()
	fout = open("Real_Version_Statistics.csv", "w")
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
