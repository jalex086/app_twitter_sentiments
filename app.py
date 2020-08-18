from flask import Flask, request, render_template, url_for
from .twitter_client import TwitterClient
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('template.html')

@app.after_request
def add_header(r):
	"""
	Add headers to both force latest IE rendering engine or Chrome Frame,
	and also to cache the rendered page for 10 minutes.
	"""
	print('entro.............')
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	r.headers['Cache-Control'] = 'public, max-age=0'
	return r

def graficar(nombres, datos, tweeter_user):
	fig = plt.figure(u'Gráfica de tweets') # Figure
	
	#ax = fig.add_subplot(111) # Axes
	ax = fig.subplots() # Axes

	xx = range(len(datos))

	ax.bar(xx, datos, width=0.8, align='center')
	ax.set_xticks(xx)
	ax.set_xticklabels(nombres)
	plt.savefig('static/images/{}.png'.format(tweeter_user))
	plt.close()
	plt.clf()
	plt.cla()
	return url_for('static', filename ='images/{}.png'.format(tweeter_user))


@app.route('/check_tweets', methods=['POST'])
def check_teets():

	tweeter_user = request.form['tweeter_user']
	# crea objeto TwitterClient  
	api = TwitterClient() 

	# Llama funcion para obtener tweets 
	tweets = api.get_tweets(query = tweeter_user, count = 3600)

	if (tweets is None):
		resultado = {
			'usuario': 'NO existe el usuario',
			'total': 0,
			'ptweets': 0,
			'ntweets': 0,
			'url': False
		}
	else:
		total = ("total de tweets analizados: {} ".format(len(tweets)))

		# Sacamos los positivos
		ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'depresivo'] 
		texto1 = ("Porcentaje tweets depresivos: {} %".format(100*len(ntweets)/len(tweets))) 

		# Negativos
		ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'nodepresivo'] 
		texto2 = ("Porcentaje tweets No depresivos: {} %".format(100*len(ptweets)/len(tweets))) 

		nombre_imagen = tweeter_user

		# printing first 5 depresivos tweets 
		'''print('\n\nDepresivos tweets:') 
		for tweet in ntweets[:10]: 
			print(tweet['text']) 

		# printing first 5 negative tweets 
		print('\n\nNo depresivos tweets:') 
		for tweet in ptweets[:10]: 
			print(tweet['text'])
		'''

		'''
		label = ("depresivos", "otros")
		posicion_y = np.arange(len(label))
		numTweets = (len(ntweets), len(ptweets))
		plt.barh(posicion_y, numTweets, align = "center")
		plt.yticks(posicion_y, label)
		plt.xlabel("cantidad de tweets")
		plt.title("Grafica de tweets")
		plt.savefig('static/images/{}.png'.format(tweeter_user))
		'''
		print(len(ntweets))
		print(len(ptweets))
		nombres = ['depresivos','otros']
		datos = [len(ntweets), len(ptweets)]
		url = graficar(nombres, datos, tweeter_user)
		resultado = {
			'usuario': nombre_imagen,
			'total': total,
			'ptweets': texto1,
			'ntweets': texto2,
			'url': url
		}
	return render_template('template.html', resultado = resultado)
