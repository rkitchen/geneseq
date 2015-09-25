from pymongo import MongoClient
import sys
import csv
import pprint

args = sys.argv
if len(args) <= 1:
    print('Must enter filename for mouse expression data')
    sys.exit(1)

filename = args[1]

client = MongoClient()
db = client.gene_locale


def doRead(row):
    """reads line from mouse expression data"""
    print(row)
    d = dict()
    expr = dict()
    expr['type'] = row['celltype']
    expr['expression'] = float(row['ExpressionInThisCellType(TPM)'])
    expr['enrichment'] = float(row['FoldEnrichmentOverNextBestCellType'])
    expr['human_id'] = row['GeneID_human']
    expr['human_name'] = row['GeneName']

    d['filter'] = {'_id': row['GeneID_mouse']}
    d['update'] = {'$set': {'processed': expr}}
    d['upsert'] = False
    return d.copy()

pp = pprint.PrettyPrinter(indent=4)

f = open(filename, newline='\n')
reader = csv.DictReader(f, delimiter='\t', quotechar='"')
rawData = list()
errors = list()
count = 0
for row in reader:
    processed = doRead(row)
    pp.pprint(processed)

    db.mouse.update_one(**processed)
    count += 1
f.close()
