#!/bin/bash
S3_OUTPUT_BUCKET=REPLACE_ME
PREFIX=`python -c 'import uuid; print str(uuid.uuid1())'`
splits=(`ls ./input/actual`)

echo "Output is stored at s3://$S3_OUTPUT_BUCKET/$PREFIX/"

for i in ${splits[@]}; do
  echo "Running job for split ${i}"
   `python phone_numbers_text.py -r emr --pool-emr-job-flows --pool-wait-minutes=1 --conf-path mrjob.conf \
  --no-output --output-dir s3://$S3_OUTPUT_BUCKET/$PREFIX/${i} input/actual/${i}`
  echo "split finished."
done