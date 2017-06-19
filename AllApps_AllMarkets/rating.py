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

def analyzelst(lst):
	if lst == None or not len(lst):
		print ("Empty List")
		return None
	print ("Length:", len(lst))
	lst.sort()
	half = len(lst)//2
	median = (lst[half]+lst[~half])/2
	quarter1 = lst[int(len(lst)*0.25)]
	quarter3 = lst[int(len(lst)*0.75)]
	print ("Min to Median to Max:", lst[0], quarter1, median, quarter3, lst[-1])
	avg = sum(lst)/len(lst)
	ste = 0
	for i in lst:
		ste += (i-avg)*(i-avg)
	ste = math.sqrt(ste/len(lst))
	print ("Average:", avg, "SE:", ste)
	return lst[0], quarter1, median, quarter3, lst[-1], avg, ste

mkt_stat = {}

fout_rating_include_default = codecs.open('stat/rating_include_default.csv', 'w', 'utf-8')
fout_rating_exclude_default = codecs.open('stat/rating_exclude_default.csv', 'w', 'utf-8')
fout_rating_num = codecs.open('stat/rating_num.csv', 'w', 'utf-8')

fout_rating_include_default.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')
fout_rating_exclude_default.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')
fout_rating_num.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')

for mkt in market_list:
	mkt_stat[mkt] = {'Package Num': 0, 'No Rating Package Num': 0, 'Default Rating Package Num': 0, 'Normal Rating Package Num': 0, 'Rating Include Default': [], 'Rating Exclude Default': [], 'Rating Num': []}
	for pkg in package_market_rating.keys():
		if package_market_rating[pkg][mkt] != None:
			mkt_stat[mkt]['Package Num'] += 1
			if package_market_rating[pkg][mkt][1] == None: mkt_stat[mkt]['No Rating Package Num'] += 1
			else:
				if (package_market_rating[pkg][mkt][1] == 0 and (package_market_rating[pkg][mkt][2] == 0 or package_market_rating[pkg][mkt][2] == None)) or package_market_rating[pkg][mkt][2] == 0:
					mkt_stat[mkt]['Default Rating Package Num'] += 1
					mkt_stat[mkt]['Rating Include Default'].append(package_market_rating[pkg][mkt][1])
					if package_market_rating[pkg][mkt][2] != None: mkt_stat[mkt]['Rating Num'].append(package_market_rating[pkg][mkt][2])
				else:
					mkt_stat[mkt]['Normal Rating Package Num'] += 1
					mkt_stat[mkt]['Rating Include Default'].append(package_market_rating[pkg][mkt][1])
					mkt_stat[mkt]['Rating Exclude Default'].append(package_market_rating[pkg][mkt][1])
					if package_market_rating[pkg][mkt][2] != None: mkt_stat[mkt]['Rating Num'].append(package_market_rating[pkg][mkt][2])
	print (mkt)
	print (mkt_stat[mkt]['Package Num'], mkt_stat[mkt]['No Rating Package Num'], mkt_stat[mkt]['Default Rating Package Num'], mkt_stat[mkt]['Normal Rating Package Num'])
	print ('Rating Include Default')
	r = analyzelst(mkt_stat[mkt]['Rating Include Default'])
	if r != None: fout_rating_include_default.write(market_name[mkt]+','+str(mkt_stat[mkt]['Default Rating Package Num']+mkt_stat[mkt]['Normal Rating Package Num'])+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('Rating Exclude Default')
	r = analyzelst(mkt_stat[mkt]['Rating Exclude Default'])
	if r != None: fout_rating_exclude_default.write(market_name[mkt]+','+str(mkt_stat[mkt]['Normal Rating Package Num'])+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('Rating Num')
	r = analyzelst(mkt_stat[mkt]['Rating Num'])
	if r != None: fout_rating_num.write(market_name[mkt]+','+str(len(mkt_stat[mkt]['Rating Num']))+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('')

fout_rating_num.close()
fout_rating_exclude_default.close()
fout_rating_include_default.close()

mkt_stat = {}

fout_rating_include_default = codecs.open('stat/common_apps_rating_include_default.csv', 'w', 'utf-8')
fout_rating_exclude_default = codecs.open('stat/common_apps_rating_exclude_default.csv', 'w', 'utf-8')
fout_rating_num = codecs.open('stat/common_apps_rating_num.csv', 'w', 'utf-8')

fout_rating_include_default.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')
fout_rating_exclude_default.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')
fout_rating_num.write('市场名称,样本数量,最小值,下四分位数,中位数,上四分位数,最大值,平均数,标准差\n')

for mkt in market_list:
	mkt_stat[mkt] = {'Package Num': 0, 'No Rating Package Num': 0, 'Default Rating Package Num': 0, 'Normal Rating Package Num': 0, 'Rating Include Default': [], 'Rating Exclude Default': [], 'Rating Num': []}
	for pkg in package_market_rating.keys():
		if package_market_rating[pkg][mkt] != None and package_market_rating[pkg]['Markets'] >= 5:
			mkt_stat[mkt]['Package Num'] += 1
			if package_market_rating[pkg][mkt][1] == None: mkt_stat[mkt]['No Rating Package Num'] += 1
			else:
				if (package_market_rating[pkg][mkt][1] == 0 and (package_market_rating[pkg][mkt][2] == 0 or package_market_rating[pkg][mkt][2] == None)) or package_market_rating[pkg][mkt][2] == 0:
					mkt_stat[mkt]['Default Rating Package Num'] += 1
					mkt_stat[mkt]['Rating Include Default'].append(package_market_rating[pkg][mkt][1])
					if package_market_rating[pkg][mkt][2] != None: mkt_stat[mkt]['Rating Num'].append(package_market_rating[pkg][mkt][2])
				else:
					mkt_stat[mkt]['Normal Rating Package Num'] += 1
					mkt_stat[mkt]['Rating Include Default'].append(package_market_rating[pkg][mkt][1])
					mkt_stat[mkt]['Rating Exclude Default'].append(package_market_rating[pkg][mkt][1])
					if package_market_rating[pkg][mkt][2] != None: mkt_stat[mkt]['Rating Num'].append(package_market_rating[pkg][mkt][2])
	print (mkt)
	print (mkt_stat[mkt]['Package Num'], mkt_stat[mkt]['No Rating Package Num'], mkt_stat[mkt]['Default Rating Package Num'], mkt_stat[mkt]['Normal Rating Package Num'])
	print ('Rating Include Default')
	r = analyzelst(mkt_stat[mkt]['Rating Include Default'])
	if r != None: fout_rating_include_default.write(market_name[mkt]+','+str(mkt_stat[mkt]['Default Rating Package Num']+mkt_stat[mkt]['Normal Rating Package Num'])+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('Rating Exclude Default')
	r = analyzelst(mkt_stat[mkt]['Rating Exclude Default'])
	if r != None: fout_rating_exclude_default.write(market_name[mkt]+','+str(mkt_stat[mkt]['Normal Rating Package Num'])+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('Rating Num')
	r = analyzelst(mkt_stat[mkt]['Rating Num'])
	if r != None: fout_rating_num.write(market_name[mkt]+','+str(len(mkt_stat[mkt]['Rating Num']))+','+str(r[0])+','+str(r[1])+','+str(r[2])+','+str(r[3])+','+str(r[4])+','+str(r[5])+','+str(r[6])+'\n')
	print ('')

fout_rating_num.close()
fout_rating_exclude_default.close()
fout_rating_include_default.close()
