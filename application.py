import logging
import json
import flask
import boto
import csv
import tinys3
import urllib
import os
import etl


from flask import request, Response , render_template

from boto.sqs  import *
from boto.sqs.message import RawMessage

from models import Restaurant,Inspection,Violation


application = flask.Flask(__name__)
application.config.from_object('config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']


@application.route('/process-task', methods=['POST'])
def process_task():
    """S3 Connection"""
    s3 = tinys3.Connection(application.config['AWS_ACCESS_KEY'],application.config['AWS_SECRET_KEY'],tls=False)
    
    """SQS Connection"""
    sqs = boto.sqs.connect_to_region(
        application.config['AWS_REGION'],
        aws_access_key_id=application.config['AWS_ACCESS_KEY'],
        aws_secret_access_key=application.config['AWS_SECRET_KEY']
    )
    task_queue = sqs.get_queue(application.config['AWS_WORKER_QUEUE'])


    """Process tasks from SQS """

    response = None
    if request.json is None:
        response = Response("", status=415)
    else:
        message = dict()
        try:
            message = request.json
            
            """Process Batch Task , Get data file and split into chunks and send sqs message to reprocess chunks"""
            
            if message['task'] == 'batch':
                
                """Download the file from the task url """
                
                urllib.urlretrieve(message['url'], "data.csv")
                
                """ Split the file into chunks  """
                file_chunks  = etl.split(open('data.csv', 'r'))
                os.remove('data.csv')
                
                """ Upload files to S3 and send tasks to SQS for Data processing  """
                for file in file_chunks:
                    f = open(file,'rb')
                    s3.upload(file,f,'etl-test-data')
                    os.remove(file)
                    
                    """ Send SQS Message with chunk file data """ 
                    data = {
                        "task":"process",
                        "bucket_name": "etl-test-data",
                        "file_name":file
                    }
                    sqs_message = RawMessage()
                    sqs_message.set_body(json.dumps(data))
                    
                    task_queue.write(sqs_message)
                    
            """Process Chunks , Load Data"""

            if message['task'] == 'process':
              
                """Download file from S3"""    
                s3_response = s3.get(message['file_name'], message['bucket_name'])
                if s3_response.status_code == 200:
                   
                    
                    s3_file = open(message['file_name'], 'w') 
                    s3_file.write(s3_response.content)
                    s3_file.close()
                    
                    """Prcoess downloaded file"""
                    local_file = open(message['file_name'])
                    etl.process_file(local_file)
                    
            response = Response("", status=200)
        except Exception as ex:
            logging.exception('Error processing message: %s' % request.json)
            response = Response(ex.message, status=500)

    return response
    
    
@application.route('/', methods=['GET'])
def index():
    restaurants = Restaurant.objects(cuisine="thai",grade__in=["A","B"]).order_by('grade','name')[:10]
    return render_template('index.html',restaurants=restaurants)



if __name__ == '__main__':
    application.run(host='0.0.0.0')