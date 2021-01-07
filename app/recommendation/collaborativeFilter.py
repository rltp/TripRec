import pandas as pd
import numpy as np
from surprise import accuracy, Dataset, Reader
from surprise.model_selection import train_test_split, GridSearchCV
from surprise import SVD
from collections import defaultdict

class CollaborativeRecommender():

    def __init__(self, data, score_index, user_index, items_index):

        self.items_index = items_index
        self.user_index = user_index
        self.data = data

        scale = (data[score_index].min(), data[score_index].max())
        reader = Reader(rating_scale=scale)
        dataset = Dataset.load_from_df(data[[user_index, items_index, score_index]], reader)

        param_grid = {'n_factors': [50, 100, 150], 'n_epochs': [25, 50, 75], 'lr_all': [0.005, 0.01], 'reg_all': [0.02, 0.1, 0.5]}
        
        gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3)
        gs.fit(dataset)

        params = gs.best_params['rmse']
        
        self.model = SVD(reg_all=params['reg_all'], n_factors=params['n_factors'],
                         n_epochs=params['n_epochs'], lr_all=params['lr_all'])
        self.model.fit(dataset.build_full_trainset())

    def predict(self, user, max=5):
        best = []
        for item in self.data[self.data[self.user_index] != user][self.items_index].unique():
            uid, iid, r_ui, est, _ = self.model.predict(uid=user, iid=item)
            best += [(iid, est)]
        best.sort(key=lambda x : x[1] , reverse=True)
        return best[:max]