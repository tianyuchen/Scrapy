import scrapy

class JobDescriptionItem(scrapy.Item):
    reference = scrapy.Field()
    title = scrapy.Field()
    publication_date = scrapy.Field()
    country = scrapy.Field()
    location_name = scrapy.Field()
    postal_code = scrapy.Field()
    education_level = scrapy.Field()
    experience_level = scrapy.Field()
    contract_type = scrapy.Field()
    job_description = scrapy.Field()
    profile_description = scrapy.Field()
    
