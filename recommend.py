#!/usr/bin/env python
import os
import math
import urllib
import random
import datetime
from lxml import etree
from collections import defaultdict

def euclidean_distance(prefs, user1, user2):
    shared = {}
    for item in prefs[user1]:
        if item in prefs[user2]:
            shared[item] = 1
    if len(shared) == 0: return 0
    sum_of_squares = sum((prefs[user1][item]-prefs[user2][item])**2 for item in shared.keys())
    return 1/(1+sum_of_squares)

def pearson_correlation(prefs, user1, user2):
    shared = {}
    for item in prefs[user1]:
        if item in prefs[user2]:
            shared[item] = 1
    n = len(shared)
    if n == 0: return 0
    # add all the preferences
    prefs1 = [prefs[user1][item] for item in shared]
    prefs2 = [prefs[user2][item] for item in shared]
    sum1 = sum(prefs1)
    sum2 = sum(prefs2)
    sum1_squared = sum(p**2 for p in prefs1)
    sum2_squared = sum(p**2 for p in prefs2)
    p_sum = sum(a*b for a,b in zip(prefs1, prefs2))
    num = p_sum - (sum1*sum2/n)
    den = math.sqrt((sum1_squared-(sum1**2/n))*(sum2_squared-(sum2**2/n)))
    if den == 0: return 0
    r = num/den
    return r

class Item(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Movie(Item):
    def __init__(self, name, date=None, url=None):
        self.name = name
        self.url = url
        self.date = date


class Recommender(object):
    def __init__(self):
        self.recommendations = []

    def recommend(self):
        raise NotImplementedError('Override this method in a subclass')

    def num_recommendations(self):
        return len(self.recommendations)

class TasteKidRecommender(Recommender):
    def recommend(self, movie_title, limit=False, shuffle=False):
        '''Given a movie title, query TasteKid for similar movies'''
        recommendations = []
        url = "http://www.tastekid.com/ask/ws?" + urllib.urlencode({'q' : movie_title})
        doc = etree.parse(url)
        for rec in doc.xpath('/similar/results/resource'):
            recommendations.append(Item(rec.xpath('name')[0].text))
        self.recommendations = recommendations

        if shuffle:
            random.shuffle(recommendations)
        if limit:
            recommendations = recommendations[:limit]

        return recommendations

class MovieLensRecommender(Recommender):
    def __init__(self):
        '''load the movielens dataset located in directory'''
        self.data_path = os.path.join(os.path.dirname(__file__), 'data', 'ml-100k')
        self.movies = {}
        for line in open(os.path.join(self.data_path, 'u.item')):
            info = line.split('|')
            id = int(info[0])
            title = info[1]
            try:
                date = datetime.datetime.strptime(info[2], '%d-%b-%Y')
            except:
                date = None
            url = info[4]
            self.movies[id] = Movie(title, date, url)
        self.prefs = defaultdict(dict)
        for line in open(os.path.join(self.data_path, 'u.data')):
            user_id, movie_id, rating, timestamp = line.split('\t')
            user_id = int(user_id)
            movie_id = int(movie_id)
            rating = float(rating)
            time = datetime.datetime.fromtimestamp(float(timestamp))
            self.prefs[user_id][self.movies[movie_id]] = rating

    def recommendations_for_user(self, user_id, similarity=euclidean_distance):
        '''given a user id, find recommendations for that user'''
        totals = defaultdict(float)
        sim_sums = defaultdict(float)
        for other_id in self.prefs:
            if other_id == user_id: continue
            sim = similarity(self.prefs, user_id, other_id)
            if sim <= 0: continue
            for item in self.prefs[other_id]:
                if item not in self.prefs[user_id] or self.prefs[user_id][item] == 0:
                    totals[item] += self.prefs[other_id][item] * sim
                    sim_sums[item] += sim
        rankings = [(total/sim_sums[item], item) for item, total in totals.items()]
        rankings.sort()
        rankings.reverse()
        return rankings

    def similar_users(self, user_id, limit=5, similarity=pearson_correlation):
        '''given a user id, find similar users'''
        scores = [(similarity(self.prefs, user_id, other_id), other_id)
                  for other_id in self.prefs.keys() if other_id != user_id]
        scores.sort()
        scores.reverse()
        return scores[:limit]

