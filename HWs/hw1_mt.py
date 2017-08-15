from bs4 import BeautifulSoup
import urllib2
import urllib
import re, os
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import PorterStemmer
from nltk.stem.snowball import EnglishStemmer
import string
import csv


# PROBLEM 1
# Get document and get the soup
web_address='/Users/michelletorres/Documents/GitHubReps/WUSTL/Debate1.html'
web_page = urllib.urlopen(web_address)
soup = BeautifulSoup(web_page.read(), 'lxml')
soup.prettify()

# a. What tags can you use to identify statements?
# <p>

# b/c. Devise a rule to assign the unlabeled statements to speakers.
statements = [x.text for x in soup.find_all('p') if x.text!=""]
is_lehrer_mentions = ['LEHRER:' in x for x in statements]
start = is_lehrer_mentions.index(True)
new_statements = []
speakers_ls = []
speaker = ''
for p in range(start,len(statements)-2):
	#if p !='(APPLAUSE)' and p!='(CROSSTALK)' and p!='(CROSSTALK)':
	check = re.search('^(OBAMA:)|(ROMNEY:)|(LEHRER:)', statements[p])
	if check is not None:
		if check.group(0)==speaker:
			new_statements[-1] = new_statements[-1]+" "+re.sub('^(OBAMA:)|(ROMNEY:)|(LEHRER:)', '',statements[p])
		else:
			new_statements.append(re.sub('^(OBAMA:)|(ROMNEY:)|(LEHRER:)', '',statements[p]))
			speaker = check.group(0)
			speakers_ls.append(speaker)
	else:
		new_statements[-1] = new_statements[-1]+" "+statements[p]

new_statements = [re.sub('(\(LAUGHTER\))|(\(CROSSTALK\))|(\(APPLAUSE\))', ' ',x) for x in new_statements]


# PROBLEM 2
# a. Load the positive and negative words into python
pos = urllib.urlopen('http://www.unc.edu/~ncaren/haphazard/positive.txt').read().split('\n')
neg = urllib.urlopen('http://www.unc.edu/~ncaren/haphazard/negative.txt').read().split('\n')

# b. Use the porter, snowball and lancaster stemmers from the nltk package to create stemmed versions of the dictionaries.
st = LancasterStemmer()
pt = PorterStemmer()
sb = EnglishStemmer()

# Positive
pos_lan = list(set([st.stem(x) for x in pos]))
pos_port = list(set([pt.stem(x) for x in pos]))
pos_sb = list(set([sb.stem(x) for x in pos]))

# Negative
neg_lan = list(set([st.stem(x) for x in neg]))
neg_port = list(set([pt.stem(x) for x in neg]))
neg_sb = list(set([sb.stem(x) for x in neg]))

# c. Create dataset

# Stopwords
stop_link = urllib.urlopen('http://www.lextek.com/manuals/onix/stopwords1.html').read()
stop_soup = BeautifulSoup(stop_link, 'lxml')
stop_words = [x for x in stop_soup.find('pre').text.split('\n')[12:] if x!=""]

def getInfo(text, statements, speakers, stopwords, posdics, negdics):
	number = statements.index(text) # Statement number
	speaker = speakers[number] # Speaker
	# Clean text
	item = text.lower() # Not capital
	item = re.sub('[^0-9a-zA-Z ]', '', item) # Remove punctuation
	item = item.split(' ') # Create a list of words
	clean = [x for x in item if x not in stopwords] 
	nclean = len(clean) #Number of non-stop words spoken
	removed = [x for x in item if x not in clean]
	clean2 = " ".join(clean)
	# Get counts
	pwords = [x for x in clean if x in posdics[0]]
	n_pwords = len(pwords) # Number of positive words
	nwords = [x for x in clean if x in negdics[0]]
	n_nwords = len(nwords) # Number of negative words
	lan_pwords = [st.stem(x) for x in clean if x in posdics[1]]
	n_lan_pwords = len(lan_pwords) # Number of positive words (Lancaster stemmer)
	lan_nwords = [st.stem(x) for x in clean if x in negdics[1]]
	n_lan_nwords = len(lan_nwords) # Number of negative words (Lancaster stemmer)
	port_pwords = [pt.stem(x) for x in clean if x in posdics[2]]
	n_port_pwords = len(port_pwords) # Number of positive words (Porter stemmer)
	port_nwords = [pt.stem(x) for x in clean if x in negdics[2]]
	n_port_nwords = len(port_nwords) # Number of negative words (Porter stemmer)
	sb_pwords = [sb.stem(x) for x in clean if x in posdics[3]]
	n_sb_pwords = len(sb_pwords) # Number of positive words (Snowball stemmer)
	sb_nwords = [sb.stem(x) for x in clean if x in negdics[3]]
	n_sb_nwords = len(sb_nwords) # Number of negative words (Snowball stemmer)
	# Dictionary
	mydic = {'number':number, 'speaker':speaker,
	'num_nonstop': nclean, 'num_poswords':n_pwords, 'num_negwords':n_nwords,
	'num_poswords_lan': n_lan_pwords, 'num_negwords_lan': n_lan_nwords,
	'num_poswords_port': n_port_pwords, 'num_negwords_port': n_port_nwords,
	'num_poswords_sb': n_sb_pwords, 'num_negwords_sb': n_sb_nwords}
	return(mydic)

x= new_statements[1]
getInfo(x, new_statements, speakers_ls, stop_words, [pos,pos_lan,pos_port, pos_sb],[neg, neg_lan, neg_port, neg_sb])


with open('/Users/michelletorres/Documents/GitHubReps/WUSTL/HWs/statements_data.csv','wb') as f:
	my_writer = csv.DictWriter(f, fieldnames=("number", "speaker", "num_nonstop", "num_poswords", "num_negwords",
		"num_poswords_lan", "num_negwords_lan", "num_poswords_port", "num_negwords_port", "num_poswords_sb", "num_negwords_sb"))
	my_writer.writeheader()
	for state in new_statements:
		temp_dict = getInfo(state, new_statements, speakers_ls, stop_words, [pos,pos_lan,pos_port, pos_sb],[neg, neg_lan, neg_port, neg_sb])
		my_writer.writerow(temp_dict)
