
모두의 자연어처리
107페이지 표 4-4 "TF-IDF를 곱한값": - 대부분의 ~

사이킷런의 TfidVectoizer를 통해 변환 가능
이미 있는 다른 함수 2개를 합친 것

fit(), transformO fitJransformO

시험문제
빈도수 합계:
df_dtm.sum().to_frame().T


ngram 시험문제 x

---

## 보강 — TF-IDF 계산과 코드 (교재 10장 1절)

### 정의

| 기호 | 뜻 |
|---|---|
| `tf(t,d)` | 문서 d에서 단어 t가 나온 **횟수** |
| `df(t)` | 단어 t가 나타난 **문서 수** |
| `idf(t)` | `log(N / (1 + df(t)))` — N은 전체 문서 수, 분모의 1은 **스무딩**(0으로 나누는 것 방지) |
| `tf-idf` | `tf(t,d) × idf(t)` |

- 문서 안에서 자주 나오고, 전체 문서에서는 드물게 나오는 단어일수록 값이 커진다.
- a, the처럼 모든 문서에 나오는 단어는 idf가 작아져 자연스럽게 걸러진다.

### 코드

```python
from sklearn.feature_extraction.text import TfidfVectorizer

corpus = ['먼저 텍스트의 각 단어를 나누어 토큰화합니다.',
          '텍스트의 단어로 토큰화해야 딥러닝에서 인식됩니다.',
          '토큰화한 결과는 딥러닝에서 사용할 수 있습니다.']

vect = TfidfVectorizer()
tfidf_matrix = vect.fit_transform(corpus)          # 문서 × 단어 행렬
print(vect.get_feature_names_out())                # 단어 사전
print(tfidf_matrix.toarray())
```

- `fit()` = 단어 사전과 idf 계산, `transform()` = 문서를 벡터로 변환, `fit_transform()` = 둘을 한 번에
- `CountVectorizer`와의 차이: Count는 **빈도**만, Tfidf는 빈도에 **희소성 가중치**를 곱한다.
- `TfidfVectorizer`는 CountVectorizer와 TfidfTransformer를 **합쳐 놓은 클래스**다(교안: "이미 있는 다른 함수 2개를 합친 것").

### 시험 포인트

- 빈도수 합계: `dtm.sum().to_frame().T` (DataFrame을 전치해 한 줄로 보기)
- n-gram은 시험 범위에서 제외
- TF-IDF는 **키워드 검색 엔진, 중요 키워드 분석, 검색 결과 순위**에 쓰인다
- 107페이지 표 4-4 "TF-IDF를 곱한 값"의 경향: 대부분의 문서에 등장하는 단어는 값이 작아지고, 특정 문서에만 등장하는 단어가 커진다
