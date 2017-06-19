import codecs, math

market_list = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26)

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

package_market_rating = {}

with codecs.open('data.txt', 'r', 'utf-8') as fin:
	for line in fin:
		package = line.split('\t')[0].replace(',', '.')
		if not package in package_market_rating:
			package_market_rating[package] = {'Markets': 0}
			for market in market_list:
				package_market_rating[package][market] = None
		market = int(line.split('\t')[1])
		downloads = line.split('\t')[2]
		if downloads == 'None': downloads = None
		else: downloads = int(downloads)
		rating = line.split('\t')[3]
		if rating == 'None': rating = None
		else: rating = float(rating)
		rating_num = line.split('\t')[4].replace('\r', "").replace('\n', "")
		if rating_num == 'None': rating_num = None
		else: rating_num = int(rating_num)
		package_market_rating[package][market] = [downloads, rating, rating_num]
		package_market_rating[package]['Markets'] += 1

with codecs.open('Downloads_Rank.csv', 'r', 'utf-8') as fin:
	for line in fin:
		package = line.split(',')[0]
		downloads = int(line.split(',')[1].replace('\r', "").replace('\n', ""))
		package_market_rating[package]['Downloads'] = downloads

print (len(package_market_rating))

common_pkg_num_lst = [0] * (len(market_list)+1)

for pkg in package_market_rating.keys():
	common_pkg_num_lst[package_market_rating[pkg]['Markets']] += 1

print (common_pkg_num_lst)

with codecs.open('stat/rating_of_apps.csv', 'w', 'utf-8') as fout:
	fout.write('包名,综合下载量')
	for i in range(3):
		for j in market_list:
			fout.write(","+market_name[j])
	fout.write('\n')
	for pkg in package_market_rating.keys():
		if package_market_rating[pkg]['Markets'] >= 17:
			fout.write(pkg+',')
			if 'Downloads' in package_market_rating[pkg]:
				fout.write(str(package_market_rating[pkg]['Downloads']))
			for j in market_list:
				fout.write(',')
				if package_market_rating[pkg][j] != None and package_market_rating[pkg][j][0] != None:
					fout.write(str(package_market_rating[pkg][j][0]))
			for j in market_list:
				fout.write(',')
				if package_market_rating[pkg][j] != None and package_market_rating[pkg][j][1] != None:
					fout.write(str(package_market_rating[pkg][j][1]))
			for j in market_list:
				fout.write(',')
				if package_market_rating[pkg][j] != None and package_market_rating[pkg][j][2] != None:
					fout.write(str(package_market_rating[pkg][j][2]))
			fout.write('\n')
