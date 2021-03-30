from airflow import DAG
from airflow.operators.python_operator import PythonOperator 
from datetime import datetime, timedelta
import pandas as pd 
import json
import tweepy
import pymysql
from sqlalchemy import create_engine
import os


#Argumentos default
default_args={
    "owner":"Jeferson Machado Santos",
    "depends_on_past":False,
    "start_date": datetime(2021, 3, 13, 18, 40),
    "retries":2,
    "retry_delay": timedelta(minutes=1)
}



engine = create_engine('mysql+pymysql://{user}:{pw}@statfoot.chvygiyeqqoe.us-east-2.rds.amazonaws.com:3306/{db}'
                      .format(user=os.environ["sql_user"],
                             pw=os.environ["sql_pw"],
                             db='twitter_app'))

connection = engine.connect()



#Definição DAG
dag = DAG(
    "tweet-flow",
    description = "Coleta dados do twitter, processa e armazena em base SQL",
    default_args = default_args,
    schedule_interval = timedelta(minutes = 5)
)

def tweet_api_connection():
    API_Key = os.environ['API_Key']
    API_Secret_key = os.environ['API_Secret_key']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']

    #Realizar autenticação no twitter
    auth = tweepy.OAuthHandler(API_Key, API_Secret_key)
    auth.set_access_token(access_token, access_token_secret)

    #construir instância api
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    return api

#Consultar Twitter API e salvar arquivo txt. Passar nome do arquivo adiante
def consult_tweet_api():
    
    api = tweet_api_connection()

    keyword = "'NETFLIX' OR 'HBOGO' OR 'DISNEYPLUS' OR 'DISNEY+' OR 'GLOBOPLAY' OR 'AMAZON PRIME' OR 'PRIME VIDEO'"
    brasil_geo_code = api.geo_search(query="Brazil", granularity="country")[0].id

    data_agora = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out = open(f"/usr/local/airflow/data/collected_tweets_{data_agora}.txt","w")

    cursor = tweepy.Cursor(api.search,
                            q='{} place:{}'.format(keyword, brasil_geo_code), 
                            #q=keyword,  
                            tweet_mode='extended',
                            rpp=2000,
                            result_type="recent",
                            lang='pt',
                            include_entities=True,
                            include_rts=False).items(2000)

    for tweet in cursor:
        
        itemstring=json.dumps(tweet._json)
        out.write(itemstring + '\n')

    return f"/usr/local/airflow/data/collected_tweets_{data_agora}.txt"


task_tweet_api = PythonOperator(
    task_id='tweet-api',
    python_callable = consult_tweet_api,
    dag=dag
)

#Abrir txt e salvar json
def read_txt_save_json(**context):
    file = context['task_instance'].xcom_pull(task_ids='tweet-api')
    with open(file, 'r') as f:
        tweets = f.readlines()

    parsed_tweets = [json.loads(i) for i in tweets]

    data_agora = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    with open(f"/usr/local/airflow/data/tweets_json_{data_agora}.json","w") as j:
        json.dump(parsed_tweets,j)

    return f"/usr/local/airflow/data/tweets_json_{data_agora}.json"

task_read_txt_save_json = PythonOperator(
    task_id = 'read-txt-save-json',
    python_callable = read_txt_save_json,
    provide_context = True,
    dag=dag
)



#Abrir json e processar e salvar

def process_json_to_df_to_sql(**context):
    file = context['task_instance'].xcom_pull(task_ids='read-txt-save-json')

    with open(file,'r') as f:
        parsed_tweets=json.load(f)

    df = pd.json_normalize(parsed_tweets)

    db_columns = connection.execute("SELECT * FROM tweets LIMIT 1")._metadata.keys

    for c in list(df.columns):
        if c in db_columns:
            df[c]=df[c].astype(str)
        else:
            df =df.drop([c],axis=1)

    #df=df.drop(['quoted_status_id','quoted_status_id_str'],axis=1)

    


    df.to_sql('tweets',con=connection,if_exists='append',index=False)


task_json_df_sql= PythonOperator(
    task_id = 'process-json-to-df-to-sql',
    python_callable = process_json_to_df_to_sql,
    provide_context = True,
    dag=dag
)


#Apagar arquivos
def remove_files(**context):
    txt_file = context['task_instance'].xcom_pull(task_ids='tweet-api')
    json_file = context['task_instance'].xcom_pull(task_ids='read-txt-save-json')

    os.remove(txt_file)
    os.remove(json_file)


task_remove_files= PythonOperator(
    task_id = 'remove-files',
    python_callable = remove_files,
    provide_context = True,
    dag=dag
)


task_tweet_api >> task_read_txt_save_json >> task_json_df_sql >> task_remove_files