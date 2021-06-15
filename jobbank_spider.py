import scrapy
from scrapy.crawler import CrawlerProcess

class JobBank(scrapy.Spider):
    name = "JobBankSpider"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Data.csv',
    }


    with open("towns.txt") as f:
        cities = f.readlines()

    def start_requests(self):
        for city in self.cities:
            yield scrapy.Request(url="https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=" + city + "&sort=D",
                                 callback=self.parse, dont_filter=True,
                             headers={
                                 'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                             },
                             )

    def parse(self, response):
        results = response.css("span.found::text").extract_first()
        results = results.replace(",", "")
        pages = int(results) // 25
        for i in range(1, pages + 2):
            yield scrapy.Request(url=response.url + "&page=" + str(i),
                                 callback=self.parse2, dont_filter=True,
                                 headers={
                                     'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                                 },
                                 )

    def parse2(self, response):
        results = response.css("div#result_block > article")
        for res in results:
            url = "https://www.jobbank.gc.ca" + res.css("a::attr(href)").extract_first()
            title = res.css("span.noctitle::text").extract_first()
            date = res.css("li.date::text").extract_first()
            company = res.css("li.business::text").extract_first()
            location = res.css("li.location::text").extract()
            location = location[-1].strip()
            salary = res.css("span.salary-item > span::text").extract_first()
            if not salary:
                salary = "N/A"

            yield {
                "Title": title.strip(),
                "Company": company.strip(),
                "Location": location.strip(),
                "Date": date.strip(),
                "Salary": salary.strip(),
                "URL": url,
            }






process = CrawlerProcess()
process.crawl(JobBank)
process.start()
