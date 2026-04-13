import scrapy

class SecSpider(scrapy.Spider):
    name = "sec_spider"
    allowed_domains = ["sec.gov", "www.sec.gov"]

    page_count = 0
    max_pages = 50

    start_urls = ["https://www.sec.gov/newsroom/press-releases"]

    def parse(self, response):
        self.page_count += 1

        for row in response.css('tr.pr-list-page-row'):
            date = row.css('td.views-field-field-publish-date time::text').get('').strip()
            title = row.css('td.views-field-field-display-title a::text').get('').strip()
            link = row.css('td.views-field-field-display-title a::attr(href)').get('')
            pr_number = row.css('td.views-field-field-release-number::text').get('').strip()

            if link:
                full_link = response.urljoin(link)
                yield scrapy.Request(
                    full_link,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'date': date,
                        'pr_number': pr_number,
                        'link': full_link,
                    }
                )

        if self.page_count < self.max_pages:
            next_page = response.css('a[rel="next"]::attr(href)').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        content = ' '.join(response.css('div.field--name-body *::text').getall()).strip()

        yield {
            'title': response.meta['title'],
            'date': response.meta['date'],
            'pr_number': response.meta['pr_number'],
            'link': response.meta['link'],
            'content': content,
        }
