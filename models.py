from mongoengine import *
import datetime
import os
import csv
import urllib
import logging

connect(
    db='nyc_restaurants',
    username='user',
    password='password',
    host='mongodb://user:password@ds113000.mlab.com:13000/nyc_restaurants'
)

class Violation(Document):
    code = StringField(max_length=10, required=True)
    description = StringField()
    critical_flag = StringField()

class Inspection(Document):
    restaurnt_id = IntField(required=True)
    inspection_date = DateTimeField(required=True)
    action = StringField()
    score = IntField()
    grade =  StringField(max_length=10)
    grade_date = DateTimeField()
    record_date = DateTimeField()
    type = StringField()
    violations = ListField(ReferenceField(Violation))



class Restaurant(Document):
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
