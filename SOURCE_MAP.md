# 주요 사실과 공식 출처

내용 확인 날짜: 2026-10-14. 사이트의 일정·규정이 바뀌면 최신 공식 내용을 확인하세요.

| 내용 | 직접 출처 |
|---|---|
| 과제 T1·T2·T3와 예측 대상 | [과제](https://virtualembryo.ai/challenge/tasks) |
| 발생 시점, 유전자 목록, 데이터 접근과 형식 | [데이터](https://virtualembryo.ai/challenge/data), [제출 형식](https://virtualembryo.ai/challenge/evaluation?section=submissions&task=1) |
| 바닥·천장, 환산식, 지표 방향·비중 | [T1 채점](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1), [T2 채점](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2), [T3 채점](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=3), [기준선](https://virtualembryo.ai/challenge/baselines) |
| 에이전트 설정 고정·증빙, 외부 자료 제한, 제출 한도 | [규칙 9·10·11·14항](https://virtualembryo.ai/challenge/rules), [FAQ](https://virtualembryo.ai/challenge/faq) |
| 대회 일정과 상금 | [일정](https://virtualembryo.ai/challenge/timeline), [상금](https://virtualembryo.ai/challenge/prizes) |
| 커뮤니티 기여상 대상·공개 링크·계정 요건 | [커뮤니티 기여상](https://virtualembryo.ai/challenge/community) |
| 데이터의 연구·교육용 이용과 출처·발표 조건 | [이용약관 14항](https://virtualembryo.ai/challenge/terms), [출판 안내](https://virtualembryo.ai/challenge/publish) |
| 로컬 채점기의 역할, 견본 150개 세포, reference 생략의 의미 | [고정 커밋의 veckit README](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/README.md) |
| 회전 오류와 수정 | [이슈 #7](https://github.com/aristoteleo/veckit/issues/7), [PR #9](https://github.com/aristoteleo/veckit/pull/9) |
| Dice 해석 조건과 좌표계 점검 한계 | [T2 ODS](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2), [형태 지표 구현](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/common/shape_metrics.py) |

`score-explainer.html`은 위 공식 환산식·가중치·절댓값 예외와 규정 10항의 시점 구간을 한국어로 설명합니다. 파일에 들어 있는 가상 숫자는 수식 학습용이며 생물 데이터·견본 결과·공식 게시판 값이 아닙니다. 새 채점 방법이나 공식 판정 도구를 뜻하지 않습니다.

| 도구의 설명·동작 | 근거와 적용 범위 | 구현·합성 검증 |
|---|---|---|
| `scale_log_ratio`·`severity_slope`의 측정값·바닥·천장 모두 절댓값 처리 | [T2](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2)·[T3](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=3) 공식 환산 규칙 | `evaluateMetric`; 음수·양수 측정값과 부호가 다른 기준값 |
| 결측 지표 skill 0, 가중치 유지 | [공식 환산 규칙](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1) | `evaluateTask`; 지표 하나만 결측인 각 과제 |
| 수동 입력의 빈칸에서는 계산 대기; 잘못된 기준값에서는 총점 중단 | 이 도구의 입력 정책. 공식 서버의 모든 예외 처리를 재현했다는 뜻이 아님 | `parseScalar`·`evaluateMetric`; 미입력·동일·역전·비유한 값 |
| 천장 이상은 skill 1; T2 조직 모양 그룹은 세 지표 각 1/3 | [공식 환산 규칙과 T2 비중](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2) | `evaluateMetric`·`evaluateTask`; 천장 초과·모든 지표가 천장인 경우 |
| ODS 비율 10.1을 자동 통과로 표시하지 않음 | [T2 ODS의 정성적 해석 조건](https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2). 이 경고로 가중치를 바꾸지 않음 | ODS 설명과 학습 문제 |
| 구간 밖을 자료 사용 허가로 표시하지 않음 | [규정 10항](https://virtualembryo.ai/challenge/rules)의 제한 구간만 설명 | `evaluateBoundary`; 열린 끝·닫힌 끝과 모호한 시점 입력 |

계산 함수는 HTML의 `score-core` 스크립트에 있으며, `verify-score-core.cjs`는 Node의 기본 기능으로 그 함수를 합성 숫자에 대해 검사합니다. 기대값은 독립적인 상수와 분수로 정합니다. 실제 배아의 예측 성능이나 이용자의 학습 효과를 검증하는 시험은 아닙니다.

기존 자료와의 관계는 [공식 기여 목록](https://virtualembryo.ai/challenge/resources)과 [Multilingual Starter 한국어 안내](https://github.com/random-guy-05/vec-multilingual-starter/blob/main/docs/tutorial_ko.md), [Local Scoring Wrapper](https://github.com/xxx12e/vec-community-kit/tree/main/vec_local_score), [Intuition Lab](https://github.com/i-habib/virtual-embryo-community/tree/main/intuition-lab), [Data Safety Kit](https://github.com/i-habib/virtual-embryo-community/tree/main/data-safety)의 공개 문서에서 확인했습니다. 이 저장소는 설치 없이 쓰는 한국어 학습 화면으로 그 자료를 보완합니다.

이 저장소는 원본 데이터나 실행 결과를 제공하지 않습니다. 코드의 실습 설정값은 절차를 보여 주기 위한 것이며 측정 결과가 아닙니다.
