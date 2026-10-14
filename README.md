# 가상 배아 챌린지(VEC) 한국어 점수 해설 도구와 입문 실습

> **비공식 커뮤니티 안내서입니다.** 대회 주최 측이 만들거나 검토한 자료가 아닙니다. 이 문서와 공식 사이트 내용이 다르면 **언제나 공식 사이트가 맞습니다.**
> 공식 사이트: https://virtualembryo.ai/challenge · 내용 확인 날짜: 2026년 10월 14일(한국 시간)

점수부터 이해하고 싶다면 **[한국어 점수 해설 도구](score-explainer.html)**를 내려받아 브라우저에서 여세요. 설치·로그인·데이터 없이 쓸 수 있습니다. 처음에는 생물 데이터와 무관한 가상 숫자로 연습합니다.

이 저장소에는 세 가지가 들어 있습니다.

1. **점수 해설 도구 `score-explainer.html`**: T1·T2·T3의 지표·바닥·천장을 입력하면 절댓값 처리, 지표별 환산, 가중치와 최종 기여분을 한국어로 보여 줍니다. 곡선과 짧은 문제로 수식을 익히고, 외부 자료 제한 구간의 경계도 확인합니다.
2. **이 입문서(README)**: 과제·자료·채점·에이전트 팀 규정을 공식 출처와 연결해 설명합니다.
3. **실습 노트북 `vec_ko_tutorial.ipynb`**: 공식 채점기 `veckit`을 설치하고, 회원 가입 없이 공개 견본으로 로컬 채점 흐름을 연습합니다. 저장된 출력은 없습니다.

### 설치 없이 먼저 해 보기

저장소의 **Code → Download ZIP**으로 소스를 받은 뒤 압축을 풀고 `score-explainer.html`을 더블클릭하세요. 또는 해당 파일 하나만 내려받아 열어도 됩니다. 파일 안에 화면과 계산 코드가 모두 들어 있어 인터넷을 끊어도 작동합니다. 출처 링크를 열 때만 인터넷이 필요합니다.

1. T1·T2·T3 중 하나를 고릅니다.
2. 가상 예제의 바닥과 천장을 비교하고, 한 지표의 측정값을 바꿔 봅니다.
3. 표·기여분 막대·곡선에서 왜 점수가 달라지는지 읽고, 짧은 문제를 풀어 봅니다.

지표를 직접 입력할 때는 **같은 평가 조건에서 구한 지표·바닥·천장**을 한 묶음으로 사용하세요. 공식 공개 기준값은 해당 validation 게시판의 원시 지표에 대응합니다. 로컬에서 다른 연습용 정답을 두고 구한 지표에 공개 기준값을 붙여도 공식 점수가 되지 않습니다. 도구는 입력한 숫자를 환산하며 채점기·제출 서버에 연결하지 않습니다. 숨김 게시판 점수나 실제 순위를 예측하지 않습니다. [공식 T1·T2·T3 채점](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1)

HTML 학습 도구의 계산·연습에는 설치나 인터넷이 필요하지 않고, 도구 코드가 입력값을 서버로 보내거나 영구 저장하지 않습니다. 아래 노트북은 패키지 설치·견본 다운로드·로컬 파일 저장이 필요한 별도 실습입니다.

---

## 1. 이 대회는 무엇인가요?

가상 배아 챌린지(Virtual Embryo Challenge, 줄여서 VEC)는 **NeurIPS 2026**(인공지능 분야의 큰 국제 학회)의 공식 경진대회입니다. 운영은 미국 스탠퍼드 대학교의 **Qiu Lab**과 협력자들이 맡고, 재정 지원은 Laude Institute Moonshots Seed Grant에서 합니다. [출처: 상금 페이지]

한 줄로 말하면, **생쥐 배아가 자라는 모습을 컴퓨터로 미리 예측하는 대회**입니다. 사용하는 자료는 생쥐 배아의 **약 100만 개 세포, 발생 시점 11곳(E6.75~E12.5)**입니다. "E9.5"는 수정 후 9.5일째 배아라는 뜻입니다. [출처: 데이터 페이지]

자료의 종류는 두 가지입니다. [출처: 데이터 페이지]
- **단일세포 RNA**: 세포를 하나하나 떼어 내어, 세포마다 유전자 32,285개가 얼마나 켜져 있는지 잰 자료입니다. 위치 정보는 없습니다. (과제 1)
- **3차원 MERFISH**: 배아를 얇게 연속으로 잘라 유전자 500개의 발현을 재고, 다시 3차원으로 쌓은 자료입니다. 세포마다 **발현 + 3차원 위치(x, y, z)**가 있습니다. (과제 2, 3) 좌표는 배아마다 따로 잡은 것이라 시점 사이에 맞춰져 있지 않습니다.

자료는 미국 UC San Diego의 **Qingquan Zhang 박사와 Neil Chi 박사 연구팀**이 만들었습니다. 대회 밖에서 자료를 사용·재사용·재배포할 때는 대회와 자료 생성팀의 출처를 밝혀야 합니다. 미출판 데이터를 논문이나 공개 발표에 쓰려면 자료 생성팀의 사전 서면 승인이 필요합니다. [출처: [약관 14항](https://virtualembryo.ai/challenge/terms), [출판 안내](https://virtualembryo.ai/challenge/publish)]

## 2. 세 가지 과제(T1·T2·T3)를 쉬운 말로

| 과제 | 쉬운 설명 | 학습용으로 주는 것 | 리더보드(점수판) 확인용 | 최종 순위용(숨김) |
|---|---|---|---|---|
| **T1 시간 예측** | 앞 시점의 세포들을 보고, **앞으로의 시점에 어떤 세포들이 어떤 비율로 있을지** 세포 집단을 통째로 예측 | E8.5, E9.5 (단일세포 RNA) | E10.5 | E12.5 |
| **T2 공간·시간 예측** | 유전자 발현과 **3차원 위치를 함께** 예측. 분자·세포·조직 세 수준을 한꺼번에 봅니다. 심장과 배아 전체를 따로 채점 | 심장: E8.25, E8.75, E9.5 / 배아: E6.75, E7.25, E8.0 | 심장: E8.5(사이 채우기), E10.5(앞으로 늘리기) / 배아: E7.5 | 심장: E12.5 / 배아: E7.75 |
| **T3 유전자 제거 예측** | 정상 배아(야생형)와 이미 본 돌연변이 하나를 참고해, **아직 못 본 유전자 제거(녹아웃) 배아**의 발현과 위치를 예측 | Mab21l2 녹아웃(E9.5) + 짝이 되는 야생형 | Gata4 녹아웃(E8.75) | β-catenin 녹아웃(E8.75) |

[출처: 과제 페이지, 데이터 페이지]

어려운 점(공식 설명 요약):
- **T1**: E10.5와 E12.5 사이에는 관찰된 시점이 없어 '사이 채우기'를 할 수 없습니다. 또 E8.5와 E9.5는 공통 세포 유형이 5개뿐이라, 나중 시점 세포의 약 3분의 2는 전에 없던 유형입니다. 즉 "세포가 얼마나 움직이나"가 아니라 "어떤 세포가 새로 생기나"를 맞혀야 합니다. [출처: 과제 페이지]
- **T2**: 발현 변화·세포 상태 분포·조직 모양과 크기·국소 공간 배치의 네 질문이 각각 점수의 25%입니다. [출처: 과제 페이지]
- **T3**: 돌연변이 배아도 겉보기에는 야생형과 거의 같아서, 야생형을 그대로 내도 전체 발현의 상관이 0.956이나 됩니다. 그래서 점수는 **야생형 → 돌연변이의 '차이'**에 매깁니다. [출처: 과제 페이지, 기준선 페이지]

## 3. 자료는 어떻게 받나요?

- 학습용 자료는 **등록한 참가자에게만** 공개됩니다. 공식 사이트에 로그인한 뒤 데이터 페이지에서 받습니다. [출처: 데이터 페이지]
- 확인용·시험용 정답은 공개하지 않고, 제출하면 **점수만** 돌려줍니다. 최종 단계가 시작되면 확인용 정답은 모든 과제에서 공개되고, 시험용 정답은 끝까지 공개되지 않습니다. [출처: 과제 페이지, 데이터 페이지]
- 로그인 없이 먼저 구경하고 싶다면 사이트의 배아 도감(atlas)에서 세포를 3차원으로 볼 수 있습니다. [출처: 데이터 페이지]
- 파일 크기 예: T1 E8.5 파일 571 MB, E9.5 파일 590 MB. [출처: 데이터 페이지]
- **외부 자료와 사전학습 모델**: 라이선스가 허용하는 외부 공개 자료·사전학습 모델·공개 코드를 사용할 수 있습니다. 제출할 때 모든 외부 출처를 밝히고, 방법 요약에서 활용 방식을 설명해야 합니다. 재현에 필요한 출처·버전·라이선스도 기록해 두세요. 숨겨진 시점·유전형의 측정값은 직접 사용하거나 사전학습 모델을 통해 간접 사용해서도 안 됩니다. 외삽 과제에서는 **E9.5 초과~E13.5 이하**의 외부 측정 자료가 제한됩니다(E9.5는 허용, E13.5는 금지). T2 보간 과제에서는 심장 **E8.25 초과~E8.75 미만**, 배아 **E7.25 초과~E8.0 미만**이 제한되며 양 끝 시점은 허용됩니다. 같은 유전자의 다른 대립유전자나 비슷한 표현형을 만드는 변형도 규정의 제한을 피해 가는 근거가 되지 않습니다. 자료를 선택하기 전에 과제별 세부 조건을 확인하세요. [출처: [규정 10항](https://virtualembryo.ai/challenge/rules)]

> 이 노트북은 전체 대회 데이터 대신, 공식 `veckit` 저장소가 안내하는 150개 세포짜리 견본을 실행할 때 내려받습니다. 이 저장소에는 **데이터 파일·저장된 실행 출력·견본에서 계산한 결과값을 넣지 않았습니다.** 채점기의 MIT 라이선스가 데이터나 실행 결과의 공개 허가까지 뜻하지는 않습니다. 데이터를 사용하거나 결과를 공유하기 전에 [데이터 이용약관 14항](https://virtualembryo.ai/challenge/terms)과 [출판 안내](https://virtualembryo.ai/challenge/publish)를 확인하세요. [견본 설명: 공식 veckit README](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/README.md)

## 4. 점수는 어떻게 매기나요?

### 4-1. 바닥 50점, 천장 100점
- **바닥(floor)** = '아무것도 안 바꾼 예측'의 점수. T1·T2는 `copy_last`(마지막으로 관찰한 단계를 그대로 냄), T3는 `wt_identity`(짝이 되는 야생형을 그대로 냄 = "돌연변이가 아무 영향이 없었다"). 바닥은 정의상 **50점**입니다. 50점보다 낮으면 '아무것도 안 한 것보다 못하다'는 뜻입니다. [출처: 기준선 페이지, 리더보드 페이지]
- **천장(ceiling)** = 실제 정답을 둘로 나눠 한쪽을 다른 쪽에 대고 채점한 값. '완벽한 모델'이 아니라 '자료 자체가 허락하는 최대치'의 추정입니다. 이보다 좋으면 **100점에서 자릅니다.** [출처: 기준선 페이지, 리더보드 페이지]
- 환산은 직선이 아니라 **쌍곡선 꼴**입니다. 지표와 바닥·천장을 확인한 뒤, 지표가 결측·NaN이면 skill 0으로 처리합니다. 유효한 값이 천장과 같거나 더 좋으면 나눗셈 전에 skill 1로 정하고, 그 밖의 경우에만 `d_floor / (d_floor + d)`를 계산합니다(d는 천장까지의 거리, d_floor는 바닥과 천장 사이 거리). 지표별 skill을 가중 평균한 뒤 100을 곱합니다. 높을수록 좋은 지표와 낮을수록 좋은 지표는 거리 방향이 반대입니다. **`scale_log_ratio`와 `severity_slope`는 측정값·바닥값·천장값 모두 절댓값으로 바꾼 뒤, 작을수록 좋은 지표로 환산**합니다. 노트북의 환산 함수는 T1 전용이며, 동일·역전·비유한 기준값에서는 합산을 멈춥니다. 이 중단 방식은 교육용 코드의 입력 정책으로, 공식 서버의 모든 오류 처리를 확인했다는 뜻은 아닙니다. [출처: 평가 페이지(채점 탭), 리더보드 페이지]
- 게시판별 바닥·천장 값(원래 단위)은 평가 페이지와 `index.json`에 공개되어 있어, 원래 지표 값에 지표별 방향·절댓값 예외·가중치와 게시판별 바닥·천장값을 적용하면 공개 게시판의 환산 점수를 계산할 수 있습니다. 숨겨진 시험용 게시판 값은 공개하지 않습니다. [출처: 평가 페이지(채점 탭), panels/index.json]

### 4-2. 과제별 지표와 비중 [출처: 과제 페이지, 평가 페이지(채점 탭)]

| 과제 | 질문(비중) | veckit 출력 이름 |
|---|---|---|
| T1 | 크게 변한 유전자 맞히기 DES 25% · 변화 방향 DCS 25% · 세포 상태 분포 MMD 30% · 유전자끼리 함께 움직이는 구조 CSS 20% | `de_score`, `de_direction`, `mmd_u`, `variogram` |
| T2 | 발현 변화 25%(DES 0.5, DCS 0.5) · 세포 상태 분포 25%(MMD 0.6, CSS 0.4) · 조직 모양과 크기 25%(SDD·ODS·TSR 각 1/3) · 국소 공간 배치 25%(NFS) | `de_score`, `de_direction`, `mmd_u`, `variogram`, `d2_shape`, `occupancy_dice`, `scale_log_ratio`, `neighborhood_mmd` |
| T3 | 반응 유전자 맞히기 DES 30% · 반응 방향 DCS 25% · 반응 크기 PSS 25% · 세포 상태 분포 20%(MMD 0.6, CSS 0.4) | `de_score`, `de_direction`, `severity_slope`, `mmd_u`, `variogram` |

(T2 이름 짝: 평가 페이지 T2 채점 탭에 SDD = `shape_metrics.py::d2_distance`(veckit 출력 이름 `d2_shape`), ODS = `occupancy_dice`, TSR = `scale_log_ratio`, NFS = `neighborhood_mmd`로 나옵니다. T3의 PSS = `severity_slope`.)

T3의 `severity_slope`는 회귀 기울기 β 자체가 아니라, 조건을 충족한 기울기의 **부호 있는 로그값**입니다. 해설 도구에는 채점기가 반환한 지표값을 넣으세요. 다시 로그를 취하거나 β를 대신 넣지 않습니다. [출처: [T3 PSS](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=3)]

### 4-3. 꼭 알아 둘 규칙 [출처: 평가 페이지(제출 탭), 데이터 페이지, FAQ]
- 제출물은 **예측한 세포 집단**입니다. T1은 발현만, T2·T3는 발현 + `obsm["spatial_3D"]`(3차원 좌표). **세포 유형 이름표는 내지 않습니다**(주최 측이 고정된 분류기로 직접 붙입니다).
- 세포 수는 게시판별 최소~최대 범위 안에서 정합니다. 수 자체에 별도 가산점은 없지만, 표본 구성과 지표의 내부 표본추출에 따라 계산값은 달라질 수 있습니다. 더 많은 세포가 점수 향상을 보장하지는 않습니다.
- 유전자 이름(`var_names`)은 게시판 유전자 목록과 **같은 유전자, 같은 순서**여야 합니다. 목록은 데이터 페이지의 게시판별 `*.genes.txt`에서 가져오세요(예: T1:val 32,285개, T2 배아 498개, T2 심장 500개, T3:gata4 500개).
- `.X`는 **로그 정규화된 값**이어야 합니다. 원래 개수(raw counts)를 내면 형식 검사는 통과하지만 **점수가 조용히 틀리게** 나옵니다.

### 4-4. 해설 도구에서 확인할 함정

- **부호 지표**: `scale_log_ratio`와 `severity_slope`는 측정값만이 아니라 바닥·천장도 절댓값으로 바꿉니다. 변환 전후 값을 표에서 확인하세요.
- **입력 대기와 결측 지표**: 수동 입력의 빈칸은 아직 입력하지 않은 상태입니다. 실제 지표 결측은 NaN으로 명시하며 skill 0으로 처리합니다. 그 지표의 비중을 다른 지표에 나눠 주지 않습니다.
- **잘못된 바닥·천장**: 두 값이 같거나 좋은 방향과 반대로 놓이면 환산을 멈춥니다. 부호가 달라도 절댓값을 취한 뒤 같아질 수 있습니다.
- **천장보다 좋은 값**: skill 1로 처리합니다. 이 범위에서 수식을 그대로 나눠 잘못된 음수나 무한대가 생기지 않도록 합니다.
- **ODS 해석**: `_dice_voxel_over_nn` 선택 입력은 공식 해석 조건을 읽도록 돕습니다. 숫자가 약 10을 넘었다는 이유만으로 유효성을 통과 처리하지 않습니다.
- **자료 시점 경계**: E시점 학습 화면은 선택한 과제의 제한 구간만 설명합니다. 구간 밖이라는 결과가 자료 사용 허가를 뜻하지 않습니다. 발달 단계 매핑, 유전형·대립유전자·유사 표현형, 자료·모델 출처와 라이선스도 [규정 10항](https://virtualembryo.ai/challenge/rules)에 따라 확인해야 합니다.

도구의 가상 숫자와 문제는 수식을 배우기 위한 것입니다. 실제 배아·견본·공식 게시판의 측정값은 포함하지 않습니다. 환산식과 ODS 조건의 출처는 [T1](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1), [T2](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2), [T3](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=3) 채점 안내입니다.

계산 코드를 직접 확인하려면 HTML의 합성 검증 화면을 보세요. Node가 설치되어 있다면 저장소 폴더에서 다음 명령으로 같은 계산 코어를 별도로 검사할 수도 있습니다. 검증은 가상 숫자만 사용하며 생물 데이터와 공식 채점기를 실행하지 않습니다.

```bash
node verify-score-core.cjs
```

설명·구현·합성 시험의 연결은 [SOURCE_MAP.md](SOURCE_MAP.md)에 정리했습니다. 이 시험의 통과는 실제 이용자의 학습 효과나 생물학적 예측 성능을 뜻하지 않습니다.

## 5. 두 갈래 참가 방식: 사람 팀 vs 에이전트 팀

| | 사람 팀(Human Team) | 에이전트 팀(Agent Team) |
|---|---|---|
| 방식 | 사람이 방법을 설계·학습·선택하는 일반적인 방식 | 코딩 에이전트나 거대언어모델(LLM) 기반 자동 시스템이 방법을 만듦. 사람은 **실행 설정을 고정하기 전** 프롬프트·도구·모델을 시험하고 수정할 수 있음. 고정 후에는 중간 결과를 보고 개입하거나 설정·예측 파일을 수정하면 안 됨 |
| 증거 제출 | 요구하지 않음 | **실행 기록(trajectory), 첫 지시문을 포함한 모든 지시문(prompts), 실행 틀 코드(harness)** |

- 두 갈래는 같은 과제·같은 지표·같은 숨김 시험으로 채점하지만, **상금은 갈래별로 따로** 줍니다. [출처: 과제 페이지, 상금 페이지]
- 에이전트 팀 제출물은 **실행 기록이 반드시 포함된, 서로 다른 증거 최소 두 종류**가 붙을 때까지 채점 대기열에 들어가지 않습니다. 수상 심사에는 실행 기록·모든 지시문·실행 코드가 필요합니다. 사람이 고정된 실행의 중간 산출물을 골라서는 안 되지만, 여러 완료된 실행 중 제출할 실행은 고를 수 있습니다. [출처: [규칙 9항·14항](https://virtualembryo.ai/challenge/rules)] ※ FAQ에는 "최소 하나"라고 적혀 있어 공식 페이지끼리 표현이 다릅니다. 페이지 사이에 어느 문구가 우선하는지 정한 조항은 확인하지 못했습니다. 이 안내서는 규칙 9항의 더 엄격한 기준인 두 종류 이상으로 안내합니다.
- 제출할 때 사용한 에이전트 프레임워크와 실제 모델 식별 문자열도 각각 밝혀야 합니다. [출처: [규정 9항](https://virtualembryo.ai/challenge/rules)]
- 한 사람은 계정 하나, 팀 하나만 가질 수 있고, 팀은 한 갈래만 고릅니다. [출처: 규칙 페이지, FAQ]

## 6. 일정과 상금 (공식 페이지 기준)

### 일정 [출처: 일정 페이지]
| 날짜(2026년) | 내용 |
|---|---|
| 7월 28일 | NeurIPS 2026 경진대회 목록 발표 |
| 8월 10일 | P1: 사이트·제출 창구 열림, 확인용 리더보드 시작 |
| 8월 15일 | P2: 시작 도구 모음(starter kit)과 기준 모델 공개 |
| **10월 20일** | **P3: 시험 단계 시작, 확인용 정답 공개, 시험 리더보드 열림** (게시판마다 공식 제출 2번까지, 단계 전체 기준) |
| **12월 2일** | **최종 제출 마감** |
| 12월 4일 | 최종 평가 시작(에이전트 팀은 증거 확인) |
| 12월 11일 | NeurIPS에서 수상자 발표 |

> 로그인과 팀 등록은 [공식 계정 페이지](https://virtualembryo.ai/challenge/account)에서 진행합니다. 커뮤니티 기여상은 계정이 필요하지만 팀 등록은 필요하지 않습니다. [출처: [커뮤니티 기여상](https://virtualembryo.ai/challenge/community)]

하루 채점 제출 한도(팀·과제·UTC 하루 기준): P1 20번, P2 8번, P3는 게시판당 단계 전체 2번. [출처: 규칙 페이지]

### 상금: 총 11만 2천 달러 [출처: 상금 페이지]
- **순위 상금 5만 4천 달러** — 갈래마다 2만 7천 달러: 1등 8천 달러 × 1, 2등 5천 달러 × 2, 3등 3천 달러 × 3.
- **범용성 상(Generality Award) 8천 달러** — 하나의 공통 구조로 과제 두 개 이상을 푼 가장 좋은 출품작 하나(두 갈래 통틀어 한 번).
- **여행 지원 3만 달러** — 초기 경력 연구자 15~20명에게 NeurIPS 워크숍 참가 지원.
- **커뮤니티 기여상 2만 달러** — 다른 참가자를 돕는 자습서·노트북·도구·문서·수정에 **기여 하나당 최대 200달러**. 순위와 상관없고, 대회에 참가하지 않아도 신청할 수 있습니다. 자동 지급은 아니며 주최 측이 기여를 심사합니다. 공개 링크를 커뮤니티 페이지에서 계정으로 신청하고, 심사는 12월 11일 또는 예산 소진 중 먼저 오는 시점까지 진행합니다. 인정된 기여의 상금은 대회가 끝난 뒤 지급합니다. 번역과 다른 나라 말 자료도 포함됩니다. [출처: 상금 페이지, 커뮤니티 기여상 페이지]

## 7. 따라 하기: veckit으로 내 컴퓨터에서 채점하기

`veckit`은 주최 측이 공개한 **로컬 채점기**입니다(MIT 라이선스, PyPI 패키지). 여러분이 준 파일끼리만 비교하며, 숨겨진 정답에는 접근하지 않습니다. 따라서 **로컬 점수는 실제 대회 점수의 예고가 아닙니다.** 파일 형식이 맞는지, 채점 흐름이 도는지 확인하는 용도입니다. [출처: veckit README]

```bash
python -m venv .venv
source .venv/bin/activate
pip install "veckit==0.1.2"
mkdir -p sample_data
# 견본 받기(150개 세포짜리)
curl -L -o sample_data/sample_8.5.h5ad https://raw.githubusercontent.com/aristoteleo/veckit/cc3859ab2a2305efc4544815d3f44f660efa77d4/data/sample_8.5.h5ad
curl -L -o sample_data/sample_9.5.h5ad https://raw.githubusercontent.com/aristoteleo/veckit/cc3859ab2a2305efc4544815d3f44f660efa77d4/data/sample_9.5.h5ad
# copy_last 채점: E8.5를 그대로 E9.5에 대한 예측으로 냄
veckit --task T1 --input sample_data/sample_8.5.h5ad --target sample_data/sample_9.5.h5ad
```

Windows PowerShell에서 실습 노트북을 열려면, 저장소 폴더에서 다음 명령을 실행하세요. Python 실행기 `py`가 설치되어 있어야 합니다. 별도의 활성화 명령 없이 가상환경의 Python을 직접 사용합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install "veckit==0.1.2" jupyterlab
.\.venv\Scripts\python.exe -m jupyterlab
```

브라우저의 파일 목록에서 `vec_ko_tutorial.ipynb`를 열고 위에서부터 실행하세요. 패키지 설치와 견본 다운로드에는 인터넷 연결이 필요합니다.

세 파일의 역할: `--input`(내 예측), `--target`(연습용 정답), `--reference`(T1·T2: 변화를 잴 앞 단계) / `--wt`(T3: 짝이 되는 야생형). `--reference`를 빼면 `--input`과 같다고 봐서 변화 지표(`de_score`, `de_direction`)가 0이 됩니다. 아무것도 안 바꾼 예측을 시험할 때만 맞는 설정이고, 진짜 모델을 채점할 때는 반드시 앞 단계를 넣으세요. [출처: veckit README]

노트북은 위 과정을 T1·T2·T3 모두에 대해 자동으로 해 줍니다. Jupyter에서 `vec_ko_tutorial.ipynb`를 열고 위에서부터 차례로 실행하면 됩니다(직접 손댈 단계 없음).

### 실습에서 확인할 것

노트북은 T1의 원시 지표와 연습용 점수 환산, T2의 전처리·좌표 변환, T3의 단순 기준 예측, 유전자 순서 오류를 차례로 다룹니다. 실행하면 자신의 환경 버전과 결과가 화면에 나오고, `sample_data/`와 `results/`에 파일이 생깁니다. 이 파일들은 로컬 실습용이며 저장소의 `.gitignore`에서 제외합니다.

견본은 채점 흐름을 익히는 용도입니다. 여기서 계산한 연습용 바닥·천장은 공식 게시판의 기준값이 아니며, 실제 순위나 생물학적 예측 성능을 뜻하지 않습니다. `mmd_u`는 불편향 추정치라 작은 견본에서 음수가 나올 수 있습니다. [출처: [공식 veckit README](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/README.md), [공식 MMD 구현](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/common/core_metrics.py)]

노트북에 출력이 저장된 상태로 파일을 다시 공유하지 마세요. 실행 결과와 데이터를 공개하려면 관련 이용 조건을 따로 확인해야 합니다.

## 8. 흔히 걸리는 함정

1. **회전 오류와 거울상 맹점을 구분하세요.** 공식 FAQ와 평가 페이지는 형태 지표의 좌우성(laterality) 맹점을 설명합니다. 한편 veckit 이슈 #7은 회전만 해도 원시 지표가 달라지는 구현 오류이며, PR #9에서 수정됐습니다. 이 수정은 고정한 GitHub 커밋 `cc3859ab`에 포함되지만 PyPI 0.1.2에는 포함되지 않았습니다. [출처: [FAQ](https://virtualembryo.ai/challenge/faq), [이슈 #7](https://github.com/aristoteleo/veckit/issues/7), [PR #9](https://github.com/aristoteleo/veckit/pull/9)]
   - 노트북은 좌표를 회전하거나 z축 부호를 뒤집어 채점기의 반응을 비교하도록 구성했습니다. z축 반사는 공간의 방향성을 뒤집습니다(변환 행렬의 행렬식 −1). 기하학적 거울상 시험에는 z축이 해부학적 좌우축인지 알 필요가 없습니다. 다만 회전 불변성이 깨진 버전의 결과를 다른 축이나 방향에 그대로 적용할 수는 없습니다.
   - **Dice에는 해석 조건이 있습니다.** 격자 한 변 길이를 실제 세포의 최근접 이웃 거리 중앙값으로 나눈 비율이 약 10보다 충분히 클 때만 조직 Dice를 해석하라고 공식 안내가 설명합니다. 자신의 실행 결과에서 `_dice_voxel_over_nn`을 확인하세요. `sliced_wasserstein`은 순위에 쓰지 않는 진단값이며, 공식 구현도 거울상 반응을 보정된 좌우 검사가 아닌 좌표계 점검으로 설명합니다. [출처: [공식 T2 ODS 설명](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2), [공식 형태 지표 구현](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/common/shape_metrics.py)]
   - 이 실습으로 실제 배아의 좌우 패턴 예측 성능이나 모든 형태에 대한 거울상 구분 성능을 검증할 수는 없습니다. 모델의 해부학적 좌우 일관성은 별도로 확인해야 합니다.
2. **T1은 유전자 32,285개입니다. 500개가 아닙니다.** 공식 제출 안내: "T1에서 500개 MERFISH 패널을 가정하는 것이 가장 흔한 형식 오류." veckit 이슈 #3에서도 같은 혼동이 있었고, 저장소 관리자는 옛 설명 문구가 남아 있었고 채점기는 맞다고 답했습니다. [출처: 평가 페이지(제출 탭), veckit 이슈 #3]
3. **유전자 순서.** 같은 유전자라도 순서가 다르면 거부됩니다. 노트북 7장은 순서를 섞은 파일의 거부 여부와 `allow_reorder=True`를 사용한 재정렬을 비교하도록 구성했습니다. [출처: 데이터 페이지]
4. **평균 세포 하나만 반복하지 마세요.** 평균만 비교하는 지표에서는 그럴듯해도 분포 지표에서는 거의 0점이고, 그 두 지표가 T1의 절반입니다. [출처: 평가 페이지(제출 탭), 기준선 페이지]
5. **세포 수 자체에 별도 가산점은 없습니다.** 무거운 지표는 자체 표본추출을 합니다(MMD 2,000개, energy distance·variogram 각각 1,500개). 세포 구성과 표본추출에 따라 계산값은 달라질 수 있으므로 더 많은 세포가 점수 향상을 보장하지는 않습니다. [출처: [데이터 페이지](https://virtualembryo.ai/challenge/data)]
6. **T2 배아 게시판은 유전자 498개.** Casp4, Pnliprp1이 E6.75·E7.25에서 측정되지 않아 빠졌습니다. [출처: 데이터 페이지]
7. **세포 유형 이름은 시점마다 통일되어 있지 않습니다.** 예: E9.5의 Endocardium이 나중에는 Endocardium-1, -2. [출처: 데이터 페이지]

## 9. 출처 (모두 2026-10-14 확인)

- 과제: https://virtualembryo.ai/challenge/tasks
- 데이터: https://virtualembryo.ai/challenge/data
- 평가(채점 탭): https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1 (task=2, task=3)
- 평가(제출 탭): https://virtualembryo.ai/challenge/evaluation?section=submissions&task=1
- 게시판 색인: https://virtualembryo.ai/challenge/panels/index.json
- 기준선(Reference rows): https://virtualembryo.ai/challenge/baselines
- 리더보드: https://virtualembryo.ai/challenge/leaderboard
- 일정: https://virtualembryo.ai/challenge/timeline
- 상금: https://virtualembryo.ai/challenge/prizes
- 커뮤니티 기여상: https://virtualembryo.ai/challenge/community (메뉴 이름 "Community award")
- 규칙: https://virtualembryo.ai/challenge/rules
- FAQ: https://virtualembryo.ai/challenge/faq
- 데이터 이용약관: https://virtualembryo.ai/challenge/terms
- 출판 안내: https://virtualembryo.ai/challenge/publish
- 커뮤니티 자료 목록: https://virtualembryo.ai/challenge/resources
- 계정 페이지: https://virtualembryo.ai/challenge/account
- veckit: https://github.com/aristoteleo/veckit · https://pypi.org/project/veckit/ · 이슈 #3, #7: https://github.com/aristoteleo/veckit/issues

주요 사실과 직접 출처 링크는 `SOURCE_MAP.md`에 묶었습니다.

## 10. 감사와 라이선스

- 채점기 `veckit`: **aristoteleo/veckit, MIT 라이선스.** 원저작권·허가문은 `NOTICE`에 보존했습니다. 견본은 같은 저장소에서 공개되지만 데이터별 라이선스와 실행 결과의 공개 허가 범위는 별도 확인이 필요합니다.
- 대회 운영: 스탠퍼드 대학교 **Qiu Lab**과 협력자들. 자료 생성: UC San Diego **Qingquan Zhang 박사, Neil Chi 박사** 연구팀.
- **글(CC BY 4.0)**: README·SOURCE_MAP의 원본 글, 노트북 Markdown 셀, `build_notebook.py`에서 `md()`에 넣은 원본 문자열입니다. **MIT**: `score-explainer.html` 전체(HTML·CSS·JavaScript·직접 작성한 화면 문구), `verify-score-core.cjs`, 생성기의 나머지 코드, 노트북 코드 셀 전체입니다. 코드 주석과 출력 문구도 포함합니다. 제3자 인용·요약, 견본 데이터와 견본 기반 출력은 이 표기로 다시 허가되지 않습니다. 자세한 범위는 `LICENSE`를 보세요.
- 작성: **Byungwoong Yoo (Independent Researcher, BigWonder)** · [ORCID](https://orcid.org/0009-0002-1797-3100). 대회 주최 측의 보증이나 검토를 받지 않은 비공식 커뮤니티 자료입니다.
- 이 공개본에는 데이터와 실행 출력을 담지 않았습니다. 사용자가 실행 후 만든 파일과 출력의 이용·공개 조건은 별도로 확인해야 합니다.

### 함께 볼 기존 커뮤니티 자료

공식 [커뮤니티 목록](https://virtualembryo.ai/challenge/resources)에 한국어 입문서와 점수 계산·진단 도구가 이미 있습니다. 이 저장소는 새로운 채점법을 제안하지 않습니다. 설치 없이 한국어로 지표 변환과 규정의 경계를 배우는 화면을 보완합니다.

- [VEC Multilingual Starter 한국어 안내](https://github.com/random-guy-05/vec-multilingual-starter/blob/main/docs/tutorial_ko.md): 명령 실행 중심의 시작 안내.
- [Local Scoring Wrapper](https://github.com/xxx12e/vec-community-kit/tree/main/vec_local_score): 로컬 점수 환산과 여러 실행의 비교.
- [Intuition Lab](https://github.com/i-habib/virtual-embryo-community/tree/main/intuition-lab): 지표의 실패 사례를 살펴보는 실습.
- [Data Safety Kit](https://github.com/i-habib/virtual-embryo-community/tree/main/data-safety): 외부 자료 제한과 출처 공개를 돕는 도구.
