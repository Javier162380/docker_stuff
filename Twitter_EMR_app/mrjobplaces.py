import json
from mrjob.job import MRJob
from mrjob.step import MRStep
from diccionaries import word_dict_english
import states


class MRJOB(MRJob):
    """We are going to perform just some Map Reduce methods. MRJOB"""
    MRJob.SORT_VALUES = True

    @staticmethod
    def filter_decode_tweets(line):
        try:
            tweet_object = json.loads(line, encoding='utf-32')
            return tweet_object
        except ValueError:
            return None

    @staticmethod
    def point_in_polygon(x, y, poly):
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def mapper_english(self, _, line):
        tweet_object = MRJOB.filter_decode_tweets(line)
        if tweet_object is not None and 'text' in tweet_object:
            # we are just going to analyze english tweets perform in the USA.
            if 'lang' in tweet_object and tweet_object['lang'] == 'en':
                tweet_value = 0
                for word in tweet_object['text'].split():
                    # we get the value of each word.
                    value = word_dict_english.get(word.upper(), 0)
                    tweet_value += value
                    # we get english hastags.
                    if '#' in word:
                        yield (word, 1)
                    else:
                        pass
                        # we are going to analyze the influence of elclasico in the USA.
                if tweet_value != 0 and tweet_object['place'] is not None:
                    if tweet_object['place']['country_code'] == 'US':
                        try:
                            state = tweet_object['place']['full_name'].split(', ')[1]
                            yield (state, tweet_value)
                        except:
                            pass
                    else:
                        pass
                elif tweet_value != 0 and tweet_object['geo'] is not None:
                    if len(tweet_object['geo']['coordinates']) == 2 and tweet_object['geo']['type'] == 'Point':
                        for state, polygon in states.statePolygons.items():
                            if (MRJOB.point_in_polygon(tweet_object['geo']['coordinates'][0],
                                                       tweet_object['geo']['coordinates'][1], polygon)) == True:
                                yield (state, tweet_value)

                elif tweet_value != 0 and tweet_object['user']['location'] is not None:
                    for full_name in states.stateNames.keys():
                        if tweet_object['user']['location'].upper().find(full_name.upper()) != -1:
                            state = states.stateNames[full_name]
                            yield (state, tweet_value)
                else:
                    pass

    def combiner(self, key, value):
        try:
            yield (key, sum(value))
        except:
            pass
    def reducer_per_type_of_object(self, key, value):
        hastag_sentiment = (sum(value), key)
        if '#' in key:
            yield ('#', hastag_sentiment)
        else:
            yield ('location', hastag_sentiment)

    def reducer_top_state_and_Hastags(self, key, hastag_sentiment):
        final_reducer = list(hastag_sentiment)
        # we retrieve the list of states order by most postitive to negative,
        state_list = []
        if key == 'location':
            for i in final_reducer:
                state_list.append(i)
        state = sorted(state_list, key=lambda tup: tup[0], reverse=True)
        for i in range(len(state)):
            yield (state[i][0], state[i][1])
        # swe retrieve the name of the number one positive state.
        state_top_1 = state[:1]
        if len(state_top_1) == 1:
            yield ("El estado mas positivo ha sido ", state_top_1[0][1])
        else:
            pass
        # we retrieve the top 10 hastags.
        hastag_list = []
        if key == '#':
            for i in final_reducer:
                hastag_list.append(i)
        hastag = sorted(hastag_list, key=lambda tup: tup[0], reverse=True)
        hastag_top_10 = hastag[:10]
        for i in range(len(hastag_top_10)):
            yield ("Hastag numero " + str(i + 1) + " repetido " + str(hastag_top_10[i][0])
                   , hastag_top_10[i][1])

    def steps(self):
        return [
            MRStep(mapper=self.mapper_english,
                   combiner=self.combiner,
                   reducer=self.reducer_per_type_of_object),
            MRStep(reducer=self.reducer_top_state_and_Hastags)
        ]


if __name__ == '__main__':
    MRJOB.run()