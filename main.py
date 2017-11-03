import sys
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import urllib
import pprint
from NLPCore import NLPCoreClient
import operator

def main():


	client_key = "AIzaSyAPbX4JVlc8waFre4Zve1v8zx1VSfhijIk"
	engine_key = '008083549322187859573:yubw3z65huy'
	r = 4
	t = 0.45
	q = "bill gates microsoft" 
	k = 10

	if r == 1:
		relation = 'Live_In'
	if r == 2:
		relation = 'Located_In'
	if r == 3:
		relation = 'OrgBased_In'
	if r == 4:
		relation = 'Work_For'


	X = {}
	Y = {}
	seenURL = []
	seenQuery = []

	service = build("customsearch", "v1",
			developerKey=client_key)

	while True:


		res = service.cse().list(
			q=q,
			cx=engine_key,
		).execute()

		for i,item in enumerate(res['items']):

	#	for a in ['']:
	#		item = res['items'][0]
	#		i = 0
			
	#		print 'Result '+str(i+1)
	#		print '['
			print ' URL: '+item['formattedUrl']
	#		print ' Title: '+BeautifulSoup(item['htmlTitle'], "html.parser").text
	#		print ' Description: '+BeautifulSoup(item['htmlSnippet'], "html.parser").text
	#		print ']'
	#		print ''

	#		print item['formattedUrl'][:7]
	#		if item['formattedUrl'][:7] != 'http://' and item['formattedUrl'][:8] != 'https://' :
	#			item['formattedUrl'] = 'http://' + item['formattedUrl']
			try:
				if item['link'] not in seenURL:
					page = urllib.urlopen(item['link'])
					seenURL.append(item['link'])
				else:
					continue
			except:
				continue

			#page = urllib.urlopen('https://en.wikipedia.org/wiki/Bill_Gates')

			soup = BeautifulSoup(page, 'html.parser')

			text = []

			nonBreakSpace = u'\xa0'

			for header in soup.find_all(['h1', 'h2', 'h3',]):
				tmp = header.get_text().replace(nonBreakSpace,' ')
				text.append(tmp.strip().encode("ascii", "ignore")+'.')
			for p in soup.find_all(['p']):
				tmp = p.get_text().replace(nonBreakSpace,' ')
				text.append(tmp.strip().encode("ascii", "ignore")+'.')
	#		for tr in soup.find_all('tr'):
	#			tmp = ""
	#			tds = tr.find_all('td')
	#			for ele in tds:
	#				tmp += ele.text.strip().encode("ascii", "ignore")
	#			tmp += '.'
	#			text.append(tmp)
	#			print '-=-=-' + tmp

			client = NLPCoreClient('/Users/yibo/Work/ADB Project2/stanford-corenlp-full-2017-06-09')
			properties = {
				"annotators": "tokenize,ssplit,pos,lemma,ner", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=text, properties=properties)
			
			#print(doc.sentences[0].relations[0])
			NER = []
			document = []
			for i in doc.sentences:
				newsentence = ''
				tmp = {}
				for x in i.tokens:
					newsentence += ' '  + x.word
					if x.ner not in tmp:
						tmp[x.ner] = 1
					else:
						tmp[x.ner] += 1
				NER.append(tmp)
				document.append(newsentence)
	#			print newsentence
	#			print tmp
			#print '--------------------------------'
			text2 = []
			for j,sen in enumerate(document):
				if r == 1 and 'PERSON' in NER[j] and 'LOCATION' in NER[j]:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 2 and 'LOCATION' in NER[j] and NER[j]['LOCATION']>=2:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 3 and 'ORGANIZATION' in NER[j] and 'LOCATION' in NER[j]:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 4 and 'PERSON' in NER[j] and 'ORGANIZATION' in NER[j]: 
					text2.append(sen.encode("ascii", "ignore"))
	#		print text2
	#		print len(text2)

			#print '--------------------------------'

			properties = {
				"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=text2, properties=properties)
			for it,i in enumerate(doc.sentences):
				
				tup = ('','')
				score = 0
				for j in i.relations:
					if j:
						if max(j.probabilities.iteritems(), key=operator.itemgetter(1))[0] == relation and float(j.probabilities[relation]) >  t:
	#						print j 
							if float(j.probabilities[relation]) > score:
								score = float(j.probabilities[relation])
								#print type(j.probabilities[relation])
								if r == 1:
									if j.entities[0].type == 'PEOPLE':
										tup = (j.entities[0].value,j.entities[1].value)
									else:
										tup = (j.entities[1].value,j.entities[0].value)
								if r == 3:
									if j.entities[0].type == 'ORGANIZATION':
										tup = (j.entities[0].value,j.entities[1].value)
									else:
										tup = (j.entities[1].value,j.entities[0].value)
								if r == 4:
									if j.entities[0].type == 'ORGANIZATION':
										tup = (j.entities[0].value,j.entities[1].value)
									else:
										tup = (j.entities[1].value,j.entities[0].value)
								if r == 2:
									tup = (j.entities[0].value,j.entities[1].value)
								if j.entities[0].value not in Y:
									Y[j.entities[0].value] = j.entities[0].type
								if j.entities[1].value not in Y:
									Y[j.entities[1].value] = j.entities[1].type
				if tup != ('',''):
					print text2[it]
					print tup[0]+'('+Y[tup[0]]+')'+'	'+tup[1]+'('+Y[tup[1]]+')'
					print score
					if tup not in X:
						X[tup] = score
					else:
						X[tup] = max(score,X[tup])
					print '--------------------------------'
			print '========================'

		if len(X) >= k:
			c = 0
			for tup, value in sorted(X.iteritems(), key=lambda (k,v): (v,k),reverse = True):
				print tup[0]+'('+Y[tup[0]]+')'+'	'+tup[1]+'('+Y[tup[1]]+'):   '+str(value)
   				c += 1
   				if c >= k :
   					return 
   		else: 
   			for tup, value in sorted(X.iteritems(), key=lambda (k,v): (v,k),reverse = True):
   				if tup not in seenQuery:
   					q = tup[0] + ' ' + tup[1]
   					seenQuery.append(q)

   		print '-*-*-*- NEXT ITERATION'
if __name__ == '__main__':
	main()