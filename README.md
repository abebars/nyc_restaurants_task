# ETL Task : NYC Restaurants Open Data
NYC Open Data ETL Task

URL : http://webserver.vmkf2pdkpu.us-east-2.elasticbeanstalk.com/

Archtuicture :
Servers : Application hosted on AWS Beanstalk (WebServer , Workers)
Database : MongoDb

Work Flow:
AWS Beanstalk - Fleet of Workers are looking for new sqs to process the data 

{"task":"batch","url":"https://nycopendata.socrata.com/api/views/xx67-kt59/rows.csv?accessType=DOWNLOAD"}

Once the worker pickup the message will split the file into chunks and upload chunks to s3 and send another sqs messagae to process the chunks

{"task":"process","bucket_name": "etl-test-data","file_name":'26aebd59-a97e-440c-9a23-2f5cfc534817_1.csv'}

When this message recieved the work will get the chunk file from s3 , validate , load the data to MongoDb



DB Choice : MongoDB
The application may load data from differnet sources as ETL Application , NoSQL will be suitable to this case

Databased Schema : 
```
 Violation:
    code = StringField(max_length=10, required=True)
    description = StringField()
    critical_flag = StringField()

 Inspection:
    restaurnt_id = IntField(required=True)
    inspection_date = DateTimeField(required=True)
    action = StringField()
    score = IntField()
    grade =  StringField(max_length=10)
    grade_date = DateTimeField()
    record_date = DateTimeField()
    type = StringField()
    violations = ListField(ReferenceField(Violation))

 Restaurant:
    restaurnt_id = IntField(required=True)
    name = StringField(required=True)
    boro = StringField(required=True)
    building = StringField(required=True)
    street = StringField(required=True)
    zipcode = IntField()
    phone = StringField(required=True)
    cuisine = ListField(StringField(max_length=100))
    grade =  StringField(max_length=10)
    grade_date = DateTimeField()
    record_date = DateTimeField()
    inspections = ListField(ReferenceField(Inspection))
