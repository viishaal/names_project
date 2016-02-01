import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import gridspec
import os
import math
import requests
import untangle

API_KEY_BEHIND_THE_NAME = "vi565456"
URL_FORMAT = "http://www.behindthename.com/api/lookup.php?name={}&key=vi565456"

SCRAPE_BTN = True

def plot_name_popularity(df, name, gender, save):
	""" given name and gender plots a line chart of the name's historic popularity since 1880
	"""
	g = df[df.name.isin([name]) & df.sex.isin([gender])]
	plt.close()
	g.plot("year", "percent")
	plt.xticks(np.arange(min(g.year), max(g.year)+1, 10))
	plt.title(name+"_"+gender)
	if save:
		plt.savefig(name+"_"+gender+".png", format="png")
	else:
		plt.show()

def unique_names(df):
	""" plots unique names in each 10 year
	"""
	per_group = 10
	bins = np.arange(df.year.min(), df.year.max(), per_group)
	grouped = df.groupby(np.digitize(df.year, bins)).agg({"name": pd.Series.nunique})
	plt.close()
	grouped[:-1].plot(label="unique_names")
	plt.title("Uniques_{}".format(per_group))
	#plt.set_legend("unique_names")
	plt.savefig("Uniques{0}.png".format(per_group), format="png")

def first_letter(arg):
	return arg.lower()[0]

def group_alphabet(arg, n):
	first = arg.lower()[0]
	number_elems = int(math.ceil(26.0/n))
	return (ord(first) - ord('a'))/number_elems


def plot_by_alphabet_groups(df, num_groups):
	df["alph_group"] = df["name"].apply((lambda x: group_alphabet(x,num_groups)))
	grouped_df = df.groupby(["alph_group", "year"], as_index=False).sum()
	p = grouped_df.pivot(index="year", columns="alph_group", values="percent")
	plt.close()
	p.plot()
	plt.savefig("alphabet_groups_"+str(num_groups)+".png", format="png")

def plot_first_letter_name_freq(df):
	""" stats based on first name's first letter and name's length
	"""
	df["first"] = df["name"].apply(first_letter)

	# all trends
	grouped_df = df.groupby(["first", "year"], as_index=False).sum()
	p = grouped_df.pivot(index="year", columns="first", values="percent")
	fig = plt.figure()
	gs = gridspec.GridSpec(5,6)

	idx = 0
	for c in p.columns:
		ax = fig.add_subplot(gs[idx/6,idx%6])
		ax.plot(p.index.values, p[c], linewidth=2)
		ax.set_title(c)
		ax.set_xticklabels([])
		ax.set_yticklabels([])
		idx = idx + 1
	#p.plot(y="b")
	fig.savefig("all_trends.png", format="png")
	#plt.show()

	# save all separately
	sns.set_style("darkgrid")
	#ensure directory is created
	dir_name = "separate_trends"
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)

	for c in p.columns:
		plt.close()
		plt.plot(p.index.values, p[c])
		plt.title("Names starting with: " + c)
		plt.savefig(dir_name+"/"+c+".png", format="png")

	#all in one
	plt.close()
	p.plot()
	plt.title("All In One")
	plt.savefig("all_in_one.png", format="png", dpi=200)


	# group alphabets
	[plot_by_alphabet_groups(df, x) for x in range(2,5)]

	# group by name length
	df["name_len"] = df["name"].apply((lambda x: len(x)))
	grouped_df = df.groupby(["name_len", "year"], as_index=False).sum()
	p = grouped_df.pivot(index="year", columns="name_len", values="percent")
	min_len = min(df["name_len"])
	max_len = max(df["name_len"])
	styles = ["-", "--", "-.", ":"]
	linestyles = [styles[i%len(styles)] for i in range(min_len, max_len + 1)]
	plt.close()
	p.plot(label=p.columns, style=linestyles)
	plt.title("popularity by length of name")
	plt.savefig("length.png", format="png", dpi=200)


def extract_origin(name, dir_name):
	""" makes request to the BTN's server and parses the xml response
	"""
	url = URL_FORMAT.format(name)
	r = requests.get(url)
	f = open("{}/{}.xml".format(dir_name, name), "w")
	xml = r.text.encode('utf-8').strip()
	obj = untangle.parse(xml)
	if hasattr(obj.response, "error_code"):
		code = obj.response.error_code.cdata
		error = obj.response.error.cdata
		return code, error,  0
	else:
		f.write(xml)
		f.close()
		if "Biblical" in xml:
			return 1111, None, 1
		else:
			return 1111, None, 0

def scrape_between_the_name(df):
	""" scrapes the web site and persists xml files and a consolidated csv files of results
	"""
	# extract origin biblical/non-biblical
	dir_name = "btn_data"
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)
	uniques = df.name.unique()
	
	f = open("biblical_names.csv", "w")
	f.write("name,is_biblical\n")
	retry_list = []
	biblical_names = []

	for u in uniques:
		(error_code, error, is_biblical) = extract_origin(u, dir_name)
		if error_code == 1111:
			f.write("{},{}\n".format(u,is_biblical))
			if is_biblical:
				biblical_names.append(u)
		elif error_code == 50:
			print "info not found: ",u
		else:           # put in retry list
			print "Failed: ", u, error_code, error
			retry_list.append(u)

	# retry
	for u in retry_list:
		(error_code, error, is_biblical) = extract_origin(u, dir_name)
		if error_code == 1111:
			f.write("{},{}".format(u,is_biblical))
			if is_biblical:
				biblical_names.append(u)

	f.close()

	print biblical_names
	print "Total biblical names:", len(biblical_names)


if __name__ == "__main__":

	df = pd.read_csv('baby-names.csv')

	df_boy = df[df['sex'].isin(["boy"])]
	df_girl = df[df['sex'].isin(["girl"])]
	#plot_first_letter_name_freq(df_boy)

	unique_names(df_boy)
	plot_name_popularity(df, "Tyler", "boy", False)
	print "Unique names (boys):", len(df[df["sex"] == "boy"].name.unique())
	print "Unique names (girls):", len(df[df["sex"] == "girl"].name.unique())

	# scrape
	if SCRAPE_BTN:
		scrape_between_the_name(df)




