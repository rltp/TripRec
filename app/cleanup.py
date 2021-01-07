import pandas as pd


class Hotels():

    ratings_index = 'rating'

    def hotels_dummies(self):
        self.hotels['description'] = self.hotels['equipments'] + "|" + \
            self.hotels['roomFeats'] + "|" + self.hotels['roomTypes']

        hotel_dummies = self.hotels.copy()
        return hotel_dummies \
            .join(hotel_dummies.description.str.get_dummies("|")) \
            .drop(columns=['totalReviews', 'img', 'equipments', 'roomFeats', 'roomTypes', 'description', 'score', 'categories', 'url'])

    def user_profiles(self, username):

        self.user_ratings = self.users.loc[self.users['username'] == username]

        return pd \
            .merge(left=self.user_ratings, right=self.hotels_dummies(), left_on='hotelAdress', right_on='adress') \
            .drop(columns=['title', 'profile', 'comment', 'adress', 'hotelAdress', 'hotelName', 'name', 'username']) \
            .reset_index(drop=True)

    def clear_user_hotels(self):
        hotels_name = self.hotels_dummies()['adress']
        hotels_clear = self.hotels_dummies()[~hotels_name.isin(
            self.user_ratings['hotelAdress'].tolist())].drop(['adress', 'name'], 1)
        return hotels_clear

    def setUsers(self, users):
        self.users = users

    def setItems(self, hotels):
        self.hotels = hotels

    def get_dummies(self):
        return self.hotels_dummies()
