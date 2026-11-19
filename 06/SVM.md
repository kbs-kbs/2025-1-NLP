# 6주차 — 서포트 벡터 머신(SVM)

> MYBOX `SVM(1).pdf`(이론) · `SVM(2).pdf`(코드) 교안 + `006_SVM_P00i/P071.ipynb` 실습 정리

## 1. SVM이란

- 1990년대~2000년대 최고의 알고리즘으로 불렸고, 수학적 이론에 바탕을 둔 우수한 성능을 낸다. 다만 **대용량 데이터에는 부적합**하다.
- **결정 경계(decision boundary)** 를 설정해 이진 분류를 한다. 2차원에서는 **직선**, 3차원에서는 **평면**, 그 이상은 **초평면(hyperplane)** 이다.
- **서포트 벡터(support vector)**: 결정 경계와 가장 가까이 있는 데이터 포인트
- **마진(margin)**: 결정 경계와 서포트 벡터 사이의 거리

## 2. 최대 마진 — 왜 마진을 최대화하는가

- 경계는 여러 개 있을 수 있지만, **마진을 최대화하는 초평면**이 더 좋은 분류기다.
- 마진이 클수록 **일반화 오차(generalization error)가 낮아지는** 경향이 있다. 마진이 작으면 데이터의 작은 섭동에도 분류가 크게 흔들린다.

### 수식 정리

- 중심선에 직교하는 벡터 `w`, 샘플 `u`를 `w`에 투영해 경계를 넘으면 −, 아니면 +
  - `u · w + b > 0` 이면 +
- 제약식
  - `w · x+ + b > 1`, `w · x− + b < −1`
  - 두 식을 합치면 `yi(w · xi + b) > 1`
  - 등호가 성립하는 점이 경계에 걸친 점(`gutters`), 곧 서포트 벡터
- 마진의 폭: `WIDTH = (x+ − x−) · w / ||w|| = 2 / ||w||`
- 따라서 목적 함수는
  - **max 1/||w|| ↔ min ||w|| ↔ min ½||w||²**, 단 `yi(w·xi + b) ≥ 1`
  - w가 2차항만 가지므로 **convex**하고 제약식은 n개의 선형 함수이므로 **유일한 해**를 가진다.
- 라그랑지안으로 풀면 w를 샘플들의 선형 결합으로 나타낼 수 있고, 목적 함수에 데이터의 **내적(xi·xj)** 이 등장한다 → 커널 트릭의 근거.
- **KKT 조건**: `αi(yi(w·xi + b) − 1) = 0` 이므로 α가 0이면 서포트 벡터가 아니다. 경계선에 있는 점만 α가 살아남는다.
- 계산은 2차 계획법(Quadratic Programming)으로 최적해를 구할 수 있다.

## 3. 소프트 마진(Soft Margin)

- 실제 데이터는 선형 분리가 불가능한 경우가 많다.
- **min ½||w||² + C∑ξi**, 단 `yi(w·xi + b) > 1 − ξi`, `ξi > 0`
  - ξ(슬랙 변수) = 경계를 넘어간 데이터의 오차 추정치
- **C의 의미** (시험 포인트)

| C | 허용 | 마진 | 학습 데이터 분류 | 쓰는 곳 |
|---|---|---|---|---|
| 크다 (예: 100) | 오류를 허용하지 않음 | 작음 | 정확 | 노이즈가 적은 곳 |
| 작다 (예: 1) | 오류를 많이 허용 | 큼 | 부정확 | 노이즈가 많은 곳 |

- 라그랑지안 유도 후 `0 ≤ αi ≤ C` 라는 제약이 생긴다(α가 아무리 커도 C보다 작아야 한다).

## 4. 커널 SVM

- 복잡한 문제는 선형 분리가 불가능하다 → 입력 공간을 **고차원 특징 공간으로 매핑**한다.
  - 예: `Φ: (x1, x2) → (x1², x2², √2x1, √2x2, √2x1x2, 1)`
- 모든 관측을 고차원으로 매핑해 내적하면 연산이 폭발한다 → **커널 함수** `K(xi, xj) = Φ(xi)ᵀΦ(xj)` 로 내적만 계산한다.
- 커널이 **positive semi-definite** 이고 대칭 행렬이면 커널로 쓸 수 있다.
- 비교
  - Linear SVM: `f(x) = w · xi + b`
  - Kernel SVM: `f(x) = ∑ αi yi K(xi, xj) + b`
- **RBF(방사형 기저 함수, 가우시안 커널)**: `k(xi, xj) = exp(−||xi − xj||² / 2σ²)`
- 하이퍼파라미터 **Gamma와 C는 클수록 굴곡진(복잡한) 결정 경계**가 된다.

## 5. 사이킷런 실습

```python
from sklearn.svm import SVC
classifier = SVC(kernel='linear')    # 'linear' / 'poly' / 'rbf'
training_points = [[1,2], [1,5], [2,2], [7,5], [9,4], [8,2]]
labels = [1, 1, 1, 0, 0, 0]
classifier.fit(training_points, labels)
print(classifier.support_vectors_)   # [[7,5], [8,2], [2,2]]
print(classifier.predict([[3,2]]))
```

### C 값 비교 (선형 커널)

```python
clf_1   = svm.SVC(kernel='linear', C=1)      # 마진 큼, 오분류 허용 → 노이즈 많은 데이터
clf_100 = svm.SVC(kernel='linear', C=100)    # 마진 작음, 오분류 최소화 → 노이즈 적은 데이터
print("Accuracy(C=1): {}%".format(clf_1.score(X_test, y_test) * 100))
print("Accuracy(C=100): {}%".format(clf_100.score(X_test, y_test) * 100))
```

### 비선형 데이터 + RBF + 그리드 서치

```python
clf = svm.SVC(C=10.0, kernel='rbf', gamma=0.1)
clf.fit(X_train, y_train)

param_grid = {'C': [0.1, 1, 10, 100], 'gamma': [1, 0.1, 0.01, 0.001, 0.00001, 10]}
clf_grid = GridSearchCV(svm.SVC(), param_grid, verbose=1)
clf_grid.fit(X_train, y_train)
print(clf_grid.best_params_)
```

### 붓꽃(Iris) 분류 — 노트북 실습

```python
from sklearn import datasets, svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

iris = datasets.load_iris()
X = iris.data[:, :2]                                # 꽃잎 길이·폭만 사용 (2차원 시각화용)
X_train, X_test, y_train, y_test = train_test_split(X, iris.target, test_size=0.3, random_state=42)

model = svm.SVC(kernel='rbf', gamma='scale')        # 다중 분류
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy :", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

- `SVC(C=10)` 처럼 C만 지정하면 기본 커널은 `rbf`다.
- 결정 경계 시각화: 격자(meshgrid)를 만들어 각 점의 예측값을 그리고 등고선(`contourf`)으로 경계를 표시한다.

## 6. 함께 본 의사결정나무 (SVM(1) 교안 뒷부분)

| 항목 | 내용 |
|---|---|
| 원리 | 데이터를 "뿌리 → 잎"까지 순차 분류, 재귀 분할 |
| 용어 | 재귀 분할, 분할값, 마디(노드), 잎, 가지치기 |
| 알고리즘 | Hunt's algorithm, CART, ID3/C4.5, SLIQ/SPRINT |
| 불순도 | Gini Index(CART), Entropy·Information Gain(ID3/C4.5), Misclassification error |
| 과적합 방지 | Pre-Pruning(조기 중단), Post-Pruning(완성 후 가지치기) |
| 사이킷런 | `DecisionTreeClassifier(criterion='gini', max_depth=None, ...)` |

- 정보 획득(Information Gain) = 분할 전 엔트로피 − 분할 후 엔트로피. IG가 가장 큰 지점에서 분기한다.
- Gain Ratio는 작고 많은 분리를 하려는 IG의 단점을 제어한다(C4.5).
