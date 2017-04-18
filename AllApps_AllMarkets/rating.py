market_list_dl = (0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15)
market_list = (0, 2, 3, 4, 5, 6, 8, 9, 11, 14, 15)

package_download = {}

fin = open('Downloads_Rank.csv', 'r')

for line in fin:
	package = line.split(',')[0]
	dl = int(line.split(',')[1].replace('\r', "").replace('\n', ""))
	package_download[package] = dl

fin.close()

package_market_rating = {}

fin = open('rating.txt', 'r')

for line in fin:
	package = line.split('\t')[0]
	marketid = int(line.split('\t')[1])
	rating = float(line.split('\t')[2])
	rating_num = line.split('\t')[3].replace('\r', "").replace('\n', "")
	if rating_num == 'None':
		rating_num = None
	else:
		rating_num = int(rating_num)
	if marketid in market_list:
		if not package in package_market_rating:
			package_market_rating[package] = {}
		package_market_rating[package][marketid] = tuple([rating, rating_num])

fin.close()

cnt = 0

select_pkg = []

market_dl_rtn_aggr = {}

for market in market_list:
	market_dl_rtn_aggr[market] = [0, 0]

for pkg, mk_rt in package_market_rating.items():
	if len(mk_rt) >= 4 and pkg in package_download and package_download[pkg] >= 50000:
		select_pkg.append(pkg)
		cnt += 1
		for mk, rt in mk_rt.items():
			if rt[1] != None:
				market_dl_rtn_aggr[mk][0] += package_download[pkg]
				market_dl_rtn_aggr[mk][1] += rt[1]

print (cnt)

select_pkg_set = set(select_pkg)

market_dl_rtn = {}

for market in market_list:
	market_dl_rtn[market] = [0, 0]

fin = open('downloads.txt', 'r')

googleplay_download_trans = {
	5: 3,
	50: 30,
	500: 300,
	5000: 3000,
	50000: 30000,
	500000: 300000,
	5000000: 3000000,
	50000000: 30000000,
	500000000: 300000000,
	5000000000: 3000000000,
	10: 7.5,
	100: 75,
	1000: 750,
	10000: 7500,
	100000: 75000,
	1000000: 750000,
	10000000: 7500000,
	100000000: 75000000,
	1000000000: 750000000,
	10000000000: 7500000000,
}

package_market_download = {}

for line in fin:
	package = line.split('\t')[0]
	if package in select_pkg_set:
		marketid = int(line.split('\t')[1])
		dld = line.split('\t')[2].replace('\r', '').replace('\n', '')
		if dld != 'None' and marketid in market_list_dl and marketid in package_market_rating[package] and package_market_rating[package][marketid][1] != None:
			dld = int(dld)
			if marketid == 0:
				dld = googleplay_download_trans[dld]
			if not package in package_market_download:
				package_market_download[package] = {}
			package_market_download[package][marketid] = dld
			rtn = package_market_rating[package][marketid][1]
			market_dl_rtn[marketid][0] += dld
			market_dl_rtn[marketid][1] += rtn

fin.close()

for key, val in market_dl_rtn.items():
	if val[0] > 0 and val[1] > 0:
		print (key, end=' : ')
		print (val, end=' ')
		print (val[1]/val[0])

for key, val in market_dl_rtn_aggr.items():
	if val[0] > 0 and val[1] > 0:
		print (key, end=' : ')
		print (val, end=' ')
		print (val[1]/val[0])

def get_median(lst):
	if not len(lst):
		return 0
	lst.sort()
	half = len(lst) // 2
	return (lst[half]+lst[~half])/2

threshold = 2.5
has_error = 0

market_stat = {}
for market in market_list:
	market_stat[market] = [0, 0, [], []]

error_type = {
	'No Rating': [],
	'Default Rating (Rating >> Median Rating)': [],
	'Default Rating (Rating << Median Rating)': [],
	'Too Less Rating Num (Rating >> Median Rating)': [],
	'Too Less Rating Num (Rating << Median Rating)': [],
	'Too Much Rating Num (Rating >> Median Rating and Rating Num >> Average Rating Num)': [],
	'Too Much Rating Num (Rating >> Median Rating and Rating Num > Average Rating Num)': [],
	'Too Much Rating Num (Rating >= Median Rating and Rating Num >> Average Rating Num)': [],
	'Too Much Rating Num (Rating << Median Rating and Rating Num > Average Rating Num)': [],
	'Other (Rating > Median Rating)': [],
	'Other (Rating < Median Rating)': []
}

Rating_Num_Threshold_1 = 50
Rating_Num_Threshold_2 = 5
Rating_Num_Threshold_3 = 0.05

for pkg in select_pkg:
	rating_lst = []
	for rt in package_market_rating[pkg].values():
		if not (rt[0] == 0 and (rt[1] == None or rt[1] == 0)):
			rating_lst.append(rt[0])
	median = get_median(rating_lst)
	error_list = []
	for mk, rt in package_market_rating[pkg].items():
		market_stat[mk][0] += 1
		rtn_dl_rate = None
		if market_dl_rtn[mk][0] > 0 and rt[1] != None and mk in package_market_download[pkg]:
			rtn_dl_rate = (rt[1]/package_market_download[pkg][mk])/(market_dl_rtn[mk][1]/market_dl_rtn[mk][0])
			rtn_dl_aggr_rate = None
		else:
			rtn_dl_aggr_rate = None
			if market_dl_rtn_aggr[mk][0] > 0 and rt[1] != None:
				rtn_dl_aggr_rate = (rt[1]/package_download[pkg])/(market_dl_rtn_aggr[mk][1]/market_dl_rtn_aggr[mk][0])
		if rt[0] > median+threshold or rt[0] < median-threshold or (rt[0] >= median and rt[1] != None and rt[1] >= 100 and ((rtn_dl_rate != None and rtn_dl_rate > Rating_Num_Threshold_1) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate > Rating_Num_Threshold_1))):
			dld = None
			dld_aggr = None
			if pkg in package_market_download and mk in package_market_download[pkg]:
				dld = package_market_download[pkg][mk]
			else:
				dld_aggr = package_download[pkg]
			error = tuple([pkg, median, mk, rt[0], rt[1], dld, dld_aggr])
			error_list.append(error[2:])
			if rt[0] >= median:
				market_stat[mk][2].append(error)
			else:
				market_stat[mk][3].append(error)
			if rt[0] == 0 and (rt[1] == None or rt[1] == 0):
				error_type['No Rating'].append(error)
			elif rt[0] > median+threshold and (rt[1] == None or rt[1] == 0):
				error_type['Default Rating (Rating >> Median Rating)'].append(error)
			elif rt[0] < median-threshold and (rt[1] == None or rt[1] == 0):
				error_type['Default Rating (Rating << Median Rating)'].append(error)
			elif rt[0] > median+threshold and (rt[1] < 10 or ((rtn_dl_rate != None and rtn_dl_rate < Rating_Num_Threshold_3) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate < Rating_Num_Threshold_3))):
				error_type['Too Less Rating Num (Rating >> Median Rating)'].append(error)
			elif rt[0] < median-threshold and (rt[1] < 10 or ((rtn_dl_rate != None and rtn_dl_rate < Rating_Num_Threshold_3) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate < Rating_Num_Threshold_3))):
				error_type['Too Less Rating Num (Rating << Median Rating)'].append(error)
			elif rt[0] > median+threshold and rt[1] >= 100 and ((rtn_dl_rate != None and rtn_dl_rate > Rating_Num_Threshold_1) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate > Rating_Num_Threshold_1)):
				error_type['Too Much Rating Num (Rating >> Median Rating and Rating Num >> Average Rating Num)'].append(error)
			elif rt[0] > median+threshold and rt[1] >= 100 and ((rtn_dl_rate != None and rtn_dl_rate > Rating_Num_Threshold_2) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate > Rating_Num_Threshold_2)):
				error_type['Too Much Rating Num (Rating >> Median Rating and Rating Num > Average Rating Num)'].append(error)
			elif rt[0] < median-threshold and rt[1] >= 100 and ((rtn_dl_rate != None and rtn_dl_rate > Rating_Num_Threshold_2) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate > Rating_Num_Threshold_2)):
				error_type['Too Much Rating Num (Rating << Median Rating and Rating Num > Average Rating Num)'].append(error)
			elif rt[0] >= median and rt[1] >= 100 and ((rtn_dl_rate != None and rtn_dl_rate > Rating_Num_Threshold_1) or (rtn_dl_aggr_rate != None and rtn_dl_aggr_rate > Rating_Num_Threshold_1)):
				error_type['Too Much Rating Num (Rating >= Median Rating and Rating Num >> Average Rating Num)'].append(error)
			elif rt[0] > median:
				error_type['Other (Rating > Median Rating)'].append(error)
			else:
				error_type['Other (Rating < Median Rating)'].append(error)
		else:
			market_stat[mk][1] += 1
	if len(error_list):
		print (pkg, end=' ')
		print (median, end=' ')
		print (error_list)
		has_error += 1

print (has_error)

error_cnt = 0

for types, error_list in error_type.items():
	error_cnt += len(error_list)
	print (types+' '+str(len(error_list))+' : ')
	for error in error_list:
		print (error)
	print ()

print (error_cnt)

print ()

for mk, stat in market_stat.items():
	print (mk, end=' : ')
	print (str(stat[0])+' '+str(stat[1]))
	print ('>Median: '+str(len(stat[2])))
#	for item in stat[2]:
#		print (item)
	print ('<Median: '+str(len(stat[3])))
#	for item in stat[3]:
#		print (item)