from random import randint
import mysql.connector as mariadb
import urllib.request
import collections
import os
import nltk
import time

mariadb_connection = mariadb.connect(user='group2', password='isthebest', database='sts')
cursor = mariadb_connection.cursor()

tTokenizer = nltk.tokenize.TweetTokenizer(preserve_case = False, strip_handles = True)
tTokenizerSoft = nltk.tokenize.TweetTokenizer(preserve_case = False, strip_handles = False)

charBlacklist = [':', ',', '"', '!', '\\']
charBlacklistSoft = ['"', ':', '\\']
currTally = {}
allTweets = {}
sentiments = collections.Counter()
skipIds = []
skipWords = []

def clearTally():
	currTally.clear()

def fetchFromDB(limit = 0):
	if limit == 0:
		query = 'select * from tweetsreal;'
	else:
		query = 'select * from tweetsreal limit {};'.format(limit)
	cursor.execute(query)
	for (tId, tName, tHandle, tTime, tTweet, tURL) in cursor:
		allTweets[tId] = tTweet

def tallyDists():
	for tId in allTweets:
		if tId not in skipIds:
			tTokenized = tTokenizer.tokenize(allTweets[tId])
			for word in [filtered for filtered in sorted(set(tTokenized)) if filtered not in (charBlacklist + skipWords) and len(filtered) > 1]:
				if word not in currTally:
					currTally[word] = []
				currTally[word].append(tId)

def getPriority():
	return sorted(currTally, key = lambda x: len(currTally.get(x)) + (1000 if x.startswith('u') else 0), reverse = True)

def grabTweets(word):
	if len(currTally[word]) >= 5:
		startPoint = randint(0, len(currTally[word]) - 5)
		sampleRange = currTally[word][startPoint:startPoint + 5]
	else:
		sampleRange = currTally[word]
	for x in sampleRange:
		print('{:>5}:   {}\n'.format(x, allTweets[x]))

def interpretation(word):
	os.system('cls')
	print('='*20)
	print('{:5} ({} left, {} instances)'.format(word, len(getPriority()), len(currTally.get(word))))
	print('='*20)
	print('Sample Tweets')
	grabTweets(word)
	print('[h]appy, [s]ad, an[g]ry, [d]ontcare, [i]nspired, a[f]raid, a[m]used, a[n]noyed, discard[x]')
	if word.startswith('u000'):
		urllib.request.urlretrieve('http://apps.timwhitlock.info/static/images/emoji/emoji-apple/{}.png'.format(word[4:]), 'emojis\{}.png'.format(word[4:]))
		os.startfile('emojis\{}.png'.format(word[4:]))

def prettySentiments():
	os.system('cls')
	print('='*20)
	print('Analysis complete.')
	print('='*20)
	print('{:>15}: {}'.format('N', len(allTweets)))
	print('{:>15}: {}'.format('Happy', sentiments['h']))
	print('{:>15}: {}'.format('Sad', sentiments['s']))
	print('{:>15}: {}'.format('Angry', sentiments['g']))
	print('{:>15}: {}'.format('Don\'t Care', sentiments['d']))
	print('{:>15}: {}'.format('Inspired', sentiments['i']))
	print('{:>15}: {}'.format('Afraid', sentiments['f']))
	print('{:>15}: {}'.format('Amused', sentiments['m']))
	print('{:>15}: {}'.format('Annoyed', sentiments['n']))

fetchFromDB()
tallyDists()

while getPriority():
	for word in getPriority():
		interpretation(word)
		choice = input('Verdict? ')
		if choice == 'x':
			skipWords.append(word)
			clearTally()
			tallyDists()
		elif choice in 'hsgdifmn':
			skipIds += currTally[word]
			sentiments[choice] += len(currTally[word])
			clearTally()
			tallyDists()
			break

prettySentiments()