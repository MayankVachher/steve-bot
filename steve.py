import spacy
from dateparser import parse
nlp = spacy.load('en')
import string

def deduce_action(sentence):
	l_sentences = []
	i_pos = 0
	e_pos = 0
	
	while e_pos < len(sentence):
		if sentence[e_pos] in ('.', '!', '?'):
			l_sentences.append(sentence[i_pos:e_pos+1].strip())
			i_pos = e_pos + 1
		e_pos += 1
	if e_pos != i_pos:
		l_sentences.append(sentence[i_pos: e_pos+1].strip())
	
	result = []
	for x in l_sentences:
		result.append(action_per_sentence(x))
	
	return result

def action_per_sentence(sentence):
	
	doc = nlp(sentence)
	
	result_dict = {}
	compound_flag = False
	result_dict['what'] = None
	result_dict['punct'] = None
	result_dict['question'] = False
	q = []
	for token in doc:
		if token.dep_ == 'ROOT':
			result_dict['action'] = ' '.join(q + [token.lemma_])
		elif token.dep_ == 'dobj':
			result_dict['what'] = ' '.join(q + [token.text])
		elif token.dep_ == 'nsubj':
			if 'who' not in result_dict:
				result_dict['who'] = ' '.join(q + [token.text])
		elif token.dep_ == 'punct':
			if token.lemma_ == '?':
				result_dict['question'] = True
			else:
				result_dict['question'] = False
		elif token.dep_ == 'pobj':
			if 'who' not in result_dict:
				result_dict['who'] = ' '.join(q + [token.text])
			else:
				result_dict['who'] += " " + ' '.join(q + [token.text])
		elif token.dep_ == 'xcomp':
			result_dict['action'] = ' '.join(q + [token.text])
		
		if token.dep_ == 'compound' or token.dep_ == 'nummod' or \
			token.dep_ == 'npadvmod' or token.dep_ == 'poss' \
			or token.dep_ == 'attr' or token.dep_ == 'prep':
			compound_flag = True
			q.append(token.text)
		else:
			compound_flag = False
			q = []
			
#         print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#           token.shape_, token.is_alpha, token.is_stop)
		
	
	time_measures = []
	locations = []
	people = []
#     print("\n")
	for ent in doc.ents:
		if ent.label_ == 'DATE' or ent.label_ == 'TIME':
			time_measures.append(ent.text)
		elif ent.label_ == 'GPE':
			locations.append(ent.text)
		elif ent.label_ == 'PERSON':
			people.append(ent.text)
		
#         print(ent.text, ent.label_)
	
	date_parse_res = parse(' '.join(time_measures))
#     print(time_measures)
#     print(date_parse_res)
	result_dict['when'] = 'Anytime'
	if date_parse_res is not None:
		result_dict['when'] = date_parse_res
	result_dict['where'] = locations
	result_dict['people'] = people
	
	return result_dict

def detect_intent(sentence):
	
	concern_verbs = []

	with open('concern_verb_list.txt', 'r') as f:
		concern_verbs = f.read().split()

	res = deduce_action(sentence)

	concern = False

	if res[0]['action'] in concern_verbs:
		concern = True

	return res, concern