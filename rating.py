market_list = (0, 2, 4, 5, 6, 8, 9, 11, 15, 21)

package_market_rating = {}

fin = open('Downloads_Rank.csv', 'r')

for line in fin:
	package = line.split(',')[0]
	downloads = int(line.split(',')[1].replace('\r', "").replace('\n', ""))
	if downloads == 0:
		downloads = 1
	package_market_rating[package] = {'Downloads': downloads}
	for market in market_list:
		package_market_rating[package][market] = None

fin.close()

fin = open('rating.txt', 'r')

for line in fin:
	package = line.split('\t')[0]
	market = int(line.split('\t')[1])
	if market in market_list:
		rating = line.split('\t')[2]
		if rating == 'None': rating = None
		else: rating = float(rating)
		rating_num = line.split('\t')[3]
		if rating_num == 'None': rating_num = None
		else: rating_num = int(rating_num)
		stars = line.split('\t')[4].replace('\r', "").replace('\n', "")
		if stars == 'None': stars = None
		else: 
			star = stars.split(';')
			star_sum = 0
			real_rating = 0
			for i in range(5):
				star_sum += int(star[i])
				real_rating += (i+1)*2*int(star[i])
			if rating_num != None and rating_num > 0 and star_sum != 0:
				rating = real_rating/star_sum
		if rating != None and rating_num != None and package in package_market_rating:
			if rating == 0 and rating_num == 0: package_market_rating[package][market] = [rating, rating_num, 'No Rating']
			elif rating_num == 0: package_market_rating[package][market] = [rating, rating_num, 'Default Rating']
			else: package_market_rating[package][market] = [rating, rating_num, 'Normal']

fin.close()

threshold_rate_too_much = 50
threshold_num_too_much = 100

threshold_rate_too_less = 0
threshold_num_too_less = 10

threshold_min_downloads = 100000

for market in market_list:
	while True:
		downloads_sum = 0
		rating_num_sum = 0
		change_cnt = 0
		for package in package_market_rating.keys():
			if package_market_rating[package]['Downloads'] >= threshold_min_downloads and package_market_rating[package][market] != None and package_market_rating[package][market][2] in ['No Rating', 'Default Rating', 'Normal']:
				downloads_sum += package_market_rating[package]['Downloads']
				rating_num_sum += package_market_rating[package][market][1]
		rating_num_downloads_rate = rating_num_sum/downloads_sum
		for package in package_market_rating.keys():
			if package_market_rating[package]['Downloads'] >= threshold_min_downloads and package_market_rating[package][market] != None and package_market_rating[package][market][2] in ['No Rating', 'Default Rating', 'Normal']:
				if package_market_rating[package][market][1] > threshold_num_too_much and package_market_rating[package][market][1]/package_market_rating[package]['Downloads'] > threshold_rate_too_much*rating_num_downloads_rate:
					change_cnt += 1
					package_market_rating[package][market][2] = 'Too Much Rating Num'
		if change_cnt == 0:
			break
	for package in package_market_rating.keys():
		if package_market_rating[package]['Downloads'] >= threshold_min_downloads and package_market_rating[package][market] != None and package_market_rating[package][market][2] == 'Normal':
			if package_market_rating[package][market][1] < threshold_num_too_less or package_market_rating[package][market][1]/package_market_rating[package]['Downloads'] < threshold_rate_too_less*rating_num_downloads_rate:
				package_market_rating[package][market][2] = 'Too Less Rating Num'

"""
for market in market_list:
	for package in package_market_rating.keys():
		if package_market_rating[package][market] != None:
			print_dl = False
			if package_market_rating[package][market][2] == 'Too Much Rating Num':
				if not print_dl:
					print (package, end = ' (')
					print (package_market_rating[package]['Downloads'], end = ') : ')
					print_dl = True
				print ([market, package_market_rating[package][market][0], package_market_rating[package][market][1]], end = ' ')
			if print_dl:
				print ()
"""

for market in market_list:			
	cnt = 0
	cnt_normal = 0
	cnt_no_rating = 0
	cnt_default_rating = 0
	cnt_too_much_rating_num = 0
	cnt_too_less_rating_num = 0
	cnt_unknown = 0
	for package in package_market_rating.keys():
		if package_market_rating[package]['Downloads'] >= threshold_min_downloads and package_market_rating[package][market] != None:
			cnt += 1
			if package_market_rating[package][market][2] == 'Normal': cnt_normal += 1
			elif package_market_rating[package][market][2] == 'No Rating': cnt_no_rating += 1
			elif package_market_rating[package][market][2] == 'Default Rating': cnt_default_rating += 1
			elif package_market_rating[package][market][2] == 'Too Much Rating Num': cnt_too_much_rating_num += 1
			elif package_market_rating[package][market][2] == 'Too Less Rating Num': cnt_too_less_rating_num += 1
			else: cnt_unknown += 1
	print ([market, cnt, cnt_normal, cnt_no_rating, cnt_default_rating, cnt_too_much_rating_num, cnt_too_less_rating_num, cnt_unknown])

def get_median(lst):
	if not len(lst):
		return None
	lst.sort()
	half = len(lst) // 2
	return (lst[half]+lst[~half])/2

threshold_min_markets = 5
threshold_abnormal = 2

for package in package_market_rating:
	if package_market_rating[package]['Downloads'] >= threshold_min_downloads:
		rating_list = []
		market_cnt = 0
		for market in market_list:
			if package_market_rating[package][market] != None:
				market_cnt += 1
				if package_market_rating[package][market][2] == 'Normal': rating_list.append(package_market_rating[package][market][0])
		if market_cnt >= threshold_min_markets:
			median = get_median(rating_list)
			if median == None:
				print (package+' ('+str(package_market_rating[package]['Downloads'])+') All Too Much or Too Less Rating Num')
			else:
				abnormal = False
				for market in market_list:
					if package_market_rating[package][market] != None and package_market_rating[package][market][2] == 'Normal':
						if package_market_rating[package][market][0] > median+threshold_abnormal or package_market_rating[package][market][0] < median-threshold_abnormal:
							if not abnormal:
								#print (package, end = ' (')
								#print (median, end = ', ')
								#print (len(rating_list), end = ') : ')
								abnormal = True
							package_market_rating[package][market][2] = 'Abnormal'
							#print ([market, package_market_rating[package][market][0], package_market_rating[package][market][1]], end = ' ')
		#		if abnormal:
		#			print ()

package_cnt = 0
package_cnt_normal = 0
package_cnt_abnormal = 0
package_cnt_no_rating = 0
package_cnt_default_rating = 0
package_cnt_too_much_rating_num = 0
package_cnt_too_less_rating_num = 0

select_package_set = set()

for package in package_market_rating:
	if package_market_rating[package]['Downloads'] >= threshold_min_downloads:
		market_cnt = 0
		for market in market_list:
			if package_market_rating[package][market] != None:
				market_cnt += 1
		if market_cnt >= threshold_min_markets:
			select_package_set.add(package)
			package_cnt += 1
			abnormal = False
			no_rating = False
			default_rating = False
			too_much_rating_num = False
			too_less_rating_num = False
			for market in market_list:
				if package_market_rating[package][market] != None:
					if package_market_rating[package][market][2] == 'Abnormal': abnormal = True
					elif package_market_rating[package][market][2] == 'No Rating': no_rating = True
					elif package_market_rating[package][market][2] == 'Default Rating': default_rating = True
					elif package_market_rating[package][market][2] == 'Too Much Rating Num': too_much_rating_num = True
					elif package_market_rating[package][market][2] == 'Too Less Rating Num': too_less_rating_num = True
			if (not abnormal) and (not too_much_rating_num): package_cnt_normal += 1
			if abnormal: package_cnt_abnormal += 1
			if no_rating: package_cnt_no_rating += 1
			if default_rating: package_cnt_default_rating += 1
			if too_much_rating_num: package_cnt_too_much_rating_num += 1
			if too_less_rating_num: package_cnt_too_less_rating_num += 1

print ([package_cnt, package_cnt_normal, package_cnt_abnormal, package_cnt_no_rating, package_cnt_default_rating, package_cnt_too_much_rating_num, package_cnt_too_less_rating_num])

for market in market_list:			
	cnt = 0
	cnt_normal = 0
	cnt_abnormal = 0
	cnt_no_rating = 0
	cnt_default_rating = 0
	cnt_too_much_rating_num = 0
	cnt_too_less_rating_num = 0
	cnt_unknown = 0
	for package in package_market_rating.keys():
		if package in select_package_set and package_market_rating[package][market] != None:
			cnt += 1
			if package_market_rating[package][market][2] == 'Normal': cnt_normal += 1
			elif package_market_rating[package][market][2] == 'Abnormal': cnt_abnormal += 1
			elif package_market_rating[package][market][2] == 'No Rating': cnt_no_rating += 1
			elif package_market_rating[package][market][2] == 'Default Rating': cnt_default_rating += 1
			elif package_market_rating[package][market][2] == 'Too Much Rating Num': cnt_too_much_rating_num += 1
			elif package_market_rating[package][market][2] == 'Too Less Rating Num': cnt_too_less_rating_num += 1
			else: cnt_unknown += 1
	print ([market, cnt, cnt_normal, cnt_abnormal, cnt_no_rating, cnt_default_rating, cnt_too_much_rating_num, cnt_too_less_rating_num, cnt_unknown])