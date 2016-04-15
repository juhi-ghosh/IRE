import sys

import aspect_term1
import parser
import cat_det

from textblob import TextBlob
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from nltk.corpus import wordnet as wn

from aspect_term_out import NN_JJ
from all_sentences_out import all_sentences

categories = cat_det.main()

synset_categories = {'price' : wn.synsets('price')[0],
					 'food' : wn.synsets('food')[0],
					 'ambience' : wn.synsets('ambience')[0],
					 'service' : wn.synsets('service')[0]}

# weight, price, appearance, functionality, behavior, performance, quality, size
# food", "service", "price", "ambience", "anecdotes/miscellaneous".

# price = price
# food = quality 
# service = functionality, behavior, performance
# ambience = weight, appearance, size


# find out the similarity score between aspect term and the category
def detect_similarity(term):
	
	#print
	#print value, wn.synsets(value)[0]
	try:
		wn_term = wn.synsets(term)[0]
	except:
		#print term
		return

	max_score = -100
	max_sim = ''
	for cat, value in synset_categories.iteritems():
		sim_score = wn.wup_similarity(wn_term, value)
		#print cat, term, sim_score
		if sim_score > max_score:
			max_score = sim_score
			max_sim = cat

	temp = []
	temp.append(max_sim)
	temp.append(max_score)

	if temp[1] >= 0.5:
		return temp
	else:
		return


# find the category depending on the adjective
def detect_aspect_cat(value):
	cat = []
	if value in categories['price']:
		cat.append("price")
	if value in categories['quality']:
		cat.append("food")
	if value in categories['functionality'] or value in categories['behavior'] or value in categories['performance']:
		cat.append("service")
	if value in categories['weight'] or value in categories['appearance'] or value in categories['size']:
		cat.append("ambience")
	if cat == []:
		cat.append("anecdotes/miscellaneous")

	return cat



def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='\t')


def main():

	# all_sentences = parser.getSentences(sys.argv[1])
	i = 0
	
	# input is of the form = [[{k1: ['a1',a2']}, {k2: ['a1',a2]}]]
	# NN_JJ = aspect_term1.main()

	top = Element('sentences')	#opens tag <sentences>
	
	for each_sentence in NN_JJ:
		#print all_sentences[i]

		if len(all_sentences[i][1]) == 0:
			i = i+1
			continue

		data = {'id':'' ,'text':'', 'aspect_term':'', 'polarity':'', 'from':'', 'to':''}

		data['id'] = str(all_sentences[i][0])
		data['text'] = str(all_sentences[i][1])

		i = i+1

		child_sent = SubElement(top, 'sentence', {'id':data['id']})	#opens tag <sentence>
		child_text = SubElement(child_sent, 'text') #opens tag <text>
		child_text.text = data['text']	#writes the sentence in <text>....</text>

		child_aspect_terms = SubElement(child_sent, 'aspectTerms')	#opens tag <aspectTerms>
		child_aspect_cats = SubElement(child_sent, 'aspectCategories')	#opens tag <aspectCategories>

		# intialize aspect category of the sentence as []
		aspect_cat_sent = {'food':[], 'service':[], 'ambience':[], 'price':[], 'anecdotes/miscellaneous':[]}
		category_polarity = {}	# for category polarity

		#print each_sentence
		if each_sentence == []:
				child_aspect_terms.text = '\n\t\t'
				child_aspect_cat= SubElement(child_aspect_cats, 'aspectCategory',
								{'category':'anecdotes/miscellaneous',
								 'polarity':'neutral'})
				#child_aspect_cats.text = '\n\t\t'
				continue

		for each_term in each_sentence:
			for aspect, value in each_term.iteritems():

				score = 0
				aspect_terms = ''

				# find the score of each aspect
				if value != []:
					for each_value in value:
						aspect_terms = aspect_terms + each_value

						sentiment = TextBlob(each_value).sentiment.polarity
						score = score + sentiment

						# find the category depending on the adjective
						aspect_cat = detect_aspect_cat(each_value)
						for each_cat in aspect_cat:
								aspect_cat_sent[each_cat].append(score)
								
				else:
					aspect_cat = ['anecdotes/miscellaneous']	# if does not belong to any category
					score = 0	# if no adjective for aspect => score=0

				data['aspect_term'] = aspect

				# find out the similarity depending on the aspct term and category
				
				x = detect_similarity(aspect)
				# print "xxxxxxxxxxxx",x
				if x != None:
					similar_category, similar_score = x[0], x[1]
					#print similar_category, similar_score, aspect_cat_sent[similar_category], score
					aspect_cat_sent[similar_category].append(score)

				if score > 0:
					data['polarity'] = "positive"
				elif score < 0:
					data['polarity'] = "negative"
				else:
					data['polarity'] = "neutral"


				# detect polarity of category
				# print aspect_cat_sent
				for cat, score in aspect_cat_sent.iteritems():
					if aspect_cat_sent[cat] != []:
						# print aspect_cat_sent[cat]
						total_score = sum(aspect_cat_sent[cat])
						if total_score > 0:
							category_polarity[cat] = 'positive'
						elif total_score < 0:
							category_polarity[cat] = 'negative'
						else:
							category_polarity[cat] = 'neutral'

				
				# assign values 'from' and 'to'
				# print "text:", data['text'], data['aspect_term']
				try:
					data['from'] = data['text'].index(data['aspect_term'])
					data['to'] = data['from'] + len(data['aspect_term'])
				except:
					pass
				
				child_aspect_term = SubElement(child_aspect_terms, 'aspectTerm', 
								{'term':data['aspect_term'],
								 'polarity':data['polarity'],
								 'from':str(data['from']),
								 'to':str(data['to']) })	#opens tag <aspectTerm>

				child_aspect_terms.extend(child_aspect_term)

		# print aspect_cat_sent
		# print category_polarity
		for key, value in category_polarity.iteritems():
			child_aspect_cat= SubElement(child_aspect_cats, 'aspectCategory',
							{'category':key,
							 'polarity':value })

			child_aspect_cats.extend(child_aspect_cat)

		#child_aspect_cat.text = '\n\t\t'
		# prints the entire xml file
		if (i == len(all_sentences)-1):
			#print i
			print prettify(top)
			

if __name__ == '__main__':
	main()