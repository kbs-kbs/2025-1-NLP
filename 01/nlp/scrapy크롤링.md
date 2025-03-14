# scrapy-splash API예제
- curl: http 요청을 보내는 프로그램/명령어
- 터미널에서 splash 서버의 api를 통해 렌더링된 페이지 반환

- `http://localhost:8050/render.html?url=https://example.com`과 같은 요청을 보내면, Splash는 example.com 페이지를 로드하고 JavaScript를 실행한 후의 최종 HTML을 반환합니다.

- POST 방식
```bash
curl --location 'http://localhost:8050/render.html' \
--header 'content-type: application/json' \
--data '{"url": "https://quotes.toscrape.com/js/"}'
```

- GET 방식
```
curl 'http://localhost:8050/render.html?url=https://quotes.toscrape.com/js/'
```

Splash API를 통해 버튼 클릭 후 렌더링된 새 페이지를 가져오려면 Lua 스크립트를 활용해야 합니다. render.html 엔드포인트만으로는 클릭 동작을 시뮬레이션할 수 없으며, execute 엔드포인트를 사용해야 합니다.

구현 방법 (CURL 예시)
```bash
curl --location 'http://localhost:8050/execute' \
--header 'Content-Type: application/json' \
--data '{
  "lua_source": "
    function main(splash)
      splash:go(\"https://quotes.toscrape.com/js/\")
      splash:wait(1.0)
      
      -- 버튼 선택 및 클릭 (예: Next 버튼)
      local btn = splash:select(\"a.next\")
      btn:click()
      
      splash:wait(1.0)  -- 새 콘텐츠 로딩 대기
      return splash:html()
    end
  "
}'
```


- 코드로
Splash로 웹 스크래핑하려면 전송된 각 요청에서 얻은 HTML을 캡처해야 합니다. 따라서 CURL 대신 Python requests를 사용하여 위의 요청을 전송해 보겠습니다.
```
import requests
import json

url = "http://localhost:8050/render.html"

payload = json.dumps({
  "url": "https://web-scraping.dev/products" # page URL to render
})
headers = {
  'content-type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
"""
<!DOCTYPE html><html lang="en"><head>
    <meta charset="utf-8">
<title>web-scraping.dev product page 1</title>    
"""
```

```
from scrapy_splash import SplashRequest

class MySpider(scrapy.Spider):
    name = 'my_spider'

    def start_requests(self):
        yield SplashRequest(
            url='http://example.com',
            callback=self.parse,
            args={'wait': 1}
        )

    def parse(self, response):
        # Your parsing logic here
        pass
```



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
