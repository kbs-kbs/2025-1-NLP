# splash API예제
- curl: http 요청을 보내는 프로그램/명령어
- 터미널에서 splash 서버의 api를 통해 렌더링된 페이지 반환

- `http://localhost:8050/render.html?url=https://example.com`과 같은 요청을 보내면, Splash는 example.com 페이지를 로드하고 JavaScript를 실행한 후의 최종 HTML을 반환합니다.

## 1. curl + splash로 동적 페이지 크롤링

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

- POST

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

-get 방식
```
http://localhost:8050/execute?lua_source=function main(splash) splash:go("https://example.com") return splash:html() end
```

## 2. requests 라이브러리 + splash 사용

curl 대신 requests를 사용

```
import requests
import json

url = 'http://localhost:8050/render.html'
headers = {
  'content-type': 'application/json'
}
payload = json.dumps({
  "url": "https://web-scraping.dev/products" # page URL to render
})


response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

"""
<!DOCTYPE html><html lang="en"><head>
    <meta charset="utf-8">
<title>web-scraping.dev product page 1</title>    
"""
```


## 3. scrapy + splash 사용

```
pip install scrapy scrapy_splash
```

```python title:dbpia.py
import scrapy
from scrapy_splash import SplashRequest

class DbpiaSpider(scrapy.Spider):
    name = 'dbpia'

    def start_requests(self):
        yield SplashRequest(
              url, # 위치 인자
              self.parse, # 위치 인자
              endpoint='execute', # 여기서부터 키워드 인자
              args={
                  'lua_source': lua_script,
                  'wait': 1.5
              }
        )



    def parse(self, response):
        # Your parsing logic here
        pass
```














---

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
