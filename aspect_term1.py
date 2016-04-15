import sys
from parser import getSentences, getAspectTermsDict
from nltk.tokenize import word_tokenize
import os
import nltk

def detect_quality(term,data,JJ_list,mydict,depth,key):
	if depth==2:
		mydict[key] = list(set(mydict[key]))
		return mydict
	for relation in data:
		if(len(relation)>=5):
			if(relation[2].split('-')[0]==term):
				if (relation[4].split('-')[0] in JJ_list):
					mydict[key].append(relation[4].split('-')[0])
				detect_quality(relation[4].split('-')[0],data,JJ_list,mydict,depth+1,key)
			elif(relation[4].split('-')[0]==term):
				if(relation[2].split('-')[0] in JJ_list):
					mydict[key].append(relation[2].split('-')[0])
				detect_quality(relation[2].split('-')[0],data,JJ_list,mydict,depth+1,key)

	mydict[key] = list(set(mydict[key]))
	return mydict

def findvblist(sentence):
	# token = nltk.word_tokenize(sentence)
	# tagged_list = nltk.pos_tag(token)
	sent = ""
	token = sentence.split(" ")
	f = open('stopwords.txt','r')
	stopwords = []
	for line in f:
		stopwords.append(line)
	for i in range(len(stopwords)):
		stopwords[i] = stopwords[i].replace('\n','')
	# print stopwords
	for word in token:
		if word not in stopwords:
			sent = sent+word
			sent = sent+" "
	sent.strip()
	token = nltk.word_tokenize(sent)
	tagged_list = nltk.pos_tag(token)
	# print tagged_list
	vblist = []
	for tags in tagged_list:
		if (tags[1]=='VB' or tags[1]=='VBD' or tags[1]=='VBG' or tags[1]=='VBN' or tags[1]=='VBP'
		or tags[1]=='VBZ'):
			vblist.append(tags[0])

	return vblist

def detect_terms(temp,sentence,nnlist):
	aspect_term = []
	for relation in temp:
		if relation[0]=='amod':
			aspect_term.append(relation[2].split('-')[0])
		if (relation[0]=='acomp' or relation[0]=='xcomp' or relation[0]=='nmod' or relation[0]=='dobj'
		or relation[0]=='nsubj' or relation[0]=='nsubjpass' or relation[0]=='xcomp' 
		or relation[0]=='pobj' or relation[0]=='abbrev'):
			aspect_term.append(relation[4].split('-')[0])
	# print aspect_term
	aspect_term = list(set(aspect_term))
	for term in aspect_term:
		if term not in nnlist:
			aspect_term.remove(term)
	for relation in temp:
		if relation[0]=='conj' and relation[2].split('-')[0] in aspect_term:
			aspect_term.append(relation[4].split('-')[0])
	aspect_term = list(set(aspect_term))
	return aspect_term

def main():
	# f1 = open('small_out4.txt','r')
	# f2 = open('small_out3.txt','r')
	sentence_list = []
	aspect_term = []
	aspect_term = getAspectTermsDict(sys.argv[1])
	sentence_list = getSentences(sys.argv[1])
#	print len(sentence_list)
	fp1 = open('all_sentences_out.py','w')
	fp1.write("all_sentences = ")
	fp1.write(str(sentence_list))
	fp1.close()

	fp = open('aspect_term_out.py','w')

	aspect_terms = []
	# print len(sentence_list)
	for i in range(len(sentence_list)): 
		sentence = sentence_list[i][1]

		#print str(i) + " " + str(len(sentence_list))
		pos_list = aspect_term[i]
		temp = []
		terms = []

		os.popen("echo '"+sentence+"' > ./stanford-parser-full/stanfordtemp.txt")
		parser_out = os.popen("./stanford-parser-full/lexparser.sh ./stanford-parser-full/stanfordtemp.txt")

		#os.popen("echo '"+sentence+"' > ~/stanford-parser-full-2015-04-20/stanfordtemp.txt")
		#parser_out = os.popen("~/stanford-parser-full-2015-04-20/lexparser.sh ~/stanford-parser-full-2015-04-20/stanfordtemp.txt")
		for relation in parser_out:
			relation = word_tokenize(relation)

			#fp.write(str(relation) + '\n')

			if(len(relation)!=0):
				temp.append(relation)
		
		x = detect_terms(temp,sentence,pos_list[0])
		JJ_list = pos_list[1]
		if len(JJ_list)==0:
			JJ_list = findvblist(sentence)
		for term in x:
			mydict = {}
			mydict[term] = []
			terms.append(detect_quality(term,temp,JJ_list,mydict,0,term))
		# for term in pos_list[0]:
		# 	terms.append(detect(term,temp,pos_list[1]))

		aspect_terms.append(terms)


	fp.write("NN_JJ = [")
	for item in range(len(aspect_terms)):
		fp.write(str(aspect_terms[item])+",")
	fp.write("]")
	fp.close()
	return aspect_terms

if __name__ == '__main__':
	main()