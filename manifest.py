from constant import *
import pymysql, os, codecs, datetime, re, xml.dom.minidom, chardet

def get_version(package, market, md5, sha256):
	if not os.path.isfile(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml'):
		return None
	try:
		dom = xml.dom.minidom.parse(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml')
		version = dom.documentElement.getAttribute("android:versionName")
		return version
	except:
		try:
			fin = open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'rb')
			fencoding = chardet.detect(fin.read())
			fin.close()
			fin = codecs.open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'r', fencoding['encoding'])
			data = fin.read()
			matcher = re.findall('android:versionName=".*?"', data)
			if len(matcher):
				return matcher[0].replace('android:versionName="', "").replace('"', "")
			return None
		except:
			return None

def get_permission(package, market, md5, sha256):
	if not os.path.isfile(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml'):
		return None
	try:
		fin = open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'rb')
		fencoding = chardet.detect(fin.read())
		fin.close()
		fin = codecs.open(root+market+"/"+package+'/{'+md5+'-'+sha256+'}/AndroidManifest.xml', 'r', fencoding['encoding'])
		data = fin.read()
		result = set()
		matcher = re.findall('<uses-permission[ \t\r\n]*android:name=".*?"', data)
		if len(matcher):
			for permission in matcher:
				result.add(re.subn('<uses-permission[ \t\r\n]*android:name="', "", permission)[0].replace('"', ""))
		matcher = re.findall('<android:uses-permission[ \t\r\n]*android:name=".*?"', data)
		if len(matcher):
			for permission in matcher:
				result.add(re.subn('<android:uses-permission[ \t\r\n]*android:name="', "", permission)[0].replace('"', ""))
		return result
	except:
		return set()

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
				package_result.append((None, None, None))
			else:
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select Version, MD5, SHA256 from Market_APK_Metadata where ID="+str(apk_id))
				info = cursor.fetchall()[0]
				version_metadata = info[0]
				if version_metadata != None: version_metadata = version_metadata.replace('V', "")
				md5 = info[1]
				sha256 = info[2]
				version_manifest = get_version(package, market_dir[market_list[i]], md5, sha256)
				permission_set = get_permission(package, market_dir[market_list[i]], md5, sha256)
				if version_metadata != version_manifest:
					version_metadata_str = version_metadata
					if version_metadata == None: version_metadata_str = 'None'
					version_manifest_str = version_manifest
					if version_manifest == None: version_manifest_str = 'None'
					print ("Version of "+package+" In "+market_name[market]+" Not Matched: "+version_metadata_str+" & "+version_manifest_str)
				package_result.append((version_metadata, version_manifest, permission_set))
		result.append(package_result)
		for i in range(len(market_list)):
			for j in range(i+1, len(market_list)):
				if package_result[i][2] != None and package_result[j][2] != None:
					if package_result[i][2] != package_result[j][2] and package_result[i][1] == package_result[j][1]:
						print ("Permission of "+package+" In "+market_name[market_list[i]]+" and "+market_name[market_list[j]]+" Not the Same While Same Version: ("+str(len(package_result[i][2]))+") ("+str(len(package_result[j][2]))+")")
						for permission in package_result[i][2]:
							if not permission in package_result[j][2]:
								print ("- "+permission)
						for permission in package_result[j][2]:
							if not permission in package_result[i][2]:
								print ("+ "+permission) 
	cursor.close()
	conn.close()
	fout = open("APK_Real_Version_Statistics.csv", "w")
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