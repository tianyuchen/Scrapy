import re # Import Regex
import scrapy
import csv
from time import sleep

from scrapy.crawler import CrawlerProcess

from tutorial.items import JobDescriptionItem

ROOT_URL = 'http://jobs.careerpage.fr'
FILE_JOB_LIST = 'job_list.txt'
FILE_JOB_DESC = 'job_desc.csv'

# Store every url of the job in job_list.txt 
class JobListSpider(scrapy.Spider):
    name = "joblist"
    
    """ Return an iterable of Requests (a list of requests or a generator function) 
    which the Spider will begin to crawl from. Subsequent requests will be generated 
    successively from these initial requests. """
    def start_requests(self):
        self.urls = [
            'http://jobs.careerpage.fr/career/multiposting-jobs-fr/',
            'http://jobs.careerpage.fr/career/multiposting-internship-fr/'
        ]
        self.completed_count = 0
        self.job_links = [] 
        for url in self.urls:
        	# Callback: call parse function and send the result back 
            yield scrapy.Request(url=url, callback=self.parse) 

    """  a method that will be called to handle the response downloaded for 
    each of the requests made. The response parameter is an instance of TextResponse 
    that holds the page content and has further helpful methods to handle it.

	The parse() method usually parses the response, extracting the scraped data as dicts 
	and also finding new URLs to follow and creating new requests (Request) from them. """
    def parse(self, response):
        for table in response.css('table.results'): # <table class="results"
            for tr in table.xpath('tbody/tr'): #
                
                # Save job links in a list
                self.job_links.append(tr.xpath('td/a/@href').extract_first())
                
        # Count number of links obtained       
        self.completed_count += 1
        
        # When all urls obtained, call onJobListFetchFinish function 
        if self.completed_count == len(self.urls):
            self.onJobListFetchFinish()
    
    # Write all job links in a text file 
    def onJobListFetchFinish(self):
        print 'Fetch finished! Job link list: ', self.job_links
        f = open(FILE_JOB_LIST, 'w')
        for url in self.job_links:
            f.write(url + '\n')
        f.close()

# Get job's description and export in job_desc.csv         
class JobDescriptionSpider(scrapy.Spider):
    name = 'jobdescription'

    # Read FILE_JOB_LIST file and save separate line in urls list
    def read_urls(self):
        f = open(FILE_JOB_LIST, 'r')
        self.urls = f.readlines()
        f.close()
        
    def start_requests(self):
        self.read_urls()
        self.items = []
        self.completed_count = 0
        
        for url in self.urls:
            
            # Fill up the url with ROOT_URL 
            yield scrapy.Request(url=(ROOT_URL + url), callback=self.parse)

    def parse(self, response):
        item = JobDescriptionItem()
        
        # Get reference from link 
        match = re.match(r'.*/jobs/(\w+)', response.url) # re: Regular Expression 
        if match:
            item['reference'] = match.groups()[0]
        
        basic_info_holder = response.css('div.header')[0]
        basic_info = [i.extract() for i in basic_info_holder.xpath('.//ul//li/span[@class="value"]/text()')]
        
        item['title'] = basic_info_holder.xpath('h2/text()').extract_first()
        item['publication_date'] = basic_info[0]

        # Use Regular Expression to get country, location_name and postal_code from a string which contains all these information 
        match = re.match(r'^((?:\w|\s)+)\s\((\d{5})\),\s(\w+)$', basic_info[1])
        # w: Alphanumeric characters
        # s: Space
        # d: Digits 
        if (match):
            geos = match.groups()
            item['country'] = geos[2]
            item['location_name'] = geos[0]
            item['postal_code'] = geos[1]
        
        item['contract_type'] = basic_info[2]
        item['education_level'] = basic_info[3]
        item['experience_level'] = basic_info[4]
        
        # Use the combine of xpath and css method to obtain job_description and profile_description 
        desc_holder = response.css('ul.description')[0]
        li_list = desc_holder.xpath('.//li')
        
        # // is just an abbreviation for the descendant:: axis
        item['job_description'] = '\n'.join(li_list[0].xpath('.//p//descendant-or-self::text()').extract())
        item['profile_description'] = '\n'.join(li_list[1].xpath('.//p//descendant-or-self::text()').extract())
        
        self.items.append(item)
        self.completed_count += 1
        # When passed all job links, call onJobDescFetchFinish function
        if self.completed_count == len(self.urls):
            self.onJobDescFetchFinish()
    
    # Write all job's infos in a csv file
    def onJobDescFetchFinish(self):
        with open(FILE_JOB_DESC, 'w') as output:
            print "Begin to write in csv."
            fieldnames = ['reference', 'title', 'publication_date', 'country', 'location_name', 'postal_code', 
            'education_level', 'experience_level', 'contract_type', 'job_description', 'profile_description']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for job in self.items:
                writer.writerow(dict((k, v.encode('utf-8')) for k, v in job.iteritems()))
        print 'Done!'

