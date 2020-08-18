import re
import fasttext
import tweepy 
from tweepy import OAuthHandler

class TwitterClient(object):
    model = fasttext.load_model("modelo-entrenado2-900.bin")
    def __init__(self): 
        ''' 
        Constructor. 
        '''
        # keys and tokens from the Twitter Dev Console 
        consumer_key = 'b60mPKOrMiZW4g8JlEYdU5Cjf'
        consumer_secret = 'z9mWYkobkvnaNFyOo5dIe44bF2gxR4lbixk8Sg6thpR6Ltv6wG'
        access_token = '1272307791127085063-OEABNF318S6rK6VxaqoF5QekWrELhs'
        access_token_secret = 'Txmk1ggTnmlb1FqRHkqvgGYhB78pXRF1qEoB3pqPPDPNd'
        
        #  Authenticacion

        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 

        except: 
            print("Error: Falla en la autenticacion")

    def clean_tweet(self, tweet): 
        ''' 
        Remueve enlaces, caracteres especiales con regex
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 
        #modificar aqui para sentimiento depresivo y no depresivo
    def get_tweet_sentiment(self, tweet):
        ''' 
        Asigna el valor del sentimiento usando un metodo fasttext 
        '''
        #prediccion del texto depresivo o no depresivo
        analysis = self.model.predict(self.clean_tweet(tweet))
        if(analysis[0][0].find("__label__depresivo") == 0):
            return 'depresivo'
        else:
            return 'nodepresivo'


    def get_tweets(self, query, count = 3000): 
        ''' 
        Main function, get twittes y parsea 
        '''
        # lista vacia con tweets
        tweets = [] 
        limit_number = 3200

        try: 

            #inicializar una list to para almacenar los Tweets descargados por tweepy
            alltweets = []
            # call twitter api to fetch tweets 
            #fetched_tweets = self.api.search(q = query)#, count = count)
            fetched_tweets = self.api.user_timeline(id = query, count = 200)

            #guardar los tweets más recientes
            alltweets.extend(fetched_tweets)

            #guardar el ID del tweet más antiguo menos 1
            oldest = alltweets[-1].id - 1

            #recorrer todos los tweets en la cola hasta que no queden más
            while len(fetched_tweets) > 0 and len(alltweets) <= limit_number and len(fetched_tweets) > 0:
                print ("getting tweets before" + str(oldest))
        
                #en todas las peticiones siguientes usar el parámetro max_id para evitar duplicados
                fetched_tweets = self.api.user_timeline(screen_name = query,count=200,max_id=oldest)
        
                #guardar los tweets descargados
                alltweets.extend(fetched_tweets)
        
                #actualizar el ID del tweet más antiguo menos 1
                oldest = alltweets[-1].id - 1
        
                #informar en la consola como vamos
                print (str(len(alltweets)) + " tweets descargados hasta el momento")

            # parsea tweets uno por uno
            for tweet in alltweets: 
                # diccionario con parametros tweet
                parsed_tweet = {} 

                # guardamos el text
                parsed_tweet['text'] = tweet.text 

                # guardamos el sentimiento
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 

                # Agregamos a los tweets
                if tweet.retweet_count > 0: 
                    # si tiene retweets se agrega solo uno
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 

            # devuelve los parseados
            return tweets 

        except tweepy.TweepError as e: 
            # print error (si hay) 
            print("Error : " + str(e)) 