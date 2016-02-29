import MySQLdb, csv, os
from collections import Counter

db = MySQLdb.connect(host=os.environ['db_host'],
                        user=os.environ['db_user'],
                        passwd=os.environ['db_password'],
                        db=os.environ['db_name'],
                        use_unicode=True,
                        charset='utf8',
                        )

def getPrefix(number, db):
  number = number.strip('+')
  q = "SELECT zones_id, prefix FROM prefixes, zones WHERE '"+ number + "' LIKE CONCAT(prefix,'%') and prefixes.retired is null ORDER BY length(prefix) DESC LIMIT 1"
  c = db.cursor()
  c.execute(q)
  result = c.fetchall()

  if (len(result) > 0):
    return result[0]
  return (None, None)

"""
"""
def insertNumber(number, zone_id, prefix, db):
  number = number.strip('+')
  q = "INSERT INTO numbers_pool (`number`, `lastUsedTime`, `zones_id`, `prefixes_prefix`) VALUES (%s, NOW(), %s, %s);"
  c = db.cursor()
  c.execute(q, [number, int(zone_id), prefix])
  db.commit()

files = 'output_from_s3'

numbers = {}

for root, dirnames, filenames in os.walk(files):
  for filename in filenames:
    with open(os.path.join(root, filename), 'rb') as csvfile:
      reader = csv.reader(csvfile, delimiter="\t", quotechar='"')
      for row in reader:
        numbers[row[0]] = row[0]



with open('output_for_mysql_load.txt', 'w') as csvfile:
  writer = csv.writer(csvfile, delimiter="\t", quotechar='"')
  for number in numbers:
    zone_id, prefix = getPrefix(number, db)
    if (zone_id is not None and prefix is not None):
      writer.writerow((number.strip('+'), zone_id, prefix))
      insertNumber(number, zone_id, prefix, db)