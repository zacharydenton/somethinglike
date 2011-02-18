#!/usr/bin/env python
import urllib
import random
from lxml import etree

class Item(object):
    def __init__(self, name):
        self.name = name

class Recommender(object):
    def __init__(self):
        self.recommendations = []

    def recommend(self):
        raise NotImplementedError('Override this method in a subclass')

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



