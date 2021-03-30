## Twitter API pipeline using Airflow and SQL
This application is a simplified model of a Airflow data pipeline, which extracts data from Twitter Api, adjust the data, and save to a SQL database.

The application uses Airflow to orchestrate the stages of data pipeline. First, every 5 minutes tweets with selected keywords are collected and its content saved to a .txt file. Then, those .txt files are manipulated and saved to .json format. Later, .json files are transformed to a pandas dataframe and then saved to a SQL database.

To access the Twitter API it is necessary to create a Twitter developer account and obtain the access keys.

## Como realizar o deploy da aplicação
1. Copy the fyles from this repo to a place where you want to run the application;
2. Create a .env file and define the following environment variables to acesse Twitter API and Mongo DB Database:
    * API_Key
    * API_Secret_key
    * access_token 
    * access_token_secret

    * sql_user 
    * LOAD_EX=n
    * FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
    * EXECUTOR=Celery


3. Open a terminal and run command "docker build --rm --build-arg AIRFLOW_DEPS="datadog,dask" --build-arg PYTHON_DEPS="flask_oauthlib>=0.9" -t puckel/docker-airflow" to build airflow image
4. Open a new terminal and start airflow, with command "docker-compose up -d"
5. In your browser, access localhost:8080 to open airflow user interface
6. Start scheduler, and the process will start
7. Tweets data must now be saved on your SQL Database every five minutes.

## License and Author info
MIT License

Copyright (c) 2021 Jeferson Machado Santos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.