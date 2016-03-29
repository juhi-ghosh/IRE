from nltk.corpus import sentiwordnet as swn
import aspect_term
from textblob import TextBlob

# POS tags
# pos : Syntactic category: n for noun files, v for verb files, a for adjective files, r for adverb files. 

def main():
	# input is of the form = [[{k1: ['a1',a2']}, {k2: ['a1',a2]}]]
	# NN_JJ = raw_input()
	NN_JJ = aspect_term.main()
	#print NN_JJ
	for each_sentence in NN_JJ:
		print
		for each_term in each_sentence:
			if each_term != []:
				# print each_term
				for key, value in each_term.iteritems():
					#print key, 
					"""pos_score = 0
					neg_score = 0"""
					score = 0

					print key, ":",

					if value != []:
						for each_value in value:
							print each_value,
							
							sentiment = TextBlob(each_value).sentiment.polarity
							score = score + sentiment

							# for senti wordnet
							"""word = list(swn.senti_synsets(each_value)) 
							pos_score = pos_score + word[0].pos_score()
							neg_score = neg_score + word[0].neg_score()"""
				
					else:

						"""	pos_score = 0
						neg_score = 0 """
						if score == 0:
							print "----"
							break

					'''if pos_score > neg_score:
						print "is POSITIVE", pos_score
					else:
						print "is NEGATIVE", neg_score'''
					if score > 0:
						print "POSITIVE", score
					else:
						print "NEGATIVE", score

			else:
				continue


if __name__ == '__main__':
	main()