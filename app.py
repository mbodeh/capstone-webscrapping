from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-item mode-advanced'})
print(table.prettify()[1:1000])
movie_containers = soup.find_all('div', class_ = 'lister-item mode-advanced')
print(type(movie_containers))
print(len(movie_containers))

names = []
years = []
imdb_ratings = []
metascores = []
votes = [] #initiating a list 

for container in movie_containers:
    
    # If the movie has Metascore, then extract:
    if container.find('div', class_ = 'ratings-metascore') is not None:
        
        # The name
        name = container.h3.a.text
        names.append(name)
        
        # The year
        year = container.h3.find('span', class_ = 'lister-item-year').text
        years.append(year)
        
        # The IMDB rating
        imdb = float(container.strong.text)
        imdb_ratings.append(imdb)
        
        # The Metascore
        m_score = container.find('span', class_ = 'metascore').text
        metascores.append(int(m_score))
        
        # The number of votes
        vote = container.find('span', attrs = {'name':'nv'})['data-value']
        votes.append(int(vote))

#change into dataframe
film_imdb = pd.DataFrame({'movie': names,
'year': years,
'imdb': imdb_ratings,
'metascore': metascores,
'votes': votes
})
film_imdb  = film_imdb [['movie', 'year', 'imdb', 'metascore', 'votes']]
film_imdb['year'].unique()
film_imdb.loc[:, 'year'] = film_imdb['year'].str[-5:-1].astype(int)
film_imdb = film_imdb.set_index('movie')
film_imdb1  = film_imdb.copy()
film_imdb1  = film_imdb1.drop('imdb', axis=1,)
film_imdb1  = film_imdb1.drop('votes', axis=1,)
film_imdb1  = film_imdb1.drop('year', axis=1,)
film_imdb1.reindex(['movie'], axis="columns")

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{film_imdb1["metascore"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = film_imdb1.plot.bar(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)