import scrapy


class MyItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    publication_date  = scrapy.Field()
    description = scrapy.Field()
    body = scrapy.Field()
