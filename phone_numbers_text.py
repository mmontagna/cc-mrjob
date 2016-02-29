import re, gzip, boto, warc, csv, phonenumbers
from boto.s3.key import Key
from gzipstream import GzipStreamFile
from mrjob.job import MRJob

#Accept the phone number if fax isn't in the surrounding text.
def acceptPhoneNumber(url, surrounding):
  return 'fax' not in surrounding

class PhoneNumberExtractor(MRJob):

  def mapper(self, _, line):
    f = None
    if True or self.options.runner != 'inline':#self.options.runner in ['emr', 'hadoop']:
      print 'Loading remote file {}'.format(line)

      # Connect to Amazon S3 using anonymous credentials
      conn = boto.connect_s3(anon=True)
      pds = conn.get_bucket('aws-publicdatasets')
      # Start a connection to one of the WARC files
      k = Key(pds, line)
      f = warc.WARCFile(fileobj=GzipStreamFile(k))
    else:
      print 'Loading local file {}'.format(line)
      f = warc.WARCFile(fileobj=gzip.open(line))

    for i, record in enumerate(f):
      for key, value in self.process_record(record):
        yield key, value
      self.increment_counter('commoncrawl', 'processed_records', 1)

  def combiner(self, key, value):
    yield key, sum(value)

  def reducer(self, key, value):
    yield key, sum(value)

  def process_record(self, record):
    if record['Content-Type'] != 'text/plain':
      return

    payload = record.payload.read()

    #WET content is already in utf-8
    body = unicode(payload.lower(), 'utf-8', errors='replace')
    for match in phonenumbers.PhoneNumberMatcher(body, None):
      try:
        standard_num = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
      except Exception as e:
        print e
        continue #Must be a junk number
      #Pass the surrounding 10 characters.
      if (acceptPhoneNumber(record.url, body[max(0,match.start - 10):min(match.end + 10, len(body))])):
        yield standard_num, 1

if __name__ == '__main__':
  PhoneNumberExtractor.run()

