# 출력이 저장되지 않은 실습 노트북을 만듭니다. 이 생성기는 과학 계산을 실행하지 않습니다.
import nbformat as nbf
nb = nbf.v4.new_notebook()
C = []

def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): C.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# 가상 배아 챌린지(VEC) 첫걸음 — 로컬 채점기 `veckit` 실습 노트북

> **비공식 커뮤니티 안내서입니다.** 대회 주최 측(스탠퍼드 Qiu Lab)이 만든 공식 자료가 아닙니다. 공식 내용과 다르면 언제나 공식 사이트(https://virtualembryo.ai/challenge)를 따르세요.

이 노트북은 **회원 가입 없이** 바로 돌릴 수 있도록, 공식 채점기 `veckit`(MIT 라이선스) 저장소에 함께 들어 있는 **아주 작은 견본 파일**(각 150개 세포)만 씁니다.

할 일:
1. `veckit` 설치와 버전 기록
2. 견본 파일 6개 내려받기
3. 과제 1(T1): '마지막 단계 그대로 베끼기(copy_last)' 예측을 만들고 채점
4. 공식 점수 환산식(바닥 50점, 천장 100점)을 견본 위에서 직접 따라 해 보기
5. 과제 2(T2): 발현과 3차원 좌표를 함께 채점하고, 회전·z축 반사에 따른 점수 차이와 정규화 오류를 살펴보기
6. 과제 3(T3): '야생형 그대로(wt_identity)' 예측과 '없앤 유전자만 0으로' 예측 채점
7. 흔한 실수: 유전자 순서가 다를 때

**주의:** 견본은 150개 세포뿐이라 여기서 나온 숫자는 **실제 대회 점수의 예고가 아닙니다.** 채점 흐름과 파일 형식을 익히는 연습용입니다. (veckit README에도 같은 경고가 있습니다.)

**자료 이용:** 이 저장소에는 데이터와 저장된 실행 출력이 없습니다. 견본은 실행할 때 공식 저장소에서 내려받습니다. 채점기의 소프트웨어 라이선스와 데이터·실행 결과의 이용 조건은 별개입니다. 데이터 사용과 결과 공유 전에는 [데이터 이용약관 14항](https://virtualembryo.ai/challenge/terms)과 [출판 안내](https://virtualembryo.ai/challenge/publish)를 확인하세요. [견본 설명: 공식 veckit README](https://github.com/aristoteleo/veckit/blob/cc3859ab2a2305efc4544815d3f44f660efa77d4/README.md)
""")

md(r"""
## 1. 설치

`veckit`은 파이썬 패키지 저장소(PyPI)에 올라와 있습니다. 이 노트북은 **0.1.2** 버전으로 고정해서 설치합니다.
""")

code(r"""
# veckit 설치 (버전 고정). anndata, numpy, scipy, scikit-learn 도 함께 설치됩니다.
%pip install -q "veckit==0.1.2"
""")

code(r"""
# 실행 환경 버전을 기록해 둡니다. 다른 사람이 같은 결과를 재현할 때 필요합니다.
import sys, platform, importlib.metadata as md_
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)   # FutureWarning 표시를 숨깁니다. scikit-learn 이외 라이브러리의 같은 종류 경고도 숨겨집니다.

VERSIONS = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    **{p: md_.version(p) for p in ["veckit", "anndata", "numpy", "scipy", "scikit-learn"]},
}
for k, v in VERSIONS.items():
    print(f"{k:13s} {v}")
""")

md(r"""
## 2. 견본 파일 내려받기

`veckit` 저장소의 `data/` 폴더에 있는 견본 6개를 받습니다. 나중에도 같은 견본 파일을 가져오도록 **특정 커밋(저장 시점) 주소로 고정**했습니다. `sample_heart_9.25`는 연습용 견본이며 공식 T2 학습 시점 목록의 한 단계라는 뜻은 아닙니다.

| 파일 | 이 노트북에서의 역할 |
|---|---|
| `sample_8.5.h5ad` | T1, 앞 단계(E8.5) — 단일세포 RNA, 32,285개 유전자 |
| `sample_9.5.h5ad` | T1, 맞혀야 할 단계(E9.5) 대신 쓰는 '연습용 정답' |
| `sample_heart_9.25.h5ad` | T2(심장), 앞 단계 |
| `sample_heart_9.5.h5ad` | T2(심장), 연습용 정답 |
| `sample_wt.h5ad` | T3, 야생형(유전자를 없애지 않은 정상 배아) |
| `sample_mab21l2_ko.h5ad` | T3, Mab21l2 유전자를 없앤(녹아웃) 배아 |

※ `.h5ad`는 단일세포 데이터를 담는 표준 파일 형식(AnnData)입니다.
""")

code(r"""
import hashlib, pathlib, urllib.request

COMMIT = "cc3859ab2a2305efc4544815d3f44f660efa77d4"   # veckit 저장소 main, 2026-10-02 커밋
BASE = f"https://raw.githubusercontent.com/aristoteleo/veckit/{COMMIT}/data/"
NAMES = ["sample_8.5", "sample_9.5", "sample_heart_9.25", "sample_heart_9.5", "sample_wt", "sample_mab21l2_ko"]

D = pathlib.Path("sample_data"); D.mkdir(exist_ok=True)
for n in NAMES:
    p = D / f"{n}.h5ad"
    if not p.exists():
        urllib.request.urlretrieve(BASE + p.name, p)
    print(f"{p.name:26s} {p.stat().st_size:>9,d} bytes  sha256={hashlib.sha256(p.read_bytes()).hexdigest()[:16]}")
""")

code(r"""
# 각 파일 안에 무엇이 들어 있는지 살펴봅니다.
import anndata as ad, numpy as np

def dense(X):
    return X.toarray() if hasattr(X, "toarray") else np.asarray(X)

A = {n: ad.read_h5ad(D / f"{n}.h5ad") for n in NAMES}
for n, a in A.items():
    X = dense(a.X)
    # expm1(X)의 세포별 합: '세포당 1만으로 맞춘 뒤 log1p' 정규화라면 약 10,000 이 나옵니다.
    libsize = float(np.median(np.expm1(X).sum(1)))
    print(f"{n:20s} 세포 {a.n_obs:4d} × 유전자 {a.n_vars:6,d} | 3D좌표: {'spatial_3D' in a.obsm} "
          f"| X 최댓값 {X.max():6.2f} | expm1 합 중앙값 {libsize:9.1f} | 세포유형 수 {a.obs['celltype'].nunique()}")
""")

md(r"""
세포별 `expm1(X)` 합과 최댓값은 입력의 정규화 상태를 점검할 때 참고할 수 있습니다. 정수 여부나 원시 카운트 여부를 이 두 값만으로 확정하지 마세요. 공식 제출 안내는 로그 정규화 값을 요구하며, 형식 검사를 통과한 것만으로 전처리가 맞다고 볼 수는 없습니다. 5장에서는 받은 값과 세포당 합계 10,000으로 맞춘 뒤 log1p한 값을 비교합니다. [출처: https://virtualembryo.ai/challenge/evaluation?section=submissions&task=2]
""")

md(r"""
## 3. 과제 1(T1) — '마지막 단계 그대로 베끼기(copy_last)'

공식 사이트에서 **바닥(floor)**, 즉 '아무것도 안 했을 때'의 기준 예측은 *마지막으로 관찰한 단계를 그대로 다시 내는 것*(copy_last)입니다. 여기서는 E8.5 견본을 그대로 E9.5에 대한 예측으로 냅니다.

`veckit.score()`에 넣는 세 파일:
- `input` : 채점할 예측
- `target` : 연습용 정답
- `reference` : '변화'를 재는 기준(앞 단계). 생략하면 `input`과 같다고 봅니다 → 변화 관련 지표가 0이 됩니다(아무것도 안 바꾼 예측에서는 이게 맞습니다).
""")

code(r"""
import json, veckit

RESULTS = {"versions": VERSIONS, "runs": {}}
def run(name, **kw):
    # veckit 으로 채점하고, 결과를 RESULTS 에 모아 둡니다.
    r = veckit.score(**kw)
    RESULTS["runs"][name] = r
    return r

def show(r, keys=None):
    m = r["metrics"]
    keys = keys or [k for k in m if not k.startswith("_")]
    print(json.dumps({k: m[k] for k in keys}, ensure_ascii=False))

T1 = dict(task="T1", target=D/"sample_9.5.h5ad", reference=D/"sample_8.5.h5ad")
r = run("T1_copy_last", input=D/"sample_8.5.h5ad", **T1)
print(r["meta"]); show(r)
""")

md(r"""
결과 읽는 법(공식 평가 페이지 기준, T1 순위에 쓰이는 네 지표):
- `de_score` (DES, 25%): 크게 오르내린 유전자를 맞혔는가. **높을수록 좋음.** 아무것도 안 바꿨으니 0.
- `de_direction` (DCS, 25%): 전체 유전자에서 변화 방향이 맞는가. **높을수록 좋음.** 역시 0.
- `mmd_u` (MMD, 30%): 세포 상태의 분포(어떤 세포가 어떤 비율로 있는가)가 같은가. **낮을수록 좋음.**
- `variogram` (CSS, 20%): 유전자끼리 함께 움직이는 구조가 유지되는가. **낮을수록 좋음.**

그 밖의 값(`energy_distance`, `pseudobulk_pearson` 등)은 참고용 진단값입니다.
""")

code(r"""
# 비교용: '정답을 그대로 낸' 경우 (현실에서는 불가능한, 위쪽 확인용)
r = run("T1_target_itself", input=D/"sample_9.5.h5ad", **T1); show(r, ["de_score","de_direction","mmd_u","variogram"])
""")

md(r"""
## 4. 점수 환산식을 직접 따라 하기 (바닥 50, 천장 100)

`veckit`은 **원래 단위의 지표 값**만 돌려줍니다. 리더보드는 대회 서버가 게시판(board)마다 잰 **바닥값**을 50, **천장값**을 100으로 환산합니다. 바닥보다 못한 예측은 50 미만의 점수도 받습니다. 공식 평가 페이지의 식은 다음과 같습니다.

- 천장까지의 거리 `d(m)` : 낮을수록 좋은 지표는 `m − 천장`, 높을수록 좋은 지표는 `천장 − m`
- 바닥 거리 `d_floor = |천장 − 바닥|`
- 지표와 기준값을 먼저 확인합니다. 지표가 없거나 NaN이면 skill 0입니다. 유효한 지표가 천장과 같거나 더 좋으면 나눗셈 전에 skill 1로 정하고, 그 밖의 경우에만 `d_floor / (d_floor + d(m))`를 계산합니다. → 바닥이면 0.5, 천장이면 1
- 과제 점수 = Σ(가중치 × skill) × 100

**이 실습의 환산 함수는 T1 전용입니다.** T2의 `scale_log_ratio`와 T3의 `severity_slope`는 측정값·바닥값·천장값을 먼저 절댓값으로 바꿔 작은 값이 좋도록 환산해야 합니다. 공식 지표의 모든 예외를 구현한 범용 환산기는 아닙니다.

동일·역전·비유한 바닥·천장에서는 이 교육용 코드가 합산을 멈춥니다. 작은 견본에서 기준값이 올바른 순서로 놓이지 않았다면, 이를 지표 결측으로 바꾸거나 억지로 점수를 내지 말고 기준값을 확인하세요. 이것은 이 코드의 보수적인 입력 정책으로, 공식 서버의 모든 예외 처리를 재현했다는 뜻은 아닙니다.

**천장**은 '정답의 절반을 나머지 절반에 대고 채점한 값'입니다. 여기서는 견본 E9.5(150개 세포)를 75개씩 둘로 나눠 같은 방식을 흉내 냅니다. 즉 아래 숫자는 **견본으로 만든 연습용 기준**이지, 공식 바닥·천장 값이 아닙니다(공식 값은 `index.json`과 평가 페이지에 게시판별로 나와 있습니다).
""")

code(r"""
# E9.5 견본을 고정된 난수(seed=0)로 둘로 나눕니다: 한쪽은 '정답', 다른 쪽은 '천장용 예측'.
rng = np.random.default_rng(0)
idx = rng.permutation(A["sample_9.5"].n_obs)
half_a, half_b = np.sort(idx[:75]), np.sort(idx[75:])
A["sample_9.5"][half_a].copy().write_h5ad(D/"t1_truth_halfA.h5ad")
A["sample_9.5"][half_b].copy().write_h5ad(D/"t1_ceiling_halfB.h5ad")

T1h = dict(task="T1", target=D/"t1_truth_halfA.h5ad", reference=D/"sample_8.5.h5ad")
floor   = run("T1h_floor_copy_last", input=D/"sample_8.5.h5ad", **T1h)["metrics"]
ceiling = run("T1h_ceiling_halfB",   input=D/"t1_ceiling_halfB.h5ad", **T1h)["metrics"]
for k in ["de_score","de_direction","mmd_u","variogram"]:
    print(f"{k:13s} 바닥 {floor[k]:>9.5f}   천장 {ceiling[k]:>9.5f}")
""")

code(r"""
# 공식 설명을 바탕으로 T1 네 지표의 환산 과정을 보여 줍니다.
# 지표 결측과 기준값 오류를 구분하며, 공식 채점기를 대체하지 않습니다.
import math
T1_WEIGHTS = {"de_score": 0.25, "de_direction": 0.25, "mmd_u": 0.30, "variogram": 0.20}
HIGHER_IS_BETTER = {"de_score", "de_direction"}

def skill(m, m_floor, m_ceil, key):
    if key not in T1_WEIGHTS:
        raise ValueError("이 함수는 T1 네 지표만 지원합니다: " + key)
    if m_floor is None or m_ceil is None or not all(math.isfinite(v) for v in (m_floor, m_ceil)):
        raise ValueError("기준값 오류: 바닥과 천장은 유한한 숫자여야 합니다.")
    d_floor = (m_ceil - m_floor) if key in HIGHER_IS_BETTER else (m_floor - m_ceil)
    if not math.isfinite(d_floor) or d_floor <= 0:
        raise ValueError("기준값 오류: 동일하거나 좋은 방향과 반대로 놓인 바닥·천장입니다.")
    if m is None or math.isnan(m):
        return 0.0               # 지표 결측: 가중치를 재분배하지 않음
    if not math.isfinite(m):
        raise ValueError("입력 오류: 지표값이 유한하지 않습니다.")
    d = (m_ceil - m) if key in HIGHER_IS_BETTER else (m - m_ceil)
    if not math.isfinite(d):
        raise ValueError("계산 범위 오류: 천장까지의 거리가 유한하지 않습니다.")
    if d <= 0:
        return 1.0               # 천장과 같거나 더 좋으면 나눗셈 전에 처리
    # d_floor + d가 넘쳐도 계산 가능한 경우를 위한 동치식입니다.
    ratio = d / d_floor if d <= d_floor else d_floor / d
    value = 1 / (1 + ratio) if d <= d_floor else ratio / (1 + ratio)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("계산 범위 오류: 환산값을 표현할 수 없습니다.")
    return value

def task_score(metrics, weights=T1_WEIGHTS):
    if (not weights or any(k not in T1_WEIGHTS or not math.isfinite(w) or w < 0 for k, w in weights.items())
            or not math.isclose(sum(weights.values()), 1.0, rel_tol=0, abs_tol=1e-12)):
        raise ValueError("가중치 오류: 지원하는 지표의 유한한 비중 합계가 1이어야 합니다.")
    s = {k: skill(metrics.get(k), floor.get(k), ceiling.get(k), k) for k in weights}
    total = 100 * sum(weights[k] * v for k, v in s.items())
    return total, s

for name in ["T1h_floor_copy_last", "T1h_ceiling_halfB"]:
    total, s = task_score(RESULTS["runs"][name]["metrics"])
    print(f"{name:22s} 과제 점수 {total:6.1f}   " + "  ".join(f"{k}={v:.3f}" for k, v in s.items()))
""")

md(r"""
바닥 예측은 정의상 **50점**, 천장 예측은 **100점**이 나옵니다. 이제 공식 '함정 예측(adversarial control)' 두 가지를 견본으로 만들어 봅시다.

- `ctrl_one_cell` : 앞 단계의 **평균 세포 하나를 복사해서** 세포 수만 맞춘 예측. 공식 설명: 평균만 비교하는 지표에서는 그럴듯하지만, 분포를 비교하는 두 지표(MMD, CSS)에서는 거의 0점.
- `ctrl_scale_ref` : 앞 단계 값을 **모두 2배**로 키운 예측. 공식 설명: 이런 예측이 바닥보다 높게 나오면 지표에 구멍이 있다는 뜻.
""")

code(r"""
a85 = A["sample_8.5"]
one = a85.copy(); one.X = np.tile(dense(a85.X).mean(0, keepdims=True), (a85.n_obs, 1)).astype(np.float32)
one.write_h5ad(D/"t1_ctrl_one_cell.h5ad")
x2 = a85.copy(); x2.X = (dense(a85.X) * 2.0).astype(np.float32)
x2.write_h5ad(D/"t1_ctrl_scale_ref.h5ad")

for name, f in [("T1h_ctrl_one_cell", "t1_ctrl_one_cell.h5ad"), ("T1h_ctrl_scale_ref", "t1_ctrl_scale_ref.h5ad")]:
    m = run(name, input=D/f, **T1h)["metrics"]
    total, s = task_score(m)
    print(f"{name:20s} 과제 점수 {total:6.1f}   " + "  ".join(f"{k}={v:.3f}" for k, v in s.items()))
""")

md(r"""
자신의 실행 결과에서 두 함정 예측을 바닥 기준과 비교해 보세요. 견본이 작아 값이 흔들릴 수 있으며, 공식 설명의 경향이 모든 작은 견본에서 그대로 나온다고 보장되지는 않습니다. 이 실습의 기준값은 공식 게시판의 기준값과 다릅니다. [출처: https://virtualembryo.ai/challenge/baselines]
""")

md(r"""
## 5. 과제 2(T2) — 유전자 발현 + 3차원 좌표

T2 제출 파일에는 `.X`(발현)와 함께 **`obsm["spatial_3D"]`(세포마다 x, y, z 좌표)**가 반드시 있어야 합니다. copy_last는 앞 단계의 세포와 좌표를 그대로 냅니다.

먼저 `sample_heart_9.25`를 받은 그대로 채점하고, 그다음 **세포당 1만으로 맞춘 뒤 log1p** 처리한 판과 비교합니다.
""")

code(r"""
T2 = dict(task="T2", setting="heart", target=D/"sample_heart_9.5.h5ad")
KEYS2 = ["de_score","de_direction","mmd_u","variogram","d2_shape","occupancy_dice","scale_log_ratio","neighborhood_mmd"]

# (가) 내려받은 값 그대로. 이 단계만으로 원시 카운트임을 판정하지 않습니다.
r_raw = run("T2_copy_last_as_received", input=D/"sample_heart_9.25.h5ad", **T2); show(r_raw, KEYS2)

# (나) 세포당 합계를 10,000으로 맞춘 뒤 log1p 한 판
a925 = A["sample_heart_9.25"].copy()
X = dense(a925.X).astype(np.float64)
a925.X = np.log1p(X / np.maximum(X.sum(1, keepdims=True), 1e-12) * 1e4).astype(np.float32)
a925.write_h5ad(D/"heart_9.25_lognorm.h5ad")
r_ln = run("T2_copy_last_lognorm", input=D/"heart_9.25_lognorm.h5ad", **T2); show(r_ln, KEYS2)
""")

md(r"""
두 줄의 발현 지표(`mmd_u`, `variogram` 등)를 비교해 전처리 전후에 어떤 값이 달라지는지 살펴보세요. 공식 안내는 **로그 정규화되지 않은 값도 형식 검사를 통과할 수 있지만 채점 결과는 잘못될 수 있다**고 경고합니다. 이 견본처럼 세포당 합계 10,000으로 맞춘 뒤 log1p한 데이터에서는 `np.expm1(X).sum(1)`이 약 10,000인지 확인할 수 있습니다. 모든 단일세포 데이터의 정규화가 같은 합계를 쓰는 것은 아니므로 실제 제출 데이터의 공식 전처리 조건을 따르세요.

### 회전 오류와 좌우 반전(거울상) 맹점
공식 FAQ는 형태 지표의 좌우성 맹점을 설명합니다. 아래 실습은 z축 부호를 뒤집는 기하학적 반사 시험입니다. 어느 축을 뒤집든 공간의 방향성을 뒤집는 변환이므로, z축이 해부학적 좌우축인지 몰라도 거울상 시험으로 유효합니다. [출처: https://virtualembryo.ai/challenge/faq]

정답 파일 자체의 좌표를 (가) 그대로, (나) 회전만, (다) z축 거울 반전해서 채점해 봅니다.
""")

code(r"""
t95 = A["sample_heart_9.5"]
C0 = np.asarray(t95.obsm["spatial_3D"], dtype=np.float64)[:, :3]
th = np.deg2rad(40)
Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
variants = {"same": C0, "rotated_40deg": C0 @ Rz.T, "mirrored_z": C0 * np.array([1, 1, -1])}
SHAPE = ["d2_shape","sliced_wasserstein","occupancy_dice","scale_log_ratio","neighborhood_mmd","morans_I_agreement"]
for name, C in variants.items():
    v = t95.copy(); v.obsm["spatial_3D"] = C.astype(np.float32)
    v.write_h5ad(D/f"heart_9.5_{name}.h5ad")
    m = run(f"T2_geometry_{name}", input=D/f"heart_9.5_{name}.h5ad", reference=D/"heart_9.25_lognorm.h5ad", **T2)["metrics"]
    print(f"{name:14s} " + "  ".join(f"{k}={m[k]}" for k in SHAPE))
""")

md(r"""
회전한 좌표와 반사한 좌표의 원시 지표를 비교해 채점기의 반응을 살펴보세요. PyPI 0.1.2의 회전 오류(#7)는 main의 PR #9에서 수정됐지만 이 노트북이 설치하는 0.1.2에는 포함되지 않았습니다. 이 실습으로 실제 배아의 좌우 패턴 예측 성능이나 모든 형태의 거울상 구분 성능을 검증할 수는 없습니다. [출처: https://github.com/aristoteleo/veckit/issues/7, https://github.com/aristoteleo/veckit/pull/9]

**Dice 해석에는 별도 조건이 있습니다.** 공식 안내는 격자 한 변 길이 ÷ 실제 세포의 최근접 이웃 거리 중앙값이 약 10보다 충분히 클 때만 조직 Dice를 해석하도록 합니다. 자신의 결과에서 `_dice_voxel_over_nn`을 확인하세요. 이 값은 앞선 `run()` 함수가 모은 `RESULTS["runs"]`의 각 기하학 기록에서 `metrics`에 들어 있습니다. 8장을 실행한 뒤 `results/scores.json`에서 `T2_geometry_same` 등의 기록을 열어 확인할 수 있습니다. 작은 견본의 Dice 크기를 조직 형태 정확도로 읽지 마세요. [출처: https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2]
""")

md(r"""
## 6. 과제 3(T3) — 유전자를 없앤 배아 예측

T3의 바닥은 **야생형을 그대로 내는 것(wt_identity)** — '돌연변이가 아무 영향도 없었다'는 예측입니다. 공식 설명대로 T3 점수는 *야생형 → 돌연변이로의 변화*에 매겨지므로, 야생형을 그대로 내면 `de_score`와 `de_direction`은 0입니다. `severity_slope`까지 0이라는 뜻은 아닙니다.

비교로 공식 기준선 `gene_ko`의 핵심 아이디어(없앤 유전자의 발현을 0으로)만 야생형에 적용해 봅니다. (공식 `gene_ko`는 `shift_transfer` 위에 이것을 더한 것이고, 여기서는 단순화한 연습판입니다.)
""")

code(r"""
T3 = dict(task="T3", target=D/"sample_mab21l2_ko.h5ad", wt=D/"sample_wt.h5ad")
KEYS3 = ["de_score","de_direction","severity_slope","mmd_u","variogram"]

r = run("T3_wt_identity", input=D/"sample_wt.h5ad", **T3); print(r["meta"]); show(r, [k for k in KEYS3 if k in r["metrics"]])

wt = A["sample_wt"].copy(); X = dense(wt.X).copy()
X[:, list(wt.var_names).index("Mab21l2")] = 0.0
wt.X = X.astype(np.float32); wt.write_h5ad(D/"t3_wt_mab21l2_zeroed.h5ad")
r = run("T3_wt_gene_zeroed", input=D/"t3_wt_mab21l2_zeroed.h5ad", **T3); show(r, [k for k in KEYS3 if k in r["metrics"]])
""")

md(r"""
## 7. 흔한 실수 — 유전자 순서

공식 데이터 페이지: 제출 파일의 유전자 이름(`var_names`)은 게시판의 유전자 목록과 **같은 유전자, 같은 순서**여야 합니다. 순서만 다르면 `--allow-reorder`(파이썬에서는 `allow_reorder=True`)로 채점기가 다시 정렬해 줍니다.
""")

code(r"""
shuf = A["sample_8.5"][:, np.random.default_rng(1).permutation(A["sample_8.5"].n_vars)].copy()
shuf.write_h5ad(D/"t1_shuffled_genes.h5ad")
try:
    veckit.score(input=D/"t1_shuffled_genes.h5ad", **T1)
    print("오류 없음(예상과 다름)")
except Exception as e:
    msg = str(e)
    print("오류 발생 — 유전자 순서 오류인지 원인을 확인하세요:", type(e).__name__, "-", msg[:300])
    RESULTS["runs"]["T1_shuffled_genes_error"] = {"error": type(e).__name__, "message": msg[:500]}

r = run("T1_shuffled_allow_reorder", input=D/"t1_shuffled_genes.h5ad", allow_reorder=True, **T1)
print("allow_reorder=True →", {k: r["metrics"][k] for k in ["de_score","de_direction","mmd_u","variogram"]})
print("원래 copy_last와 같은가?", r["metrics"] == RESULTS["runs"]["T1_copy_last"]["metrics"])
""")

md(r"""
## 8. 로컬 결과 저장

실행하면 채점 결과와 버전이 `results/scores.json`에 저장됩니다. 출력의 “채점 횟수”는 성공한 채점뿐 아니라 의도적으로 발생시킨 오류 기록도 포함한 항목 수입니다. 이 저장소에는 해당 파일을 넣지 않았습니다. 생성한 데이터와 실행 결과는 공개하기 전에 이용 조건을 확인하세요.
""")

code(r"""
out = pathlib.Path("results"); out.mkdir(exist_ok=True)
(out / "scores.json").write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print("저장:", out / "scores.json", "| 채점 횟수:", len(RESULTS["runs"]))
print("\n요약 (T1 연습용 환산 점수)")
for n in ["T1h_floor_copy_last","T1h_ceiling_halfB","T1h_ctrl_one_cell","T1h_ctrl_scale_ref"]:
    print(f"  {n:22s} {task_score(RESULTS['runs'][n]['metrics'])[0]:6.1f}")
""")

md(r"""
## 다음 단계
- 실제 데이터는 공식 사이트에서 **로그인 후** 받습니다: https://virtualembryo.ai/challenge/data
- 실제 제출 파일의 유전자 목록은 게시판별 `*.genes.txt`와 `index.json`에서 가져오세요(데이터 페이지).
- 채점기 문제는 veckit 이슈 게시판에: https://github.com/aristoteleo/veckit/issues

**출처·감사:** 채점기는 `aristoteleo/veckit`(소프트웨어 MIT 라이선스, © 해당 저작권자)입니다. 대회는 스탠퍼드 대학교 Qiu Lab과 협력자들이 운영하며, 데이터는 UC San Diego의 Qingquan Zhang 박사와 Neil Chi 박사 연구팀이 만들었습니다. 데이터 이용·출처 표기·발표 조건은 [약관 14항](https://virtualembryo.ai/challenge/terms)을 따르세요. 작성자는 Byungwoong Yoo(Independent Researcher, BigWonder)이며, 이 노트북은 비공식 커뮤니티 자료입니다.
""")

nb["cells"] = C
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb["metadata"]["language_info"] = {"name": "python"}
nbf.write(nb, "vec_ko_tutorial.ipynb")
print("written", len(C), "cells")
