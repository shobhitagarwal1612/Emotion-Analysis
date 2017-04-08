from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
from __future__ import unicode_literals

import collections
import json
import os
import os.path
import pickle

from django.db import models
from nltk.corpus import movie_reviews as reviews

from emotionanalysis.build import build_and_evaluate


class Amazon_Scrape(models.Model):
    amazon_url = models.URLField(max_length=100)

    def fun(self, url):
        # Define command and arguments
        command = 'python'

        path = os.getcwd()

        path2script = path + '/parsers/' + 'parse_amazon.py'

        # Variable number of args in a list
        args = [url]

        # Build subprocess command
        cmd = [command, path2script] + args
        # check_output will run the command and store to result
        x = subprocess.call(cmd, universal_newlines=True)

        command = 'Rscript'
        path2script = path + '/Rscripts/' + 'scrape-data.R'

        cmd = [command, path2script] + args
        open('userReviews.txt', 'w').close()
        # check_output will run the command and store to result
        # x = subprocess.call(cmd, universal_newlines=True)


class Amazon_Analyse(models.Model):
    def analyse_class(self):

        model = self.get_model()
        # print(show_most_informative_features(model,'this is a nice day',n=50))
        # print(show_most_informative_features(model,'this is a worst day',n=50))
        comments, ratings = self.parse_data()
        comments_sentiment = model.predict(comments)
        # print(comments_sentiment)

        specs = ['camera', 'performance', 'battery', 'look', 'feel', 'money', 'sound', 'network', 'storage', 'software']
        # specs = []
        total_score = []
        data = []
        comments_list = collections.defaultdict(lambda: [])
        self.generate_specification_sentiment(comments, comments_list, comments_sentiment, data, ratings,
                                              specs, total_score)

        net_score = round(sum(total_score) / len(total_score), 2)
        # net_score = 0
        print("total score", net_score)

        return net_score, data, comments_list, comments_sentiment

    def get_model(self):
        filename = 'dump.pkl'
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                model = pickle.load(f)
        else:
            X = [reviews.raw(fileid) for fileid in reviews.fileids()]
            y = [reviews.categories(fileid)[0] for fileid in reviews.fileids()]
            model = build_and_evaluate(X, y, outpath=filename)

        return model

    def generate_specification_sentiment(self, comments, comments_list, comments_sentiment, data, ratings,
                                         specs, total_score):

        save_path = os.getcwd() + '/analyse/data/'
        global emotion
        for spec in specs:
            spec_comments = []

            for i, comment in enumerate(comments):
                if spec in comment.split():
                    emotion = comments_sentiment[i]

                    spec_comments.append([comment, ratings[i], emotion])
                    comments_list[spec].append((emotion, comment))

            comments_list[spec].sort()

            if len(spec_comments) > 0:
                sentiment_value = self.calculate_sentiment(spec, spec_comments, total_score)
                data.append((spec, sentiment_value))

            completeFileName = os.path.join(save_path, spec + ".txt")

            with open(completeFileName, 'wb') as fp:
                pickle.dump(spec_comments, fp)

    def calculate_sentiment(self, spec, spec_comments, total_score):
        sentiment_value = sum(i[2] for i in spec_comments) * 1.0 / len(spec_comments)
        sentiment_value = round(sentiment_value, 3) * 10
        total_score.append(sentiment_value)
        sentiment_value = round(sentiment_value, 3)
        print(spec, sentiment_value)
        return sentiment_value

    def Amazon_spec(self, tokenn):

        comments, ratings = self.parse_data()

        model = self.get_model()

        comments_sentiment = model.predict(comments)

        print(comments_sentiment)
        specs = [tokenn]

        total_score = []
        data = []
        comments_list = collections.defaultdict(lambda: [])
        self.generate_specification_sentiment(comments, comments_list, comments_sentiment, data, ratings,
                                              specs, total_score)
        if len(data) == 0:
            return [], comments_list
        else:
            return data[0][1], comments_list

    def parse_data(self):
        with open('amazon_data.json') as data_file:
            data = json.load(data_file)
        comments = [data["reviews"][i]["review_text"] for i in range(len(data["reviews"]))]
        ratings = [data["reviews"][i]["review_rating"] for i in range(len(data["reviews"]))]
        return comments, ratings
