---
name: html_report_generation
description: Generating interactive HTML profitability dashboards with w-72 sidebar layout, responsive grids, Pure SVG vector charts, and standard rounding formatters.
---

# HTML Report Generation Skill

이 스킬은 엑셀 데이터를 경영진 보고용 프리미엄 HTML 대시보드로 자동 빌드하고 시각화하는 프론트엔드 퍼블리싱 규격을 정의합니다.

## 1. UI/UX & Layout Standards

대시보드 생성 에이전트는 다음 스타일 규칙을 엄격히 준수하여 경영진에게 "Wow Factor"를 제공해야 합니다.

- **McKinsey & Stitch 스타일 테마**:
  - 메인 네이비: `bg-primary: #051c2c` (사이드바 배경)
  - 보조 포인트 및 강조: `#00538c` (Royal Blue)
  - 긍정/이익률 지표: `#00a3a3` (Teal)
  - 리스크/경고 지표: `#e11d48` (Crimson Red)
  - 전체 배경: `#f6faff` (밝은 블루톤의 화이트)
- **고정형 사이드바 레이아웃 (w-72)**:
  - 좌측에 너비 `w-72` 고정 네이비 사이드바가 위치하며, 8개의 메뉴 항목이 배치됩니다.
  - 메뉴 항목 번호 표기는 로마자(I, II, III...) 대신 아라비아 숫자(1, 2, 3...)를 사용하며, 한글 번역이 완료된 명칭으로 매핑합니다.
  - **목차/제목 매핑 규격**:
    1. **1. 당월 수익성** (Right Title: **당월 수익성**)
    2. **2. 월별 수익성 추이** (Right Title: **월별 수익성 추이**)
    3. **3. Fundamental 수익성** (Right Title: **Fundamental 수익성**)
    4. **4. 제품군별 수익성** (Right Title: **제품군별 수익성**)
    5. **5. 시리즈별 수익성** (Right Title: **시리즈별 수익성**)
    6. **6. 모델별 수익성** (Right Title: **모델별 수익성**)
    7. **7. Account별 수익성** (Right Title: **Account별 수익성**)
    8. **8. Account별 수익성 상세** (Right Title: **Account별 수익성 상세**)
    9. **9. Sales Deduction** (Right Title: **Sales Deduction Analysis**)
  - 각 메뉴 아이콘은 Google Material Symbols Outlined 라이브러리를 사용합니다.
- **Default Active Tab (기본 활성 탭)**:
  - 대시보드가 최초 로드될 때 default active 탭은 반드시 **`1. 당월 수익성`** (current_month_pnl) 뷰여야 합니다.
- **반응형 뷰포트**:
  - `ml-72 flex-1 flex flex-col min-h-screen` 구조로 메인 본문 콘텐츠를 분리하고, 스크롤 가능한 SPA(Single Page Application) 구조로 실시간 탭 전환을 구현합니다.

---

## 2. Formatting Policy (수치 표기 규격)

대시보드 내부의 모든 숫자 렌더링 시 다음 전역 포맷 규칙을 적용해야 합니다:

### 퍼센트(%) 및 변동폭(%p) 포맷팅
- 모든 비율 지표(YoY 증감률, MP%, COI%, S/D%, COGS%)는 **소수점 첫째 자리**까지만 반올림 표기합니다.
- 비율 손익 항목(S/D Ratio, MP Ratio, COI Ratio)의 전년 대비 변동 표기 시, `증감액` 열은 `-`로 비우고, `증감률` 열에 `%p` 단위를 붙여 `▲/▼` 형태 및 시맨틱 색상(Teal/Crimson)으로 표기합니다.
- JavaScript 포맷터:
  ```javascript
  function fmtPercent(val) {
      if (val === null || val === undefined || isNaN(val)) return '-';
      return (val * 100).toFixed(1) + '%';
  }
  ```

### 금액 관련 지표 포맷팅 (K$ 표준화)
- 판매량을 제외한 모든 매출 및 손익 금액 지표는 원본 달러($) 값을 **1,000으로 나누어 소수점을 완전히 제거한 뒤 정수 단위로 반올림하고 K$ 접미사**를 붙여 포맷팅합니다.
- JavaScript 포맷터:
  ```javascript
  function fmtCurrency(val) {
      if (val === null || val === undefined || isNaN(val)) return '-';
      const kVal = Math.round(val / 1000);
      return kVal.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + 'K$';
  }
  ```

---

## 3. Pure SVG Vector Charts Guideline

대시보드 파일은 단독 오프라인 구동 및 보안 유지를 위해 외부 라이브러리(Chart.js, ApexCharts 등) 없이 **순수 HTML5 SVG 태그**로 차트를 직접 그립니다:

1. **월별 추이 차트 (Trend)**:
   - Net Sales(막대, Royal Blue `#00538c`, 적자 월은 Crimson Red `#e11d48`) + MP%(꺾은선, Teal `#00a3a3`) + COI%(꺾은선, Deep Navy `#051c2c`)를 2중 Y축 형태로 하나의 SVG 컨테이너에 중첩 렌더링합니다.
2. **Waterfall 차트 (Bridge)**:
   - 다단 브리지 형태로, 시작/끝 YTD 막대(Deep Navy `#051c2c`), 증익 요인(Teal `#00a3a3`), 감익 요인(Crimson Red `#e11d48`) 막대로 구분하여 SVG로 빌드하고 커넥터 점선(`stroke-dasharray="2 2"`)을 연결합니다.
3. **매출차감 세부 비중 차트 (Stacked Rebate)**:
   - TT(Slate Gray `#64748b`), NTTSI(Royal Blue `#00538c`), NTTSO(Crimson Red `#e11d48`) 지표를 가로 막대에 위로 쌓는 누적 막대 차트(Stacked Bar) 형태로 SVG를 렌더링합니다.
   - **뷰포트 및 레이아웃**: SVG 너비를 `800px`, 우측 여백을 `240px`로 설계하고 막대 두께(`barW`)를 `50px~52px` 수준으로 넓혀 캔버스 가독성을 높입니다.
   - **수치 표시**: 막대 최상단에는 합산 S/D%를, 막대 내부(TT, NTTSO)에는 각 세그먼트별 비율을 백색 텍스트로 표시합니다 (세그먼트 세로 높이가 14px 미만인 경우 글자 겹침 방지를 위해 생략).
   - **오른쪽 요약 정보**: 수직 점선 우측에 YTD/MTD 누적 S/D% 및 전년비 YoY 증감(%p)을 Crimson Red(증가 시)/Teal(감소 시)로 렌더링하고, 그 하단에 범례를 표시합니다.
   - **유통 채널별 조회 연동**: 대시보드 상단에 가로형 단일 선택기 버튼 목록을 배치하여 채널별 조회를 가능하게 합니다. 첫 번째 채널은 'TV Total'로 두고, 유통 선택 시 막대 그래프, X축 하단의 상세 수치 행, 우측 실적 요약 카드 데이터가 해당 유통의 전용 실적으로 동시 연동되어 실시간 변경되어야 합니다.
4. **제품군별 월별 실적 추이 차트 (Segment Combo Chart)**:
   - 세그먼트별 순수 실적 비교를 위해 상단에 필터용 버튼 필(OLED, QNED, 일반 UHD, FHD, 초대형 순서 고정, **초대형은 FHD 뒤에 위치**)을 제공합니다.
   - **단일 선택(Single-Selection) 강제**: 다중 선택을 방지하여 사용자가 각 카테고리를 독립적으로 하나씩 비교 분석할 수 있도록 라디오 버튼(Radio Button) 방식으로 제어합니다. (최소 1개의 제품군은 반드시 활성 상태여야 하므로 이미 활성화된 버튼 재클릭 시 비활성화 차단).
   - 최초 로드 시 **OLED** 제품군만 단독 활성화 상태로 차트를 렌더링합니다.
5. **마우스 호버 툴팁**:
   - SVG 엘리먼트 내에 `onmousemove="showTooltip(event, '내용')"` 및 `onmouseout="hideTooltip()"` 속성을 바인딩하고 CSS `:hover` 투명도 조절 효과를 가미합니다.

---

## 4. Implication Area (시사점 영역) 렌더링 규격

대시보드 하단에는 경영진의 의사결정을 돕는 종합 시사점 요약 상자를 배치합니다:
- **레이아웃**: 
  - 배경색: `#ffffff`
  - 외곽선: `border-slate-200` 및 좌측 세로 바에 `border-l-4 border-l-accent-blue` (Stitch 테마 강조선) 적용
  - 패딩 및 효과: `p-8`, `rounded-lg shadow-sm` 적용
- **타이틀**:
  - 타이틀 텍스트는 반드시 **`Implication`**으로 표기하고, notes 아이콘(`material-symbols-outlined`)을 나란히 배치합니다.
- **주석 텍스트 연동**:
  - 파이썬 가공 파이프라인에서 정량 수치와 6개월 추이를 자동 분석하여 주입한 5문장 인사이트 텍스트를 `#comment-text` 문단 태그에 안전하게 바인딩하여 출력합니다.

---

## 5### 제품군별 매출 비중 (단일 도넛 차트 및 대칭 인출선 규격)
- **도넛 두께 및 마스크 반경**: 도넛 반지름을 `65px`, 두께(stroke-width)를 **`28px`**로 확대 렌더링하고, 안쪽 구멍 크기를 조율하기 위해 중앙 마스크 서클의 반지름을 **`51px`**로 설정합니다.
- **인출선 엇갈림 분기 및 이격**: FHD와 기타 매출(Others)처럼 11시~12시 영역에 밀집된 라벨의 겹침을 방지하기 위해, FHD는 **강제 좌측**(`isRight = false`), 기타 매출은 **강제 우측**(`isRight = true`)으로 인출선 방향을 엇갈리게 고정하고, 꺾임점 $y_2$ 및 텍스트 y좌표를 상단으로 **`12px`** 오프셋시켜 y축 상의 간격도 벌려줍니다.
- **상단 텍스트 잘림 방지 (Clipping Prevention)**: 지시선 이격으로 인해 텍스트 y좌표가 음수 영역으로 나가서 잘리는 문제를 차단하기 위해, 도넛의 Y축 중심(`cy`)을 반드시 **`110px 이상`** (viewBox 400x200 기준)으로 내려 상단 경계선(`y=0`)과의 안전 마진을 강제 확보해야 합니다.
 
### 제품군별 수익성 (수익성 매트릭스 Y축 격리 이격 및 눈금 정수화)
- **콤팩트 뷰포트 및 스크롤바 제거**: 가로 가둠 영역을 걷어내어 가로 스크롤바가 생기지 않도록 설정하고, SVG viewBox 너비를 **`600px`**, 높이를 **`240px`**로 설계하여 화면 크기에 최적화된 오목조목한 간격을 유치합니다.
- **막대 좌우 1cm 격리 여백**: 첫 번째 항목(OLED) 중심 X를 `95px`, 마지막 항목(기타 매출) 중심 X를 `505px`로 고정 분배하여, 각각 왼쪽 금액 축선(`x = 55`) 및 오른쪽 이익률 축선(`x = 545`) 간에 최소 **`24px (약 6.3mm)`** 이상의 충분한 1cm 상당 여백을 확보합니다.
- **Y축 텍스트 이격**: Y1(Sales 금액) 텍스트를 `x = 48` 에, Y2(COI%) 텍스트를 `x = 552` 에 각각 축선으로부터 완전히 바깥으로 격리(이격)하여 막대 그래프와 수치의 겹침을 원천 차단합니다.
- **5,000K$ 그리드 정수화**: Y1 금액 그리드 눈금은 최대값 `20,000K$` 기준 **`5,000K$ 간격`**(`0`, `5,000K$`, `10,000K$`, `15,000K$`, `20,000K$`)의 정수 단위로 렌더링합니다.
- **노이즈 컨트롤 및 요약 정리**: 불필요한 토글 스위치("기타 매출 제외 전사 COI%"), 가이드 텍스트 및 차트 바깥 하단의 부연 코멘트 단락을 전면 삭제하여 미니멀한 UI를 완성합니다.ine을 충분히 그릴 수 있도록 캔버스 너비를 **`400px`**로 확장합니다 (좌우 마진 70px씩 배정).
- **대칭 지시선 규칙**: 2025 YTD 막대의 비율 수치는 **왼쪽 방향**으로, 2026 YTD 막대의 비율 수치는 **오른쪽 방향**으로 지시선(connecting line)을 뽑아서 표시하여 글씨 겹침을 배제합니다. (비율이 1% 미만인 미미한 항목은 지시선을 생략합니다.)

### YTD 콤보 차트 단절 및 전체 노드 수치 표시 (``, ``)
- **Spacer를 이용한 이중 시계열 단절**: 연도별 YTD 누적 영역과 당해년도 월별 누적 영역 사이에 1칸의 빈 Spacer(공백)를 두고, MP% 및 COI% 꺾은선 그래프는 해당 Spacer 구간에서 연결되지 않고 끊어지도록 구현하여 성격이 다른 두 데이터 흐름을 안전하게 단절합니다.
- **전체 노드 라벨 표기 및 겹침 방지**: 모든 데이터 노드(Spacer 제외) 위에 MP% 및 COI% 수치 카드(말풍선)를 상시 표시하며, 두 꺾은선의 간격이 좁아 겹칠 가능성이 높은 경우 Y축 오프셋을 이격 조정(14px 아래 또는 18px 위)하여 수치 간 충돌을 방지합니다.

### 6 Core Summary KPI 요약 카드 세로 배치 규격
- MTD 당월 전년비 YoY 증감률과 YTD 누적/증감률이 가로 한 줄에 얽혀 가독성을 저해하는 것을 방지하기 위해, MTD YoY 지표는 첫째 줄에 굵고 크게 표시하고 YTD 누적/증감률은 줄바꿈하여 `text-[10px] text-slate-400 font-normal mt-1.5` 스타일로 서브 정렬합니다.

### 탭별 독립적 임플리케이션 동적 렌더링 (SPA)
- **동적 연동**: `switchTab` 동작 시 자바스크립트로 하단 `#comment-text` 영역에 들어갈 임플리케이션 텍스트를 활성화 탭(Pl Structure / Fundamental P&L / 기타 탭)에 따라 동적으로 변경 주입하여 탭 정보의 중복 및 불일치를 해소합니다.

### 단일 도넛 차트 및 대칭 인출선 규격
- **도넛 두께 및 마스크 반경**: 도넛 반지름을 `65px`, 두께(stroke-width)를 **`28px`**로 확대 렌더링하고, 안쪽 구멍 크기를 조율하기 위해 중앙 마스크 서클의 반지름을 **`51px`**로 설정합니다.
- **인출선 엇갈림 분기 및 이격**: FHD와 기타 매출(Others)처럼 11시~12시 영역에 밀집된 라벨의 겹침을 방지하기 위해, FHD는 **강제 좌측**(`isRight = false`), 기타 매출은 **강제 우측**(`isRight = true`)으로 인출선 방향을 엇갈리게 고정하고, 꺾임점 $y_2$ 및 텍스트 y좌표를 상단으로 **`12px`** 오프셋시켜 y축 상의 간격도 벌려줍니다.
- **상단 텍스트 잘림 방지 (Clipping Prevention)**: 지시선 이격으로 인해 텍스트 y좌표가 음수 영역으로 나가서 잘리는 문제를 차단하기 위해, 도넛의 Y축 중심(`cy`)을 반드시 **`110px 이상`** (viewBox 400x200 기준)으로 내려 상단 경계선(`y=0`)과의 안전 마진을 강제 확보해야 합니다.

### 수익성 매트릭스 Y축 격리 이격 및 눈금 정수화
- **콤팩트 뷰포트 및 스크롤바 제거**: 가로 가둠 영역을 걷어내어 가로 스크롤바가 생기지 않도록 설정하고, SVG viewBox 너비를 **`600px`**, 높이를 **`240px`**로 설계하여 화면 크기에 최적화된 오목조목한 간격을 유치합니다.
- **막대 좌우 1cm 격리 여백**: 첫 번째 항목(OLED) 중심 X를 `95px`, 마지막 항목(기타 매출) 중심 X를 `505px`로 고정 분배하여, 각각 왼쪽 금액 축선(`x = 55`) 및 오른쪽 이익률 축선(`x = 545`) 간에 최소 **`24px (약 6.3mm)`** 이상의 충분한 1cm 상당 여백을 확보합니다.
- **Y축 텍스트 이격**: Y1(Sales 금액) 텍스트를 `x = 48` 에, Y2(COI%) 텍스트를 `x = 552` 에 각각 축선으로부터 완전히 바깥으로 격리(이격)하여 막대 그래프와 수치의 겹침을 원천 방지합니다.
- **5,000K$ 그리드 정수화**: Y1 금액 그리드 눈금은 최대값 `20,000K$` 기준 **`5,000K$ 간격`**(`0`, `5,000K$`, `10,000K$`, `15,000K$`, `20,000K$`)의 정수 단위로 렌더링합니다.
- **Y축 콤보 차트 눈금 최적화**: 월별 및 YTD 콤보 차트의 왼쪽 금액 Y축 그리드 간격(`stepSales`)은 매출 최댓값이 큰 지점(예: 1,000K$를 대폭 상회하는 지점)에서는 기존 2,500K$에서 **10,000K$**(`10000000`)로 늘려서 텍스트 겹침을 미연에 방지합니다.
- **노이즈 컨트롤 및 요약 정리**: 불필요한 토글 스위치("기타 매출 제외 전사 COI%"), 가이드 텍스트 및 차트 바깥 하단의 부연 코멘트 단락을 전면 삭제하여 미니멀한 UI를 완성합니다.

### '기타 매출' 명칭 통일 규격 (Others 변경)
- UI 전반에서 회계적 결산 조정과 콘텐츠 매출 등이 혼재된 `'Others'` 항목을 **`'기타 매출'`**로 일관되게 표기합니다 (도넛 차트 툴팁/텍스트, 매트릭스 X축/설명 말풍선/하단 주석, Tie-out Table 행 헤더 등 전 부문에 전역 적용).

### MRGB 신규 제품군 추가 및 시각화 표준
- **분류 및 필터링 정합성**: NERP raw data K열 및 P열의 QNED와 MRGB 구분에 따라 `MRGB`를 독립 세그먼트로 추출하며, `UHD` 제품군 연산 시 QNED 뿐만 아니라 MRGB 제품군도 제외되도록 예외 필터식(`& (s['QNED'] != 'MRGB')`)을 강제해야 합니다.
- **MRGB 테마 색상**: 타사/기타 제품군과의 명확한 대조를 위해 **보라색/Indigo (`#4f46e5`, 반투명 버블 차트용: `rgba(79, 70, 229, 0.75)`)** 색상을 일관되게 부여합니다.
- **수익성 매트릭스 X축 고정폭 재배치**: 카테고리가 6개(`OLED`, `QNED`, `MRGB`, `UHD`, `FHD`, `기타 매출`)로 증가함에 따라 X축 고정 분배 수식을 `const getX = (i) => 95 + (i * 82)`로 변경 적용하여 축 레이블과 막대 그래프 사이의 격리 마진(24px 이상)을 유지하고 화면 잘림을 차단합니다.
- **월별 추이 필터 UI**: 차트 상단 제품군 필터 탭에 `MRGB` 버튼을 추가하여 단일 선택(Single-Selection) 방식 필터링 동작에 완벽히 호환되도록 구성합니다.


## 6. 시리즈별 / 모델별 / Account별 / Account별 상세 수익성 화면 및 UI 제어 규격

- **조회 기준 Toggle Switch**:
  - 각 화면별 조회 기준을 제어하는 YTD vs MTD 버튼 토글 스위치는 다음 스타일로 렌더링합니다 (아래 예시는 시리즈별 탭이며, 모델별/Account별/Account별 상세도 이와 동일한 CSS 스타일을 공유함):
    ```html
    <div class="inline-flex rounded-md shadow-sm text-xs">
        <button type="button" id="btn-series-ytd" class="bg-primary text-white px-3 py-1 rounded-l-md font-semibold focus:outline-none" onclick="setSeriesBasis('ytd')">YTD 누적 실적</button>
        <button type="button" id="btn-series-mtd" class="bg-white text-slate-700 border border-slate-300 border-l-0 px-3 py-1 rounded-r-md font-semibold hover:bg-slate-50 focus:outline-none" onclick="setSeriesBasis('mtd')">당월 실적</button>
    </div>
    ```
- **요약 행(Summary Row) Highlight 스타일링**:
  - 시리즈별 수익성 화면 및 Account별 상세 화면에서 요약 행(`row_type === 'summary'` 또는 '합계' 행) 렌더링 시, 짝수행 스타일(`tr:nth-child(even)`)과의 충돌을 방지하기 위해 `tr.setAttribute('style', ...)` 인터페이스를 통해 직접 인라인 스타일을 주입합니다:
    - 배경색: `#e2e8f0 !important` (slate-200)
    - 굵기: `font-weight: bold`
    - 테두리: `border-top: 2px solid #94a3b8; border-bottom: 2px solid #94a3b8;` (slate-400)
  - 모델별 수익성 및 Account별 수익성은 별도의 요약 행이나 종합 합계 행 없이 심플한 순위 리스트로 렌더링하며, 모델별 수익성은 판매량이 0인 모델을 리스트에서 제외합니다.
- **Account별 상세 (account_detail) 전용 제어 및 렌더링 규칙**:
  - **유통 채널 선택**: 체크박스를 지양하고 가로 flex-wrap 형태의 목록으로 노출하며, 선택된 항목에 대해 굵은 글씨와 2px 두께의 밑줄(`text-primary font-bold border-b-2 border-primary pb-1`)을 적용하고 비선택 항목은 연회색(`text-slate-500 hover:text-slate-800 font-medium`)으로 처리합니다. YTD 누적 매출이 없는 채널은 필터링하여 제외합니다.
  - **전체 TV 수익성 우선 노출 (Overall TV Summary)**: 시리즈별 수익성 테이블 바로 위에 전체 TV 수익성을 요약하여 볼 수 있도록 'TV 수익성 실적' 테이블을 고정 렌더링합니다. 이 테이블에는 Y26 실적, Y25 실적, 그리고 Grand Total(합계) 행을 포함합니다.
  - **모델 리스트 30개 제한**: 모델별 수익성 테이블 렌더링 시 해당 채널의 모델 중 판매량이 0인 항목을 제외하고, Net Sales 기준 내림차순 정렬한 뒤 상위 30개만 잘라서 렌더링합니다.
- **공통 컴포넌트 숨김/노출 제어**:
  - `switchTab(tabId)` 내에서 특정 탭의 전용 뷰 형태를 위해 공통 컴포넌트의 노출 여부를 동적으로 제어해야 합니다.
    - KPI 그리드(`#kpi-grid`): `pl_structure`, `pnl_detail`, `blu_model`, `model_series`, `account`, `account_detail` 탭에서 숨김(`display: none`), 그 외 탭에서 노출(`display: grid`).
    - 임플리케이션 슬롯(`#comment-slot`): `blu_model`, `model_series`, `account`, `account_detail` 탭에서 숨김(`display: none`), 그 외 탭에서 노출(`display: block`).

---

## 7. 업데이트 메타데이터 동적 동기화 규칙 (Updated Date & Report Month)

보고서 빌드 시 하드코딩된 메타데이터로 인해 구버전 정보가 렌더링되는 오류를 차단하기 위해 다음 동적 갱신 규칙을 준수해야 합니다:

- **수정일(Updated Date) 자동화**: 대시보드 리포트 생성 및 저장 시, 템플릿의 하드코딩된 작성 날짜를 실제 저장/수정 날짜(예: `2026년 08월 12일`)로 치환하여 `Updated Date` 영역을 갱신합니다.
- **보고월(Report Month) 자동 동기화**: 대시보드 우측 상단 `Report Month` 영역의 하드코딩 초깃값(`2026.05` 등)을 실제 엑셀 원천 데이터의 최신 실적 결산월(예: `2026.07`)로 치환하여 `id="top-bar-month"` innerText 렌더링 전에 동시 매치시킵니다.

---

## 8. Price Tracker 대시보드 가격 비교 팝업 및 지표 표준 (Price History Popup)

유통 가격 모니터링을 위한 가격 비교 대시보드(Price Tracker)에서 모델명 클릭 시 가격 변화 추이를 시각화할 때 준수해야 하는 기준은 다음과 같습니다:

- **차트 클릭 및 X축 이벤트 연동**: 1:1 비교 막대 차트의 막대를 클릭할 때 뿐만 아니라 막대 하단의 X축 텍스트 라벨 영역을 클릭할 때도 꺾은선 팝업 모달이 노출되도록 Chart.js 옵션의 `onClick` 마우스 x좌표 비율 보정을 구현합니다.
- **국가별 통화 기호 동적 포맷팅**: 꺾은선 차트의 Y축 및 데이터 레이블은 국가별 통화 매핑 정보(`countryCurrencies`, `currencySymbols`)와 `formatCurrency(val)` 함수를 호출하여 CHF, EUR, GBP, SEK 등 각 유통 국가의 공식 화폐 단위를 동적으로 렌더링해야 합니다.
- **LG 포인트 툴팁 내 ATA 지표**: 가격 추이 꺾은선 차트에서 엘지(LG) 제품의 데이터 포인트에 마우스 호버 시 출력되는 툴팁 내에 엘지와 삼성의 가격비인 **`ATA: (엘지제품가격/삼성제품가격 * 100)`** 값을 연산하여 다음 줄에 출력합니다. 이때 ATA 비율은 단독 수치(예: `ATA: 113`)로 기재하며 퍼센트(`%`) 단위 기호는 표기하지 않습니다.

