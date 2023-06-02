import scrapy

from scrapy.crawler import CrawlerProcess
from apscheduler.schedulers.twisted import TwistedScheduler
from datetime import datetime, timedelta


class UnispiderSpider(scrapy.Spider):
    name = "unispider"
    allowed_domains = [ "pureportal.coventry.ac.uk", "pureportal.coventry.ac.uk/en/persons/"] 
    #so that the scarper doesn't scrape the entire internet
    start_urls = ["https://pureportal.coventry.ac.uk/en/persons"]

    def parse(self, response):
        persons = response.css('div.result-container')
        for person in persons:
            if person.css('ul li span.minor.dimmed::text').get() != None:
                    person_url =  person.css('h3 a').attrib['href'] 
                    publication_url = person_url + "/publications/"
                    yield response.follow(publication_url, callback = self.parse_person_pubs)

        next_page = response.css("li.next a ::attr(href)").get()
        if  next_page is not None:
            next_page_url = "https://pureportal.coventry.ac.uk" + next_page
            yield response.follow(next_page_url, callback = self.parse)

    def parse_person_pubs(self, response):
        publications = response.css("div.result-container h3.title")
        for publication in publications:
            doc_link = publication.css("a ::attr('href')").get()

            yield response.follow(doc_link, callback=self.get_abstract, meta={'publication': publication, 'rp' : response})

    def get_abstract(self, response):
        doc_abstract = response.xpath('//*[@id="main-content"]/section[1]/div/div/div[1]/div[1]/div/text()').get()
        publication = response.meta['publication']
        rp = response.meta['rp']

        yield {
            "name": rp.css('div.header.person-details h1::text').get(),
            "job_title": rp.css('span.job-title::text').get(),
            "organization": rp.css('a.link.primary span::text').get(),
            "doc_link": publication.css("a::attr(href)").get(),
            "doc_title": publication.css("span::text").get(),
            "doc_abstract": doc_abstract,
        }


# Create a scheduler
scheduler = TwistedScheduler()

# Schedule the spider to run every 14 days
scheduler.add_job(
    lambda: CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}).crawl(UnispiderSpider),
    'interval',
    days=14,
    start_date=datetime.now() + timedelta(days=1)  # Start the first run tomorrow
)

# Start the scheduler
scheduler.start()


# Make sure to adjust the allowed_domains and start_urls according to your target website. The scheduler is set to run the spider every 14 days, and the first run will start tomorrow. You can modify the start_date to your preferred starting time.

# To run the script, simply execute the following command in your terminal:

# Copy code
# python my_spider.py
# The spider will automatically crawl the website every 14 days based on the scheduled interval.