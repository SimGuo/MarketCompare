from constant import *
from manifest import get_version
import pymysql, os, shutil, time

def version_cmp(v1, v2): # return if v1 is later than v2
	if v1 == None: return False
	if v2 == None: return True
	l1 = len(v1.split('.'))
	l2 = len(v2.split('.'))
	for i in range(0, min(l1, l2)):
		if int(v1.split('.')[i]) > int(v2.split('.')[i]): return True
		elif int(v1.split('.')[i]) < int(v2.split('.')[i]): return False
	return l1 > l2

def decode_apk(srcapk, destdir):
	shutil.copy(srcapk, destdir+'.apk')
	os.system("apktool d -f "+destdir+".apk > apktool.log")
	time.sleep(0.5)
	os.remove(destdir+'.apk')

def dir_cmp(dir1, dir2):
	ls1 = os.listdir(dir1)
	ls2 = os.listdir(dir2)
	for i in ls1:
		if os.path.isfile(dir1+i):
			if os.path.isdir(dir2+i):
				print ('D '+str(dir1+i)[str(dir1+i).index('/')+1:])
			elif os.path.isfile(dir2+i):
				if open(dir1+i, 'rb').read() != open(dir2+i, 'rb').read():
					print ('D '+str(dir1+i)[str(dir1+i).index('/')+1:])
			else:
				print ('- '+str(dir1+i)[str(dir1+i).index('/')+1:])
		elif os.path.isdir(dir1+i):
			if os.path.isdir(dir2+i):
				dir_cmp(dir1+i+'/', dir2+i+'/')
			elif os.path.isfile(dir2+i):
				print ('D '+str(dir1+i)[str(dir1+i).index('/')+1:])
			else:
				print ('- '+str(dir1+i)[str(dir1+i).index('/')+1:])
	for i in ls2:
		if (not os.path.isdir(dir1+i)) and (not os.path.isfile(dir1+i)):
			print ('+ '+str(dir2+i)[str(dir2+i).index('/')+1:])

if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	for package in package_list:
		package_result = []
		for i in range(len(market_list)):
			market = market_list[i]
			ifexists = cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_result.append((None, None))
			else:
				apk_id = cursor.fetchall()[0][0]
				cursor.execute("select MD5, SHA256 from Market_APK_Metadata where ID="+str(apk_id))
				info = cursor.fetchall()[0]
				md5 = info[0]
				sha256 = info[1]
				version_manifest = get_version(package, market_dir[market_list[i]], md5, sha256)
				package_result.append((version_manifest, md5+'-'+sha256))
		newest_version = None
		for package_market_result in package_result:
			if version_cmp(package_market_result[0], newest_version):
				newest_version = package_market_result[0]
		print ('The Latest Version of '+package+' Is '+newest_version)
		md5_sha256_lst = []
		md5_sha256_market = {}
		for i in range(len(package_result)):
			package_market_result = package_result[i]
			if package_market_result[0] == newest_version and package_market_result[1] != None:
				if not package_market_result[1] in md5_sha256_lst:
					md5_sha256_lst.append(package_market_result[1])
				md5_sha256_index = md5_sha256_lst.index(package_market_result[1])
				if not md5_sha256_index in md5_sha256_market:
					md5_sha256_market[md5_sha256_index] = [i]
				else:
					md5_sha256_market[md5_sha256_index].append(i)
		if len(md5_sha256_lst) == 1:
			print (package+' Has Only One MD5-SHA256')
		else:
			for i in range(len(md5_sha256_lst)):
				md5_sha256 = md5_sha256_lst[i]
				line = str(i)+' - '
				for j in md5_sha256_market[i]:
					line += market_name[market_list[j]]+','
				print (line[:-1])
			shutil.rmtree('~tmp1', ignore_errors=True)
			time.sleep(1)
			decode_apk(root+market_dir[market_list[md5_sha256_market[0][0]]]+'/'+package+'/{'+md5_sha256_lst[0]+'}/'+package+'.apk', '~tmp1')			
			for i in range(1, len(md5_sha256_lst)):
				shutil.rmtree('~tmp2', ignore_errors=True)
				time.sleep(1)
				decode_apk(root+market_dir[market_list[md5_sha256_market[i][0]]]+'/'+package+'/{'+md5_sha256_lst[i]+'}/'+package+'.apk', '~tmp2')
				print ('Comparison Between 0 And '+str(i))
				dir_cmp('~tmp1/', '~tmp2/')
	cursor.close()
	conn.close()
	shutil.rmtree('~tmp1', ignore_errors=True)
	shutil.rmtree('~tmp2', ignore_errors=True)
