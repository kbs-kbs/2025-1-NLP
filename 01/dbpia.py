import scrapy
from scrapy_playwright.page import PageMethod
import time
import math

class DbpiaSpider(scrapy.Spider):
    name = 'dbpia'
    allowed_domains = ['www.dbpia.co.kr']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = input('검색어를 입력해주세요: ')
        self.node_ids = []
        self.max_pages = 0
        self.pages_crawled = 0
        self.start_time = time.time()

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://www.dbpia.co.kr/search/topSearch?searchOption=all&query={self.query}#a',
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "#totalCount")
                ],
                "playwright_page_goto_kwargs": {
                    "timeout": 200000,
                    "wait_until": "domcontentloaded"
                },
            },
            callback=self.parse_node_count
        )

    async def parse_node_count(self, response):
        node_count = int(response.css('#totalCount::text').get().replace('건', '').replace(',', ''))
        self.inform('논문 개수', node_count)

        page = response.meta["playwright_page"]
        if node_count == 0:
            return
        elif node_count > 20:
            self.max_pages = math.ceil(node_count/100)
            await page.wait_for_selector('#selectWrapper')
            element = await page.query_selector('#selectWrapper')
            await element.click()
            await page.wait_for_selector('#get100PerPage')
            element = await page.query_selector('#get100PerPage')
            await element.click()
        else:
            self.max_pages = 1
        await page.wait_for_load_state('load')
        updated_html = await page.content()
        self.inform('최대 페이지 수', self.max_pages)

        while True:
            new_response = scrapy.http.HtmlResponse(
                url=response.url,
                body=updated_html,
                encoding="utf-8",
                request=response.request
            )
            self.parse_node_ids(new_response)

            if self.pages_crawled < self.max_pages:
                await self.click_next_button(page)
                await page.wait_for_load_state('load')
                updated_html = await page.content()
            else: break
        
        for node_id in self.node_ids:
            if 'NODE' in node_id:
                yield scrapy.Request(
                    url=f'https://www.dbpia.co.kr/journal/articleDetail?nodeId={node_id}',
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_goto_kwargs": {
                            "timeout": 200000,
                            "wait_until": "domcontentloaded"
                        },
                    },
                    callback=self.parse_article_detail_page
                )
            else:
                yield scrapy.Request(
                    url=f'https://www.dbpia.co.kr/journal/detail?nodeId={node_id}',
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_goto_kwargs": {
                            "timeout": 200000,
                            "wait_until": "domcontentloaded"
                        },
                    },
                    callback=self.parse_detail_page
                )

    def parse_node_ids(self, response):
        self.node_ids += response.css('#searchResultList section.thesisAdditionalInfo.thesis__info::attr(data-nodeid)').getall()
        self.pages_crawled += 1
        self.inform('완료한 페이지', self.pages_crawled, '노드 리스트', self.node_ids)

    async def click_next_button(self, page):
        if self.pages_crawled%10 < 10:
            next_button = await page.query_selector(f'#pageList a:nth-child({self.pages_crawled%10 + 2})')
        else:
            next_button = await page.query_selector('#goNextPage')
        await next_button.click()

    async def parse_article_detail_page(self, response):
        title = response.css('#thesisTitle::text').get()
        issue_year = response.css('section.thesisDetail__journal > ul > li:nth-child(4) > span:nth-child(1)').get()
        abstract = response.css('div.abstractTxt::text').get()
        self.inform('제목', title, '발행 연도', issue_year, '초록', abstract)

        page = response.meta["playwright_page"]
        await page.close()

    async def parse_detail_page(self, response):
        title = response.css('#thesisTitle::text').get()
        issue_year = response.css('p.projectDetail__advisoir__desc::text').get()
        abstract = response.css('div.abstractTxt::text').get()
        self.inform('제목', title, '발행 연도', issue_year, '초록', abstract)

        page = response.meta["playwright_page"]
        await page.close()

    def inform(self, name, value, *args):
        info = {name: value}
        if args:
            info.update({args[i]: args[i + 1] for i in range(0, len(args), 2)})
        self.logger.info(f'{info} ({(time.time() - self.start_time):.1f}초)')
