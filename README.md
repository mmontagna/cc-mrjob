### Running the phone number extractor

* Find a recent common crawl here (http://blog.commoncrawl.org/) download a WET file manifest 'wet.paths.gz'.
* Unzip the manifest and place it in the input folder.
* Split the manifest into many jobs `split -l 3648 ./input/wet.paths ./input/actual/`
* Edit ./run_phone_number_extract_jobs.sh and fill in your desired s3 output bucket.
* Edit mrjob.config (add at least aws_access_key_id & aws_secret_access_key,
you will also want to review the instance config, spot price, number, type, etc...).
* Run ./run_phone_number_extract_jobs.sh -> this will print an s3 output prefix/localtion
### Once all jobs complete
* Copy the output from s3 `aws s3 sync [the s3 output prefix from above] ./actual_output`
* To import the found numbers into your MySQL DB you'll need to set the following environment variables:
    * db_host
    * db_user
    * db_password
    * db_name
* Then run `python import_into_db.py` (you will need to have installed python's MySQLdb package).

If the process gets stuck or a job fails, that is OK. You can just delete the split files that
suceeded from `./input/wet.paths` and then rerun the process.

![Common Crawl Logo](http://commoncrawl.org/wp-content/uploads/2012/04/ccLogo.png)

# mrjob starter kit

This project demonstrates using Python to process the Common Crawl dataset with the mrjob framework.
There are three tasks to run using the three different data formats:

+ Counting HTML tags using Common Crawl's raw response data (WARC files)
+ Analysis of web servers using Common Crawl's metadata (WAT files)
+ Word count using Common Crawl's extract text (WET files)

## Setup

To develop locally, you will need to install the `mrjob` Hadoop streaming framework, the `boto` library for AWS, the `warc` library for accessing the web data, and `gzipstream` to allow Python stream decompress gzip files.

This can all be done using `pip`:

    pip install -r requirements.txt

If you would like to create a virtual environment to protect local dependencies:

    virtualenv --no-site-packages env/
    source env/bin/activate
    pip install -r requirements.txt

To develop locally, you'll need at least three data files -- one for each format the crawl uses.
These can either be downloaded by running the `get-data.sh` command line program or manually by grabbing the [WARC](https://aws-publicdatasets.s3.amazonaws.com/common-crawl/crawl-data/CC-MAIN-2014-35/segments/1408500800168.29/warc/CC-MAIN-20140820021320-00000-ip-10-180-136-8.ec2.internal.warc.gz), [WAT](https://aws-publicdatasets.s3.amazonaws.com/common-crawl/crawl-data/CC-MAIN-2014-35/segments/1408500800168.29/wat/CC-MAIN-20140820021320-00000-ip-10-180-136-8.ec2.internal.warc.wat.gz), and [WET](https://aws-publicdatasets.s3.amazonaws.com/common-crawl/crawl-data/CC-MAIN-2014-35/segments/1408500800168.29/wet/CC-MAIN-20140820021320-00000-ip-10-180-136-8.ec2.internal.warc.wet.gz) files.

## Running the code

The example code includes three tasks, the first of which runs a HTML tag counter over the raw web data.
One could use it to see how well HTML5 is being adopted or to see how strangely people use heading tags.

    "h1" 520487
    "h2" 1444041
    "h3" 1958891
    "h4" 1149127
    "h5" 368755
    "h6" 245941
    "h7" 1043
    "h8" 29
    "h10" 3
    "h11" 5
    "h12" 3
    "h13" 4
    "h14" 19
    "h15" 5
    "h21" 1

We'll be using `tag_counter.py` as our primary task, which runs over WARC files.
To run the other examples, `server_analysis.py` (WAT) or `word_count.py` (WET), simply run that Python script whilst using the relevant input format.

### Running locally

Running the code locally is made incredibly simple thanks to mrjob.
Developing and testing your code doesn't actually need a Hadoop installation.

First, you'll need to get the relevant demo data locally, which can be done by running:

    ./get-data.sh

If you're on Windows, you just need to download the files listed and place them in the appropriate folders.

Once you have the data, to run the tasks locally, you can simply run:

    python tag_counter.py --conf-path mrjob.conf --no-output --output-dir out input/test-1.warc
    # or 'local' simulates more features of Hadoop such as counters
    python tag_counter.py -r local --conf-path mrjob.conf --no-output --output-dir out input/test-1.warc

### Running via Elastic MapReduce

As the Common Crawl dataset lives in the Amazon Public Datasets program, you can access and process it without incurring any transfer costs.
The only cost that you incur is the cost of the machines and Elastic MapReduce itself.

By default, EMR machines run with Python 2.6.
The configuration file automatically installs Python 2.7 on your cluster for you.
The steps to do this are documented in `mrjob.conf`.

To run the job on Amazon Elastic MapReduce (their automated Hadoop cluster offering), you need to add your AWS access key ID and AWS access key to `mrjob.conf`.
By default, the configuration file only launches two machines, both using spot instances to be cost effective.

    python tag_counter.py -r emr --conf-path mrjob.conf --no-output --output-dir out input/test-100.warc

If you are running this for a full fledged job, you will likely want to make the master server a normal instance, as spot instances can disappear at any time.

## Running it over all Common Crawl

To run your mrjob task over the entirety of the Common Crawl dataset, you can use download the WARC file listing found at `CC-MAIN-YYYY-WW/warc.paths.gz`.

As an example, the [August 2014 crawl](http://commoncrawl.org/august-2014-crawl-data-available/) has 52,849 WARC files listed by [warc.paths.gz](https://aws-publicdatasets.s3.amazonaws.com/common-crawl/crawl-data/CC-MAIN-2014-35/warc.paths.gz).

It is highly recommended to run over batches of WARC files at a time and then perform a secondary reduce over those results.
Running a single job over the entirety of the dataset complicates the situation substantially.

You'll also want to place your results in an S3 bucket instead of having them streamed back to your local machine.
For full details on this, refer to the mrjob documentation.

## Running with PyPy

If you're interested in using PyPy for a speed boost, you can look at the [source code](https://github.com/mcroydon/social-graph-analysis) from **Social Graph Analysis using Elastic MapReduce and PyPy**.

## License

MIT License, as per `LICENSE`
