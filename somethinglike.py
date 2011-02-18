#!/usr/bin/env python
# movie recommendations
import argparse
import recommend

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, help='number of recommendations to display (default: 3)', default=3)
    parser.add_argument('-r', '--random', action='store_true', help='randomize the results')
    parser.add_argument('movie_title', help='the title of a movie you like', nargs='+')
    args = parser.parse_args()

    recommender = recommend.TasteKidRecommender()
    recommendations = recommender.recommend(' '.join(args.movie_title), args.random, args.number) 
    for movie in recommendations:
        print movie.name

if __name__ == "__main__": 
    main()
