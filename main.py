import sys
import getopt
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import urllib
import pprint
from NLPCore import NLPCoreClient
import operator

def main():

	# r: relation to extract. t: extraction confidence threshold.
	# q: seed query. k: the number of tuples required.
	client_key = sys.argv[1]
	engine_key = sys.argv[2]
	r = sys.argv[3]
	t = sys.argv[4]
	q = sys.argv[5]
	k = sys.argv[6]

	print('Parameters:')
	print('Client key  = ' + client_key)
	print('Engine key  = ' + engine_key)
	print('Relation    = ' + r)
	print('Threshold   = ' + t)
	print('Query       = ' + q)
	print('# of Tuples = ' + k)

	# client_key = "AIzaSyCX8KognQPauqFUOCMxZL9AMgzFyHZAqVg"
	# engine_key = '013766798457561572077:h1lapoxu5aq'
	# r = 4
	# t = 0.35
	# q = "bill gates microsoft" 
	# k = 15

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

	iteration = 1
	while True:
		print '========== Iteration: ' + str(iteration) + ' - Query: ' + q + ' ========== '
		res = service.cse().list(
			q=q,
			cx=engine_key,
		).execute()

		for i,item in enumerate(res['items']):
			print 'Processing URL: '+item['formattedUrl']

			# Extract actual plain text from webpage.
			# For webpage unable to retreive, skip it and move on.
			try:
				if item['link'] not in seenURL:
					page = urllib.urlopen(item['link'])
					seenURL.append(item['link'])
				else:
					continue
			except:
				continue

			soup = BeautifulSoup(page, 'html.parser')

			text = []

			nonBreakSpace = u'\xa0'

			for header in soup.find_all(['h1', 'h2', 'h3',]):
				tmp = header.get_text().replace(nonBreakSpace,' ')
				text.append(tmp.strip().encode("ascii", "ignore")+'.')
			for p in soup.find_all(['p']):
				tmp = p.get_text().replace(nonBreakSpace,' ')
				text.append(tmp.strip().encode("ascii", "ignore")+'.')

			# 1st pipeline: tag name entities for webpage.
			# Identify sentences containing name entities for processed relation. 
			client = NLPCoreClient('/Users/wanheng/Desktop/adb/P2/stanford-corenlp-full-2017-06-09')
			properties = {
				"annotators": "tokenize,ssplit,pos,lemma,ner", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=text, properties=properties)
			
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

			text2 = []
			relations = {1 : ['PERSON', 'LOCATION]'],
						 2 : ['LOCATION', 'LOCATION'],
						 3 : ['ORGANIZATION', 'LOCATION'],
						 4 : ['PERSON', 'ORGANIZATION']}
			for j,sen in enumerate(document):
				if r == 1 and relations[r][0] in NER[j] and relations[r][1] in NER[j]:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 2 and 'LOCATION' in NER[j] and NER[j]['LOCATION']>=2:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 3 and 'ORGANIZATION' in NER[j] and 'LOCATION' in NER[j]:
					text2.append(sen.encode("ascii", "ignore"))
				if r == 4 and relations[r][0] in NER[j] and relations[r][1] in NER[j]: 
					text2.append(sen.encode("ascii", "ignore"))

			# 2nd pipeline: exist of relation type and extraction confidence.
			properties = {
				"annotators": "tokenize,ssplit,pos,lemma,ner,parse,relation", #Second pipeline; leave out parse,relation for first
				"parse.model": "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", #Must be present for the second pipeline!
				"ner.useSUTime": "0"
				}
			doc = client.annotate(text=text2, properties=properties)
			relation = 'Work_For'
			relation_overall = 0
			relation_cnt = 0
			for it,i in enumerate(doc.sentences):		
				tup = ('','')
				tup_type = ('', '')
				score = 0
				
				for j in i.relations:
					if j:
						# and float(j.probabilities[relation]) > t
						if max(j.probabilities.iteritems(), key=operator.itemgetter(1))[0] == relation:
							relation_overall += 1
							# if float(j.probabilities[relation]) > score:
							score = float(j.probabilities[relation])
							#print type(j.probabilities[relation])
							if r == 1 and [j.entities[0].type, j.entities[1].type] == ['PEOPLE','LOCATION']:
								if j.entities[0].type == 'PEOPLE':
									tup = (j.entities[0].value,j.entities[1].value)
									tup_type = (j.entities[0].type,j.entities[1].type)
								else:
									tup = (j.entities[1].value,j.entities[0].value)
									tup_type = (j.entities[1].type,j.entities[0].type)
							if r == 3 and [j.entities[0].type, j.entities[1].type] == ['ORGANIZATION','LOCATION']:
								if j.entities[0].type == 'ORGANIZATION':
									tup = (j.entities[0].value,j.entities[1].value)
									tup_type = (j.entities[0].type,j.entities[1].type)
								else:
									tup = (j.entities[1].value,j.entities[0].value)
									tup_type = (j.entities[1].type,j.entities[0].type)
							if r == 4 and [j.entities[0].type, j.entities[1].type] == ['PEOPLE','ORGANIZATION']:
								if j.entities[0].type == 'ORGANIZATION':
									tup = (j.entities[0].value,j.entities[1].value)
									tup_type = (j.entities[0].type,j.entities[1].type)
								else:
									tup = (j.entities[1].value,j.entities[0].value)
									tup_type = (j.entities[1].type,j.entities[0].type)
							if r == 2 and j.entities[0].type == 'LOCATION' and j.entities[1].type == 'LOCATION':
								tup = (j.entities[0].value,j.entities[1].value)
								tup_type = (j.entities[0].type,j.entities[1].type)

							if tup != ('', '') :
								if tup not in X:
									relation_cnt += 1
									X[tup] = score
									print '================= EXTRACTED RELATION ================='
									print 'Sentence: ' + text2[it]
									print 'RelationType: ' + relation + ' | Confidence= ' + str(score) \
									+' | EntityType1= ' + tup_type[0] + ' | EntityValue1= ' + tup[0] \
									+' | EntityTpye2= ' + tup_type[1] + ' | EntityValue2= ' + tup[1]
									print '================= END OF RELATION DESC ==============='
								else:
									X[tup] = max(score, X[tup])

			print 'Relations extracted from this website: ' + str(relation_cnt) + ' (Overall: ' + str(relation_overall) + ')'
			print '----------------------------------------------------'


		# Remove tuples with confidence below threshold.
		print 'pruning relations below threshold'
		Z = {}
		for tup, value in X.iteritems():
			if value > t:
				Z[tup] = value
		X = Z
		print 'Number of tuples after pruning: ' + str(len(X))
		

		print '================= ALL RELATIONS ================='
		flag = False
		if len(X) >= k:
			c = 0
			for tup, value in sorted(X.iteritems(), key=lambda (k,v): (v,k),reverse = True):
				print 'RelationType: ' + relation + ' | Confidence= ' + str(value) \
				+' | Entity #1: ' + tup[0] + '(' + relations[r][0] + ')' \
				+' | Entity #2: ' + tup[1] + '(' + relations[r][1] + ')'
   				c += 1
   				if c >= k :
   					return 
   		else: 
   			for tup, value in sorted(X.iteritems(), key=lambda (k,v): (v,k),reverse = True):
   				print 'RelationType: ' + relation + ' | Confidence= ' + str(value) \
				+' | Entity #1: ' + tup[0] + '(' + relations[r][0] + ')' \
				+' | Entity #2: ' + tup[1] + '(' + relations[r][1] + ')'
   				if tup not in seenQuery:
   					if flag == False:
						q = tup[0] + ' ' + tup[1]
						flag = True
   					seenQuery.append(q)
   			if flag == False:
   				break

   		iteration += 1
   		print '-*-*-*- NEXT ITERATION -*-*-*-'
if __name__ == '__main__':
	main()