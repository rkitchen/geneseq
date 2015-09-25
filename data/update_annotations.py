from pymongo import MongoClient
import pymongo
import csv
import pprint
import sys

args = sys.argv
if len(args) <= 1:
    print('Must enter filename for mouse expression data')
    sys.exit(1)

filename = args[1]

client = MongoClient()
db = client.gene_locale

db.mouse_annotations.drop()
db.create_collection('mouse_annotations')
db.mouse_annotations.create_index('level1', unique=True)

pp = pprint.PrettyPrinter(indent=4)

f = open(filename, newline='\n')
reader = csv.DictReader(f, delimiter='\t', quotechar='"')

for row in reader:
    _id = row['sampleID'].split(':')
    db.mouse_annotations.find({'level1': _id[0]})
    pp.pprint(row)
    d = dict()
    d['level1'] = _id[0]
    d['level2'] = row['level2']
    d['level3'] = row['level3_celltype']
    d['level4'] = row['level4']
    d['regions'] = [_id[1]]
    d['method'] = row['method']
    d['protected'] = (row['protected'] == 'private')

    try:
        db.mouse_annotations.insert_one(d)
    except pymongo.errors.DuplicateKeyError:
        db.mouse_annotations.update_one({'level1': _id[0]}, {'$push': {'regions': _id[1]}})
f.close()
