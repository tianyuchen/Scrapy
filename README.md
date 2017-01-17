## Objectif:

This project is aiming at exporting data to a CSV file from web pages.
Here, we need to the get information of the job at Http://jobs.careerpage.com/career/multiposting-jobs-en/ and http://jobs.careerpage.com/career/multiposting-internship-en/.

## Usage:

Launching the program, you need to run the spiders:

    $ scrapy crawl joblist
    
    $ scrapy crawl jobdescription
    
It will generate a job_desc.csv file which contains all job's information.    
    
