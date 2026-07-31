---
name: profitability_analysis
description: Excel P&L raw data parsing, standard/fundamental profitability calculations, Waterfall bridge analysis, and business implication extraction.
---

# Profitability Analysis Skill

이 스킬은 LGE Swiss 지점 TV 수익성 NERP 데이터를 가공하고 분석하여 경영진이 즉각 의사결정할 수 있는 재무 지표 및 시사점(Implications)을 도출하는 지침을 정의합니다.

## 1. P&L Structure & Formulas

이 스킬을 사용하는 에이전트는 원천 데이터 집계 시 반드시 다음 공식과 변수 매핑을 사용해야 합니다.

### Standard P&L 지표
- **Net Sales (시산)**: `Net Sales` 컬럼의 합산.
- **Gross Sales (실적)**: `GrossSales_Actual` (`Gross Sales(실적)`) 컬럼의 합산.
- **Sales Deduction (매출 차감)**: `Sales Deduction` 컬럼의 합산 (음수).
- **Marginal Profit (MP)**: `Marginal Profit` 컬럼의 합산.
- **Operating Income (COI)**: `Operating Income` 컬럼의 합산.
- **Net ASP**: `NetSales_Actual` / `Qty_Actual` (제상품 Net Sales / 판매량).
- **MP%**: `Marginal Profit` / `Net Sales`.
- **COI%**: `Operating Income` / `Net Sales`.
- **S/D%**: `abs(Sales Deduction)` / `Gross Sales(실적)`.

### Fundamental P&L 지표 (Gap 보정)
Fundamental 손익은 결산 시점의 일시적 Gap 항목(반품충당금, 판가 차이 등)을 소급 조정하여 실질 수익성을 판단하기 위한 지표입니다.
- **Total_Gap**: `PL Gap` + `COGS Gap` - `COGS_Allowance for Return` (단, 각 컬럼의 `NaN` 결측치는 반드시 `0`으로 사전 치환해야 함).
- **Variable_Total_Gap**: `Variable PL Gap` + `Variable COGS Gap` - `Variable COGS_Allowance for Return`.
- **MP_Fundamental**: `Marginal Profit` + `Variable_Total_Gap`.
- **COI_Fundamental**: `Operating Income` + `Total_Gap`.
- **MP%_Fundamental**: `MP_Fundamental` / `Net Sales`.
- **COI%_Fundamental**: `COI_Fundamental` / `Net Sales`.

### YTD Trend 시계열 데이터 가공 공식 (Spacer 단절 및 진척도)
YTD 콤보 차트에 제공되는 데이터는 Standard 및 Fundamental 각각의 손익 계산 로직(`calc_pnl_structure` 대 `calc_fundamental_pnl_structure`)을 적용하여 다음과 같이 조립합니다:
1. **다개년 YTD (2023-2026)**: 각 연도의 1월부터 당해 최신 마감월(예: 5월)까지의 누계 데이터를 슬라이싱한 뒤, Standard 기준은 `mp_rate`/`coi_rate`를 추출하고 Fundamental 기준은 `mp_fundamental_rate`/`coi_fundamental_rate`를 매핑합니다.
2. **Spacer 영역**: 누계 성격 분할을 위해 중간 인덱스에 `{ sales: null, mp_rate: null, coi_rate: null, is_spacer: true }`를 주입합니다.
3. **당해 월별 누적 진척도**: 당해 연도(2026년)의 1월 누적부터 최신 마감월 누적까지 월별 YTD 슬라이스를 순차적으로 루프 연산하여 시계열 트렌드로 추가합니다.

### 제품군별 수익성 분석 데이터 연산 (get_blu_dashboard_data)
- **세그먼트 분류 조건 (Lambda 형식)**:
  - OLED: `lambda s: s['OLED/UHD'] == 'OLED'`
  - QNED: `lambda s: s['QNED'] == 'QNED'`
  - 일반 UHD: `lambda s: (s['OLED/UHD'] == 'UHD') & (s['QNED'] != 'QNED')`
  - FHD: `lambda s: s['OLED/UHD'] == 'FHD'`
  - 초대형: `lambda s: s[large_col] == '초대형'` (여기서 `large_col`은 17번째 열인 `초대형(OLED포함)`을 가리킵니다. 초대형 모델은 이 열에 `'초대형'` 문자열이, 일반 모델은 `'x'` 문자열이 입력되어 있습니다.)
  - **인코딩 선언 필수 규칙 (Encoding Declaration)**: Windows 한글 환경(CP949 기본값)에서 Python이 스크립트를 실행할 때 코드 내 한글 리터럴 `'초대형'` 비교 연산이 불일치하는 오류를 방지하기 위해, 실행 파이썬 스크립트 파일 최상단에 반드시 **`# -*- coding: utf-8 -*-`** 선언을 추가해야 합니다.
  * Pandas 연산 시 Boolean Series key mismatch 경고를 피하기 위해 반드시 슬라이스된 dataframe에 대해 직접 람다 조건 마스킹을 수행하여 결측치 전파 및 warnings를 사전 차단해야 합니다.
- **YTD / MTD 분리 구조**:
  - 차트의 동적 토글을 위해 `s3_profit_ytd`와 `s3_profit_mtd`, 그리고 Others 점유 비중(`others_share = others_coi / total_coi`)을 별도 메타데이터(`s3_meta_ytd`, `s3_meta_mtd`)로 분리 산출하여 JSON payload에 전달합니다.
- **명칭 통일**:
  - 데이터 연산 키로는 기존의 `Others`를 유지하되, 화면에 노출되는 범례, 축 라벨, 말풍선, 툴팁, 아코디언 행 헤더 등 모든 UI 레이블은 반드시 **`'기타 매출'`**로 한글 명칭 통일하여 매핑 렌더링해야 합니다.

---

## 2. Waterfall YoY Bridge Analysis

전년 YTD vs 당년 YTD 영업이익(COI) 증감 분석 시 다음 Bridge 연산 공식을 사용하여 차액(Explained Delta)이 실제 COI 증감액과 100% 일치해야 합니다:

1. **물량 효과 (Volume Effect)**: 
   $$(Qty_{This} - Qty_{Last}) \times \frac{COI_{Last}}{Qty_{Last}}$$
2. **가격 효과 (Price Effect)**: 
   $$Qty_{This} \times (GrossASP_{This} - GrossASP_{Last})$$
   *(단, Gross ASP = Gross Sales / Qty)*
3. **매출차감 효과 (S/D Effect)**: 
   $$Qty_{This} \times (SD\_Unit_{This} - SD\_Unit_{Last})$$
   *(단, SD_Unit = SD_val / Qty)*
4. **변동원가 효과 (Variable COGS Effect)**: 
   $$-Qty_{This} \times (VarCOGS\_Unit_{This} - VarCOGS\_Unit_{Last})$$
   *(단, VarCOGS_Unit = Variable COGS / Qty)*
5. **고정비 효과 (Fixed Cost Effect)**: 
   $$-(FixedCost_{This} - FixedCost_{Last})$$
   *(단, Fixed Cost = Fixed COGS + Fixed SG&A)*
6. **기타/Gap 효과 (Residual Gap)**: 
   $$\text{Delta COI} - (\text{물량} + \text{가격} + \text{매출차감} + \text{변동원가} + \text{고정비 효과})$$

---

## 3. Implication & Comment Extraction Rules

### 3.1 에이전트의 정체성 (Analyst Identity)
- 이 스킬을 활용하는 에이전트는 자신을 전문 **비즈니스 및 재무 분석가 (Business and Financial Analyst)**로 포지셔닝해야 합니다.
- 주관적인 과장이나 모호한 형용사(예: 소폭 변동을 '주요 악화 요인'으로 기술하는 등)를 배제하고, 반드시 아래의 정량적 임계값(Threshold)에 기반하여 팩트 중심의 객관적 서술을 수행해야 합니다.

### 3.2 수치 변동 동사 & 형용사 매핑 룰 (Quantitative Modifiers)
에이전트는 데이터 분석 결과에 따라 아래의 분기 규칙을 100% 준수하여 문장을 조립해야 합니다:

1. **판매량 증감 판단**:
   - MTD 전월비: `qty_vs_prev_pct >= 0` 이면 `"증가"`, 미만이면 `"감소"` 로 표기.
   - 최근 6개월 평균비: `qty_vs_avg_pct >= 0` 이면 `"증가하여 전반적인 물량 회복 흐름"`, 미만이면 `"감소하여 물량 둔화 흐름"` 으로 표기.
2. **이익률 변동 판단**:
   - `coi_vs_prev_p >= 0` 이면 `"상승"`, 미만이면 `"하락"` 로 표기.
3. **매출차감률(S/D%) 변동 영향 수식어 판단**:
   - **보합 수준 (`abs(sd_vs_prev_p) < 0.5%p`)**: `"소폭 변동(보합세)하여 마진 영향은 극히 제한적"` 으로 기술.
   - **보통 수준 (`0.5%p <= abs(sd_vs_prev_p) < 1.5%p`)**: `"일부 변동하여 마진에 소폭 영향을 주었으나"` 로 기술.
   - **급변 수준 (`abs(sd_vs_prev_p) >= 1.5%p`)**: `"급증/급감하여 실질 수익성을 상쇄/개선하는 주요 변동 요인"` 으로 기술.

### 3.3 5문장 조립 템플릿
- **1문장 (현상 진단)**: 당월 판매량 및 영업이익률(COI%)을 전월 및 최근 6개월 평균값과 대조하여 총평합니다.
  - 포맷: `"2026년 [당월]월 실적은 판매량 [당월Qty]대, 영업이익률 [당월COI]%를 기록하여 전월([전월Qty]대, [전월COI]%) 대비 판매량은 [전월비Qty증감]% [증가/감소]했으며 영업이익률은 [전월비COI변동]p [상승/하락]했고, 최근 6개월 평균 대비로도 판매량은 [6개월평균비Qty증감]% [증가하여 전반적인 물량 회복 흐름 / 감소하여 물량 둔화 흐름]을 보이고 있습니다."`
- **2문장 (개선 요인)**: 마진을 방어했거나 단가(ASP) 상승을 견인한 고부가 제품 믹스(OLED, QNED) 영향 등을 분석합니다.
- **3문장 (악화 요인)**: 이익률에 악영향을 준 매출차감률(S/D%) 변동 등을 위의 임계값 수식어 룰에 맞춰 정량적으로 기술합니다.
- **4문장 (결산조정 및 특이사항)**: 충당금 환입(Allowance for Return 등), 일회성 비용 등의 일시적 결산 보정이 일어났는지 객관적으로 서술합니다.
- **5문장 (Implication 종합)**: 향후 마진 보존이나 비즈니스 개선을 위해 주시해야 할 핵심 지표를 요약 제시합니다.

---

## 4. Fundamental Waterfall Bridge & Analysis Guidelines (실질 손익 브릿지 분석 규격)

### Fundamental Waterfall Bridge 수식
대시보드 내 `Fundamental Waterfall` 차트 렌더링 시, standard 지표와 Gap 보정 요인의 수학적 결합 관계를 다음 브릿지 흐름에 맞춰 100% 동일하게 일치시킵니다:
1. **Net Sales**에서 시작하여 변동비 항목(`재료비`, `변동O/H`, `판촉비`, `물류비`, `지급수수료`, `SVC비`, `기타 변동비`)을 감해 **`MP (Standard)`**를 유치합니다.
2. `MP (Standard)`에서 고정비 항목(`광고비`, `지급수수료`, `인건비`, `관리비`, `R&D`, `SVC`, `기타 고정비`)을 감해 **`COI (Standard)`**를 도출합니다.
3. `COI (Standard)`에서 실질 손익 보정 항목인 **`PL Gap`** (가산/감산), **`COGS Gap`** (가산/감산), **`COGS Allowance`** (충당금 차감 영향, 음수) 단계를 순차적으로 거쳐 최종 목적지인 **`COI (Fundamental)`**을 완벽하게 수식 Reconcile 하여 표출합니다.

### 관리회계 전문가 시사점 템플릿 (Management Accounting Viewpoints)
탭 전환 시 활성화된 탭의 재무적 성격에 최적화된 인사이트를 제공합니다:
- **P&L Structure 탭**: 다개년 재료비율 하락 추세(마진 방어 핵심 동인) 및 물량/ASP 상관관계 분석, 고정 O/H 계정 분류 상쇄 영향에 초점을 맞추어 5문장 내외로 관리회계 오피니언을 작성합니다.
- **Fundamental P&L 탭**: 보고상 실적과 실질 기초 수익력(Underlying Profitability) 간의 갭을 만드는 PL/COGS Gap 요인의 정의와 발생 원인을 해설하고, 장부상 수치 이면의 지점 원가 통제 효율을 입증하는 내용을 5문장 내외로 서술합니다.

### Account별 성과 현황 데이터 연산 (get_account_detail)
- **MTD / YTD 연산 분리**: 
  - `get_account_detail(df, latest_year, max_month, is_ytd=True, is_fundamental=False)` 함수는 `is_ytd` 값에 따라 당월 실적 또는 YTD 누계 실적 데이터를 슬라이싱하여 거래선별 실적을 산출해야 합니다.
- **동적 매출 비중(Sales Share %)**: 
  - 각 거래선별 '매출 비중'은 조회 기준의 전사 총 Net Sales에 연동되어 동적으로 계산되어야 합니다. 즉, MTD 조회 시에는 당월 전사 합산 Net Sales 대비 비중을, YTD 조회 시에는 YTD 전사 합산 Net Sales 대비 비중으로 나누어 산출합니다.

### 대용량 엑셀 데이터 비동기 로드 규칙
- 베네룩스(LGEBN) 등 행수가 15만 행 이상(약 230MB 이상)인 지점의 경우, pyxlsb 엔진을 이용한 엑셀 로딩 시 메모리가 수백 MB 이상 소모되고 연산에 수 분 가량 소요됩니다.
- 따라서, 실행 환경 구축 시 전용 portable python(`python_portable\python.exe`) 인터프리터를 지정하고, 백그라운드 비동기 태스크 명령어로 실행하여 시스템 타임아웃을 차단해야 합니다.
