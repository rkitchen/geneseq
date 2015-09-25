from pymongo import MongoClient
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

db.mouse.drop()
db.create_collection('mouse')

# db.mouse.create_index('geneID', unique=True)


def doRead(row):
    """reads line from mouse expression data"""
    print(row)
    gene_id = row.pop('').split('.')[0]

    columns = dict()
    expr_data = list()

    i = 0
    for k, v in row.items():
        k = k.split(':')
        name = k[0]
        region = k[1]

        if name not in columns:
            columns[name] = (i, list())
            i += 1
            expr_data.append({'name': name, 'regions': list()})

        index = columns[name][0]

        if region not in columns[name][1]:
            columns[name][1].append(region)
            expr_data[index]['regions'].append({'region': region, 'values': list()})

        region_index = columns[name][1].index(region)

        expr_data[index]['regions'][region_index]['values'].append(float(v))

    d = dict()
    d['_id'] = gene_id
    d['expression'] = expr_data
    return d.copy()

pp = pprint.PrettyPrinter(indent=4)

f = open(filename, newline='\n')
reader = csv.DictReader(f, delimiter='\t', quotechar='"')
rawData = list()
count = 0
for row in reader:
    processed = doRead(row)
    pp.pprint(processed)
    db.mouse.insert_one(processed)
    count += 1
    # if count >= 5:
    #     break
f.close()
