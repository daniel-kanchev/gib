import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from gib.items import Article


class GibspiderSpider(scrapy.Spider):
    name = 'gibspider'
    start_urls = ['https://www.gib.com/en/press-releases']

    def parse(self, response):
        dropdown_years = response.xpath('//select[@id="year"]/option/@value').getall()
        for year in dropdown_years:
            yield response.follow(f'https://www.gib.com/en/press-releases?year={year}', self.parse_year)

    def parse_year(self, response):
        articles = response.xpath('//div[@class="news-box-wrap"]')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./span[@class="press-date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3[@class="no-pad-top"]/text()').get()
        if title:
            title = title.strip()

        date = datetime.strptime(date.strip(), '%d.%m.%Y')
        date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="news-box-wrap no-border-bottom"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
