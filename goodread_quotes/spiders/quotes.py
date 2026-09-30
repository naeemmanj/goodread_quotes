import scrapy
from scrapling.fetchers import Fetcher
from urllib.parse import urljoin


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["goodreads.com"]
    start_urls = ["https://www.goodreads.com/quotes"]

    author_no = 1

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True
            )

    def parse(self, response):
        url = response.url

        print("Page URL:", url)

        page = Fetcher.get(url)

        print("Status:", page.status)

        page_title = page.xpath("//title/text()").get()
        print("Page Title:", page_title)

        for quote in self.extract_quotes(page):
            quote["Author No"] = self.author_no
            yield quote
            self.author_no += 1

        next_url = self.get_next_page(page, url)

        if next_url:
            print("Next page:", next_url)

            yield scrapy.Request(
                next_url,
                callback=self.parse,
                dont_filter=True
            )

    def extract_quotes(self, page):
        quotes = page.xpath("//div[@class='quote']")

        for quote in quotes:
            author_name = quote.xpath(".//span[@class='authorOrTitle']/text()").get()
            author_quote = quote.xpath(".//div[@class='quoteText']/text()[1]").get()
            author_image = quote.xpath(".//img/@src").get()
            author_likes = quote.xpath(".//a[@class='smallText']/text()").get()
            yield {
                "Author Name": author_name.strip(),
                "Author Quote": author_quote.strip(),
                "Author Image": author_image,
                "Author Likes": author_likes.strip(),
            }

    def get_next_page(self, page, current_url):
        next_url = page.xpath("//a[@class='next_page']/@href").get()

        if next_url:
            return urljoin(current_url, next_url)
        return None