import pickle

consumer_key = input('Consumer Key: ')
consumer_secret = input('Consumer Secret: ')
access_token_key = input('Access Token Key: ')
access_token_secret = input('Access Token Secret: ')
with open('credential_twitter.pkl', mode='wb') as output:
    pickle.dump((consumer_key, consumer_secret,
                 access_token_key, access_token_secret), output)
    output.close()
