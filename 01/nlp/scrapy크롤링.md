# 필요한 라이브러리 설치
!pip install scrapy pandas

import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from google.colab import files

class DbpiaSpider(scrapy.Spider):
    name = "dbpia"
    allowed_domains = ["dbpia.co.kr"]
    
    def __init__(self, search='', min_year='', max_year='', *args, **kwargs):
        super(DbpiaSpider, self).__init__(*args, **kwargs)
        self.search = search
        self.min_year = min_year
        self.max_year = max_year
        self.results = []

    def start_requests(self):
        base_url = f"https://www.dbpia.co.kr/search/topSearch?searchOption=all&query={self.search}"
        yield scrapy.Request(url=base_url, callback=self.parse_search)

    def parse_search(self, response):
        article_links = response.css('article a::attr(href)').getall()
        for link in article_links:
            full_link = response.urljoin(link)
            yield scrapy.Request(url=full_link, callback=self.parse_article)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse_search)

    def parse_article(self, response):
        title = response.css('h1.thesisDetail__tit::text').get()
        year_text = response.css('li.journalList__item span::text').getall()
        year = year_text[3] if len(year_text) > 3 else None
        
        if year and self.min_year <= year <= self.max_year:
            keywords_list = response.css('a.keywordWrap__keyword::text').getall()
            keywords_list = [kw.replace("#", "").strip() for kw in keywords_list]

            abstract_elem = response.css('div.abstractTxt::text').get()
            abstract_parts = abstract_elem.split('  ') if abstract_elem else []
            abstract = abstract_parts[0].strip() if len(abstract_parts) > 0 else None
            multilingual_abstract = abstract_parts[1].strip() if len(abstract_parts) > 1 else None

            self.results.append({
                'title': title,
                'year': year,
                'keywords': keywords_list,
                'abstract': abstract,
                'multilingual_abstract': multilingual_abstract,
            })

# 사용자 입력 받기
search = input("검색할 키워드: ").strip()
min_year = input("추출할 최소 년도를 입력: ").strip()
max_year = input("추출할 최대 년도를 입력: ").strip()

# Scrapy 프로세스 설정 및 실행
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
})

spider = DbpiaSpider(search=search, min_year=min_year, max_year=max_year)
process.crawl(spider)
process.start()

# 크롤링 결과를 DataFrame으로 변환
df = pd.DataFrame(spider.results)

# CSV 파일로 저장
csv_filename = f"{search}_{min_year}_{max_year}_dbpia.csv"
df.to_csv(csv_filename, index=False)

# 파일 다운로드
files.download(csv_filename)

print(f"크롤링이 완료되었습니다. 총 {len(df)} 개의 논문 정보를 수집했습니다.")
print(f"결과가 {csv_filename} 파일로 저장되었습니다.")
