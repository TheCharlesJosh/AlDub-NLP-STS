import mysql.connector as mariadb
import time
import tweepy

auth = tweepy.OAuthHandler('access key', 'access code')
auth.set_access_token('private key', 'public key')


api = tweepy.API(auth_handler = auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

sampleSize = 100000
forLoopCounter = 0
numberOrganic = 0
targetOrganic = 5000
initialSeconds = time.time()
finalSeconds = 0

mariadb_connection = mariadb.connect(user='root', password='root', database='sts')
cursor = mariadb_connection.cursor()

for tweet in tweepy.Cursor(api.search, q='ALDubEBTamangPanahon', until='2015-10-25').items(sampleSize):
	forLoopCounter += 1
	try:
		if numberOrganic >= targetOrganic:
			break
		else:
			cursor.execute("INSERT INTO tweets2 (twitterName,twitterHandle,tweetTime,tweet,tweetURL) VALUES (%s,%s,%s,%s,%s)", (tweet.user.name.encode('unicode-escape'), tweet.user.screen_name.encode('unicode-escape'), tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'), tweet.text.encode('unicode-escape'), 'https://twitter.com/{}/status/{}'.format(tweet.user.screen_name, tweet.id)))
			mariadb_connection.commit()
			numberOrganic += 1
			print('Total number of tweets: {}/{}'.format(numberOrganic, forLoopCounter))
	except tweepy.TweepError:
		print('Error: {}').format(error)
	except mariadb.Error as error:
		print('Error: {}').format(error)

finalSeconds = time.time()

print('\n')
print('Total number of tweets:     {}'.format(numberOrganic))
print('Total running time:                 {}'.format(finalSeconds - initialSeconds))
print('Average operation time per tweet:   {}'.format((finalSeconds - initialSeconds)/sampleSize))

mariadb_connection.close()