import sys
from collections import OrderedDict

import aspect_term
import parser
from textblob import TextBlob
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='\t')


def main():

	all_sentences = parser.getSentences(sys.argv[1])
	i = 0
	
	#input is of the form = [[{k1: ['a1',a2']}, {k2: ['a1',a2]}]]
	NN_JJ = aspect_term.main()

	top = Element('sentences')	#opens tag <sentences>
	
	for each_sentence in NN_JJ:
		
		if len(all_sentences[i][1]) == 0:
			i = i+1
			continue

		data = {'id':'' ,'text':'', 'aspect_term':'', 'polarity':'', 'from':'', 'to':''}

		data['id'] = all_sentences[i][0]
		data['text'] = all_sentences[i][1]

		i = i+1

		child_sent = SubElement(top, 'sentence', {'id':data['id']})	#opens tag <sentence>
		child_text = SubElement(child_sent, 'text') #opens tag <text>
		child_text.text = data['text']	#writes the sentence in <text>....</text>

		child_aspect_terms = SubElement(child_sent, 'aspectTerms')	#opens tag <aspectTerms>

		#print each_sentence
		if each_sentence == []:
				child_aspect_terms.text = '\n\t\t'
				aspect_cat = SubElement(child_sent, 'aspectCategories')
				aspect_cat.text = '\n\t\t'
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
				else:
					score = 0	# if no adjective for aspect => score=0

				data['aspect_term'] = aspect

				if score > 0:
					data['polarity'] = "positive"
				elif score < 0:
					data['polarity'] = "negative"
				else:
					data['polarity'] = "neutral"
				
				# assign values 'from' and 'to'
				if score != 0:
					data['from'] = int(score * 100 - 10)
					data['to'] = int(score * 100 + 10)
				else:
					data['from'] = int(score)
					data['to'] = int(score)

				child_aspect_term = SubElement(child_aspect_terms, 'aspectTerm', 
								{'term':data['aspect_term'],
								 'polarity':data['polarity'],
								 'from':str(data['from']),
								 'to':str(data['to']) })	#opens tag <aspectTerm>

				child_aspect_terms.extend(child_aspect_term)

		aspect_cat = SubElement(child_sent, 'aspectCategories')
		aspect_cat.text = '\n\t\t'
		# prints the entire xml file
		if (i == len(all_sentences)-1):
			print prettify(top)
			

if __name__ == '__main__':
	main()

#create a csv file and read into an xml file