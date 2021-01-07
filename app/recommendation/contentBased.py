import pandas as pd

class ContentRecommander(object):

    def __init__(self, items, users):
        self.setItems(items)
        self.setUsers(users)

    def predict(self, user, max = 5):
        features = self.user_profiles(user)
        transpose = features.transpose()
        profile = (transpose.dot(features[self.ratings_index]) / transpose.dot(
            features[self.ratings_index]).sum()).drop(self.ratings_index, 0)
        matrix = self.clear_user_hotels().dot(profile)
        return pd \
            .concat([self.get_dummies()['adress'], matrix], axis=1) \
            .rename(columns={0: 'prediction'}) \
            .sort_values(by='prediction', ascending=False)\
            .head(max)