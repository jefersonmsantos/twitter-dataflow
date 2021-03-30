import pytest
from dags.tweet_app_dag import consult_tweet_api, read_txt_save_json, process_json_to_df_to_sql, remove_files
import unittest.mock as mock
import pytest-mock
import pickle



#test for consult_tweet_api
class test_consult_tweet_api(object):
    
    def cursor_bug_free():
        with open('cursor.pickle', 'rb') as handle:
            cursor = pickle.load(handle)

        cursor=iter([cursor])
        return cursor

    def test_saved_file(self, mocker):
        cursor_mock = mocker.patch("data.consult_tweet_api.cursor", side_effect = cursor_bug_free)
        
        tweet_api_connection()




#test for read_txt_save_json





#test for process_json_to_df_to_sql





#test for remove_files