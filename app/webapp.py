# pylint: disable=invalid-name
import pandas as pd
import os
from flask import Flask
from flask import render_template, redirect, url_for
from app.cleanup import Hotels
from app.recommendation.contentBased import ContentRecommander as CB
from app.recommendation.collaborativeFilter import CollaborativeRecommender as CF
from flask_cors import CORS

app = Flask(__name__, static_folder="./templates/build/static",
            template_folder="./templates/build")
CORS(app)

DATASETS_DIR = os.path.realpath(os.path.join(__file__, '..', 'datasets'))

@app.route("/scrap")
def scrap():
    app.logger.infos('Scrapping started...')

    data = Scrapper('https://www.tripadvisor.fr/Hotels-g187070-France-Hotels.html', 30)

    ratings = pd.DataFrame(data.get_reviews())
    hotels = pd.DataFrame(data.get_hotel())

    hotels.to_csv(DATASETS_DIR+'/hotels.csv', index=False)
    ratings.to_csv(DATASETS_DIR+'/ratings.csv', index=False)

    return "<h1>Scrapped</h1>"

@app.route("/contentBased/<user>/<int:max>")
def contentBased(user=None, max=None):
    if(user == None or max == None):
        return redirect(url_for('/'))

    predicted = cb.predict(user, max=max)
    rec = pd.merge(left=hotels, right=predicted, left_on="adress", right_on='adress')
    return rec.to_json()


@app.route("/collaborativeFilter/<user>/<int:max>")
def collaborativeFilter(user=None, max=None):
    if(user == None or max == None):
        return redirect(url_for('/'))
    predicted = cf.predict(user, max=max)
    matches = pd.DataFrame(predicted, columns=['hotelAdress', 'prediction'])
    rec = pd.merge(left=hotels, right=matches, left_on="adress", right_on='hotelAdress')
    return rec.to_json()


@app.route("/users")
def users():
    data = ratings['username'].unique().tolist()
    return pd.DataFrame(data).to_json()


@app.route("/")
def render():
    return render_template('index.html')


if __name__ == "__main__":

    print('Initialization ...')

    ratings = pd.read_csv(DATASETS_DIR+'/ratings.csv')
    hotels = pd.read_csv(DATASETS_DIR+'/hotels.csv')

    print('> Datasets loaded')

    cf = CF(data=ratings, score_index='rating', user_index='username', items_index='hotelAdress')

    print('> Collaborative filtering models loaded')

    CB = type('CB', (Hotels,), dict(CB.__dict__))
    cb = CB(items=hotels, users=ratings)

    print('> Content based matrix loaded')
    print('> Web deamon is loaded')
    app.run(host='0.0.0.0')
