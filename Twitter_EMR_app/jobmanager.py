from mrjobplaces import MRJOB
import os
from pymongo import MongoClient

def main():
    from twitter import twitter
    #twittersetup.
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    api_token = os.getenv('API_TOKEN')
    api_token_secret = os.getenv('API_TOKEN_SECRET')
    twitter = twitter(api_key, api_secret, api_token, api_token_secret)
    #twittersearch.
    query = os.environ['TWEETER_ACCOUNT']
    number_of_days = float(os.getenv('DOWNLOAD_TIME'))
    twitter.streamingapi(query, 'ficherotemp', number_of_days, s3=False)
    # mongosetup.
    dbobject = MongoClient(os.getenv('MONGODB_HOST'), int(os.getenv('MONGODB_PORT')))
    database = dbobject.hadoop_sentiment_analysis
    collection = database[str(query)]

    with open('ficherotemp.json','r') as file:
        #we perform the sentiment_analysis.
        number_of_instances = os.getenv('INSTANCE_TYPE')
        number_of_core_instances = os.getenv('NUM_CORE_INSTANCES')
        mr_job = MRJOB(args=[file.name, '-r', 'emr', '--no-output',
                             '-c', './app/mrjob.conf','--instance-type',number_of_instances,
                             '--num-core-instances',number_of_core_instances])
        with mr_job.make_runner() as runner:
            runner.run()
            print("Lanzamos el job de map reduce")
            #we store sentiment results in a list of diccionaries.
            results=[{i[0]: i[1]} for i in mr_job.parse_output(runner.cat_output())]

            if len(results)>0:
                collection.insert_many(results)
                print('Resultados almacenados en base de datos con exito.')
            else:
                print('Error al insertar en mongodb. documents must be a non-empty list.')

if __name__ == '__main__':
    main()

