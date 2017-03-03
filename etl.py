import os
import csv
import uuid
import models
import datetime

from models import Restaurant,Inspection,Violation

def split(filehandler, delimiter=',', row_limit=1000,
      output_name_template=str(uuid.uuid4())+'_%s.csv', output_path='.', keep_headers=True):

    """
        Split CSV into Chunks
        @return List of file names
    """
    
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    file_chunks = [ output_name_template % current_piece]
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            file_chunks.append(output_name_template % current_piece)
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)
    
    return file_chunks


def process_file(filehandler,delimiter=','):
    
    """Process CSV file to insert data into DB"""
    
    reader = csv.reader(filehandler)
    headers = next(reader)
    headers = tuple(header.lower().replace(' ', '_') for header in headers)
    for num, line in enumerate(reader):
        record = {header: value for header, value in zip(headers, line)}
        # Cast record to correct type
        record['camis'] = int(record['camis'])
        try:
            record['score'] = int(record['score'])
        except ValueError:
            record['score'] = None
        try:
            record['inspection_date'] = datetime.datetime.strptime(
                    record['inspection_date'], '%m/%d/%Y')
        except ValueError:
            record['inspection_date'] = None
        try:
            record['grade_date'] = datetime.datetime.strptime(
                    record['grade_date'], '%m/%d/%Y')
        except ValueError:
            record['grade_date'] = None
        try:
            record['record_date'] = datetime.datetime.strptime(
                    record['record_date'], '%m/%d/%Y')
        except ValueError:
            record['record_date'] = None
        record['cuisine_description'] = [
            x.strip().lower() for x in record['cuisine_description'].split(',')
        ]
    
        if record['violation_code']:
            violation = Violation.objects(code = record['violation_code']).first()
            if violation is None:
                violation = Violation(
                                code = record['violation_code'],
                                description = record['violation_description'],
                                critical_flag = record['critical_flag']
                            )
                violation.save()
    
        inspection = Inspection.objects(restaurnt_id = record['camis'],inspection_date=record['inspection_date']).first()
        if inspection is None:
            inspection = Inspection(
                                restaurnt_id = record['camis'],
                                inspection_date = record['inspection_date'],
                                action = record['action'],
                                score = record['score'],
                                grade =  record['grade'],
                                grade_date = record['grade_date'],
                                record_date = record['record_date'],
                                type = record['inspection_type']
                        )
            inspection.save()
        inspection.update(add_to_set__violations=[violation])
    
        restaurant = Restaurant.objects(restaurnt_id = record['camis']).first()
        if restaurant is None:
            restaurant = Restaurant(
                            restaurnt_id = record['camis'],
                            name = record['dba'],
                            boro = record['boro'],
                            building = record['building'],
                            street = record['street'],
                            zipcode = record['zipcode'],
                            phone = record['phone'],
                            cuisine = record['cuisine_description'],
                            grade =  record['grade'],
                            grade_date = record['grade_date'],
                            record_date = record['record_date']
                        )
            restaurant.save()

        elif(restaurant.grade_date is None or
                      record['grade_date'] and
                      record['grade_date'] > restaurant.grade_date):
            restaurant.grade = record['grade']
            restaurant.grade_date = record['grade_date']
            restaurant.save()
                    
        restaurant.update(add_to_set__inspections=[inspection])
