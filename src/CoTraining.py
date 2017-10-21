import warnings
import time
import numpy as np
from sklearn import preprocessing as pr , svm
from Wrapper import Wrapper
warnings.filterwarnings('ignore')


class CoTraining(Wrapper):
    def __init__(self, label, un_label, test):
        Wrapper.__init__(self, label, un_label,test)
        self.NO_OF_MODELS = 2
        self.final_file = '../dataset/analysed/co_training_' + self.get_file_prefix() + str(time.time())

    def map_tweet(self , tweet , mode ):
        """
        :param tweet: 
        :param mode: 
        :return: 
        """
        if mode:
            return self.map_tweet_feature_values(tweet)
        if not mode:
            return self.map_tweet_n_gram_values(tweet)

    def predict(self , tweet):
        z = self.transform_tweet(tweet , 1,self.config.NO_TOPIC)
        z_0 = self.transform_tweet(tweet , 0,self.config.NO_TOPIC)
        predict_proba = self.ds._get_model_(1, self.config.NO_TOPIC).predict_proba([ z ]).tolist()[ 0 ]
        predict_proba_0 = self.ds._get_model_(0, self.config.NO_TOPIC).predict_proba([ z_0 ]).tolist()[ 0 ]
        sum_predict_proba = self.commons.get_sum_proba(predict_proba , predict_proba_0)
        f_p , s_p = self.commons.first_next_max(sum_predict_proba)
        f_p_l = self.commons.get_labels(f_p , sum_predict_proba)
        predict = self.ds._get_model_(1,self.config.NO_TOPIC).predict([ z ]).tolist()[ 0 ]
        predict_0 = self.ds._get_model_(0,self.config.NO_TOPIC).predict([ z_0 ]).tolist()[ 0 ]
        if predict == predict_0:
            return predict
        else:
            if f_p - s_p < self.config.PERCENTAGE_MINIMUM_DIFF\
                    or f_p < self.config.PERCENTAGE_MINIMUM_CONF_CO:
                maxi = max(predict , predict_0)
                mini = min(predict , predict_0)

                if maxi > 0 and mini < 0:
                    return self.config.LABEL_NEUTRAL

                if maxi > 0 and mini == 0:
                    return self.config.LABEL_POSITIVE

                if maxi == 0 and mini < 0:
                    return self.config.LABEL_NEGATIVE
            else:
                return f_p_l

    def predict_for_iteration(self, tweet , last_label):
        z = self.transform_tweet(tweet , 1,self.config.NO_TOPIC)
        z_0 = self.transform_tweet(tweet , 0,self.config.NO_TOPIC)
        predict_proba = self.ds._get_model_(1,self.config.NO_TOPIC).predict_proba([z]).tolist()[ 0 ]
        predict_proba_0 = self.ds._get_model_(0,self.config.NO_TOPIC).predict_proba([z_0]).tolist()[ 0 ]
        sum_predict_proba = self.commons.get_sum_proba(predict_proba , predict_proba_0)
        f_p , s_p = self.commons.first_next_max(sum_predict_proba)
        f_p_l = self.commons.get_labels(f_p , sum_predict_proba)
        predict = self.ds._get_model_(1).predict([z]).tolist()[0]
        predict_0 = self.ds._get_model_(0).predict([z_0]).tolist()[0]

        if predict == predict_0:
            return predict, 0.9
        else:
            if f_p - s_p < self.config.PERCENTAGE_MINIMUM_DIFF \
                    or f_p < self.config.PERCENTAGE_MINIMUM_CONF_CO:
                return self.config.UNLABELED,0
            else:
                return f_p_l,f_p

