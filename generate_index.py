# -*- coding: utf-8 -*-
import os
import re
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
countries_info = {
    'AG': {'name': 'Austria (오스트리아)', 'code': 'AG', 'path': './법인별/01. AG/AG_TV_Profitability_Report.html', 'id': 'austria'},
    'BN': {'name': 'Benelux (베네룩스)', 'code': 'BN', 'path': './법인별/02. BN/BN_TV_Profitability_Report.html', 'id': 'benelux'},
    'CK': {'name': 'Czech (체코)', 'code': 'CK', 'path': './법인별/03. CK/CK_TV_Profitability_Report.html', 'id': 'czech'},
    'Swiss': {'name': 'Switzerland (스위스)', 'code': 'Swiss', 'path': './법인별/05. Swiss/Swiss_TV_Profitability_Report.html', 'id': 'swiss'},
    'ES': {'name': 'Spain (스페인)', 'code': 'ES', 'path': './법인별/06. ES/ES_TV_Profitability_Report.html', 'id': 'spain'},
    'FS': {'name': 'France (프랑스)', 'code': 'FS', 'path': './법인별/07. FS/FS_TV_Profitability_Report.html', 'id': 'france'},
    'HS': {'name': 'Greece (그리스)', 'code': 'HS', 'path': './법인별/08. HS/HS_TV_Profitability_Report.html', 'id': 'greece'},
    'IS': {'name': 'Italy (이탈리아)', 'code': 'IS', 'path': './법인별/09. IS/IS_TV_Profitability_Report.html', 'id': 'italy'},
    'LA': {'name': 'Latvia (라트비아)', 'code': 'LA', 'path': './법인별/10. LA/LA_TV_Profitability_Report.html', 'id': 'latvia'},
    'MK': {'name': 'Hungary (헝가리)', 'code': 'MK', 'path': './법인별/11. MK/MK_TV_Profitability_Report.html', 'id': 'hungary'},
    'PL': {'name': 'Poland (폴란드)', 'code': 'PL', 'path': './법인별/12. PL/PL_TV_Profitability_Report.html', 'id': 'poland'},
    'PT': {'name': 'Portugal (포르투갈)', 'code': 'PT', 'path': './법인별/13. PT/PT_TV_Profitability_Report.html', 'id': 'portugal'},
    'RO': {'name': 'Romania (루마니아)', 'code': 'RO', 'path': './법인별/14. RO/RO_TV_Profitability_Report.html', 'id': 'romania'},
    'SW': {'name': 'Sweden (스웨덴)', 'code': 'SW', 'path': './법인별/15. SW/SW_TV_Profitability_Report.html', 'id': 'sweden'},
    'UK': {'name': 'United Kingdom (영국)', 'code': 'UK', 'path': './법인별/16. UK/UK_TV_Profitability_Report.html', 'id': 'uk'}
}

data_by_country = {}
latest_report_month_str = ""

for code, info in countries_info.items():
    file_path = os.path.join(base_dir, info['path'].replace('./', ''))
    print(f"Reading data for {info['name']} from {file_path}...")
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist!")
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    match = re.search(r'<script id="dashboard-data" type="application/json">\s*(.*?)\s*</script>', html, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        latest_year = data['LATEST_YEAR']
        latest_month = data['LATEST_MONTH']
        cur_month_str = f"{latest_year}.{latest_month:02d}"
        if not latest_report_month_str or cur_month_str > latest_report_month_str:
            latest_report_month_str = cur_month_str
        
        kpi = data['DATA']['standard']['kpi']['ytd']
        data_by_country[code] = {
            'year': latest_year,
            'month': latest_month,
            'qty': kpi['qty'],
            'qty_yoy': kpi['qty_yoy'],
            'sales': kpi['sales'],
            'sales_yoy': kpi['sales_yoy'],
            'mp': kpi.get('mp', 0.0),
            'mp_yoy': kpi.get('mp_yoy', None),
            'coi': kpi['coi'],
            'coi_yoy': kpi['coi_yoy']
        }
        print(f"Loaded: Sales={kpi['sales']/1000000:.1f}M$, COI={kpi['coi']*100:.1f}%, MP={kpi.get('mp',0.0)*100:.1f}%")
    else:
        print(f"Error parsing json in {file_path}")

# Build index.html
html_template = f"""<!DOCTYPE html>
<html class="light" lang="ko">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>Executive Portal | LGE Europe TV P&L Dashboard</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&amp;family=Noto+Sans+KR:wght@300;400;500;700&amp;display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
    <script id="tailwind-config">
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    "colors": {{
                        "primary": "#051c2c",
                        "on-primary": "#ffffff",
                        "secondary": "#a50034",
                        "surface": "#f6faff",
                        "surface-variant": "#ebf5ff",
                        "outline": "#73777d",
                        "outline-variant": "#c3c7cc",
                        "error": "#e11d48",
                        "background": "#ffffff",
                        "primary-hover": "#860027",
                        "teal-accent": "#00a3a3",
                        "crimson-accent": "#e11d48"
                    }},
                    "borderRadius": {{
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem"
                    }},
                    "fontFamily": {{
                        "headline": ["\\"Source Serif 4\\"", "serif"],
                        "body": ["Inter", "Noto Sans KR", "sans-serif"]
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ font-family: 'Inter', 'Noto Sans KR', sans-serif; background-color: #f6faff; color: #051c2c; }}
        h1, h2, h3, h4, h5, h6 {{ font-family: 'Source Serif 4', serif; }}
        .sidebar-item.active {{ background-color: rgba(255, 255, 255, 0.1); border-right: 4px solid #ffffff; }}
        .sub-link.active {{ color: #ffffff !important; font-weight: 600; }}
        .country-node.active > button {{ background-color: rgba(255, 255, 255, 0.05); color: #ffffff; }}
    </style>
</head>
<body class="flex min-h-screen">
    <!-- Sidebar Navigation -->
    <aside class="w-72 bg-primary text-white fixed h-screen flex flex-col z-50 shadow-lg">
        <div class="p-8 border-b border-white/10 flex-shrink-0">
            <div class="flex items-center gap-2 mb-2">
                <span class="material-symbols-outlined text-white/80">insights</span>
                <h1 class="text-xl font-bold tracking-tight">TV P&L Portal</h1>
            </div>
            <p class="text-[10px] text-white/50 uppercase tracking-[0.2em] font-medium">LGE Europe TV Portal</p>
        </div>
        
        <nav class="flex-1 py-6 space-y-1 overflow-y-auto" id="sidebar-nav">
            <div class="px-4 pb-4">
                <button class="sidebar-item active w-full flex items-center gap-4 px-6 py-3.5 rounded transition-all hover:bg-white/5 text-left" id="btn_summary" onclick="showHome()">
                    <span class="material-symbols-outlined text-sm opacity-50">home</span>
                    <span class="font-medium text-sm">대시보드 포털 홈</span>
                </button>
            </div>
            
            <div class="px-8 py-2 text-[10px] font-bold text-white/40 uppercase tracking-widest">Regional Dashboards</div>
"""

# Dynamic Submenus Generation
for code, info in countries_info.items():
    country_id = info['id']
    code_badge = info['code']
    name = info['name']
    path = info['path']
    
    html_template += f"""
        <!-- {name} -->
        <div class="country-node px-4" id="node-{country_id}">
            <button class="w-full flex items-center justify-between px-4 py-3 rounded text-left text-white/70 hover:text-white hover:bg-white/5 transition-all group" onclick="toggleSubmenu('{country_id}')">
                <span class="flex items-center gap-3 text-xs font-medium">
                    <span class="text-[9px] font-mono font-bold bg-white/10 text-white/80 px-1.5 py-0.5 rounded border border-white/10 uppercase tracking-wider">{code_badge}</span>
                    <span>{name}</span>
                </span>
                <span class="material-symbols-outlined text-xs opacity-50 transition-transform" id="arrow-{country_id}">expand_more</span>
            </button>
            <div class="sub-menu flex-col pl-9 mt-1 space-y-1 pb-2 border-l border-white/10 ml-6" id="sub-{country_id}" style="display: none;">
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'current_month_pnl', this); return false;">Ⅰ. 당월 손익 실적</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'pl_structure', this); return false;">Ⅱ. 구조적 손익 추이</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'fundamental_structure', this); return false;">Ⅲ. Fundamental 손익</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'pnl_detail', this); return false;">Ⅳ. 수익성 상세 분석</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'blu_model', this); return false;">Ⅴ. 시리즈별 수익성</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'model_series', this); return false;">Ⅵ. 모델별 수익성</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'account', this); return false;">Ⅶ. Account별 수익성</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'account_detail', this); return false;">Ⅷ. Account별 상세 수익성</a>
                <a href="#" class="sub-link block px-3 py-1.5 text-[11px] text-white/40 hover:text-white rounded hover:bg-white/5 transition-all" onclick="showReport('{name}', '{path}', 'sales_deduction', this); return false;">Ⅸ. Sales Deduction 분석</a>
            </div>
        </div>
    """

# Standard Footer and Main Layout
html_template += f"""
        </nav>
        
        <div class="p-8 border-t border-white/10 bg-black/10 flex flex-col gap-1 text-[10px] text-white/40 font-sans tracking-tight leading-relaxed flex-shrink-0">
            <p class="font-bold text-white/50 text-[11px] mb-1">System Admin</p>
            <p class="text-white/60">Harry Park</p>
            <p><a href="mailto:harry.park@lge.com" class="hover:text-primary text-white/50 underline decoration-white/20 transition-all">harry.park@lge.com</a></p>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="ml-72 flex-1 flex flex-col min-h-screen">
        <!-- Top Bar Header -->
        <header class="h-20 bg-white border-b border-slate-200 flex items-center justify-between px-12 sticky top-0 z-40">
            <div class="flex items-center gap-6">
                <span class="text-xs font-bold tracking-widest text-slate-400 uppercase">Europe TV P&L Portal</span>
                <div class="h-4 w-px bg-slate-200"></div>
                <p class="text-sm font-semibold text-primary" id="page-indicator">대시보드 포털 홈</p>
            </div>
            <div class="flex items-center gap-6">
                <div class="text-right">
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Report Month</p>
                    <p class="text-sm font-bold text-primary" id="report-month-indicator">{latest_report_month_str}</p>
                </div>
                <div class="h-8 w-px bg-slate-200"></div>
                <button class="items-center gap-2 text-xs font-bold border border-slate-200 rounded px-4 py-2 hover:bg-slate-50 transition-all cursor-pointer" id="btn-back-home" style="display: none;" onclick="showHome()">
                    <span class="material-symbols-outlined text-xs">arrow_back</span> 포털 홈으로
                </button>
            </div>
        </header>

        <!-- View Container -->
        <div class="flex-1 flex flex-col relative overflow-y-auto">
            
            <!-- Home Grid View -->
            <div class="px-6 py-8 max-w-[95%] mx-auto w-full flex-1" id="home-view-container">
                <!-- Welcome Banner -->
                <div class="bg-primary text-white p-8 rounded-lg shadow-md mb-12 relative overflow-hidden">
                    <div class="relative z-10">
                        <h2 class="text-3xl font-headline font-bold mb-3">유럽 TV 결산 손익 관리 포털</h2>
                        <p class="text-xs text-white/70 leading-relaxed max-w-6xl">본 포털은 유럽 주요 지사 및 지점의 TV 사업 P&L 결산 실적(Standard & Fundamental)을 종합 모니터링하기 위한 통합 인덱스 포털입니다. 아래 각 지점별 카드 또는 좌측 사이드바 메뉴에서 특정 법인을 선택하시면 상세 손익 분석 데이터와 다개년 Waterfall Bridge 차트, 제품군별 수익성 매트릭스를 인터랙티브하게 조회하실 수 있습니다.</p>
                    </div>
                    <div class="absolute -right-24 -bottom-24 w-80 h-80 bg-white/5 rounded-full blur-2xl pointer-events-none"></div>
                </div>

                <div class="flex items-center gap-4 mb-8">
                    <span class="h-6 w-1 bg-secondary"></span>
                    <h3 class="text-2xl font-headline font-bold text-primary">지점/법인별 YTD 손익 실적 요약</h3>
                </div>

                <!-- Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
"""

# Country Grid Cards Generation
for code, info in countries_info.items():
    country_id = info['id']
    code_badge = info['code']
    name = info['name']
    path = info['path']
    
    if code not in data_by_country:
        continue
        
    cdata = data_by_country[code]
    
    # Format values
    sales_val = cdata['sales']
    coi_val = cdata['coi']
    mp_val = cdata['mp']
    
    # Format YoY and Indicator
    sales_yoy = cdata['sales_yoy']
    coi_yoy = cdata['coi_yoy']
    mp_yoy = cdata['mp_yoy']
    
    # Sales YoY formatting (%)
    if sales_yoy is not None:
        sign_s = "▲" if sales_yoy >= 0 else "▼"
        color_s = "text-teal-accent" if sales_yoy >= 0 else "text-crimson-accent"
        sales_yoy_str = f"{sign_s} {abs(sales_yoy)*100:.1f}%"
    else:
        color_s = "text-slate-400"
        sales_yoy_str = "-"
        
    # COI YoY formatting (percentage points)
    if coi_yoy is not None:
        sign_c = "▲" if coi_yoy >= 0 else "▼"
        color_c = "text-teal-accent" if coi_yoy >= 0 else "text-crimson-accent"
        coi_yoy_str = f"{sign_c} {abs(coi_yoy)*100:.1f}%p"
    else:
        color_c = "text-slate-400"
        coi_yoy_str = "-"

    # MP YoY formatting (percentage points)
    if mp_yoy is not None:
        sign_m = "▲" if mp_yoy >= 0 else "▼"
        color_m = "text-teal-accent" if mp_yoy >= 0 else "text-crimson-accent"
        mp_yoy_str = f"{sign_m} {abs(mp_yoy)*100:.1f}%p"
    else:
        color_m = "text-slate-400"
        mp_yoy_str = "-"
        
    # Format calculated metrics
    coi_pct = coi_val * 100
    mp_pct = mp_val * 100
    sales_mil_str = f"{sales_val / 1000000:.1f}M$"
    
    # Status Badge
    if coi_pct >= 5.0:
        status_badge = '<span class="status-badge text-[10px] font-bold px-2 py-0.5 rounded border bg-green-50 text-green-700 border-green-200">✓ Healthy</span>'
        border_color = 'border-l-teal-accent'
    elif 0.0 <= coi_pct < 5.0:
        status_badge = '<span class="status-badge text-[10px] font-bold px-2 py-0.5 rounded border bg-amber-50 text-amber-700 border-amber-200">⚠ Warning</span>'
        border_color = 'border-l-amber-500'
    else:
        status_badge = '<span class="status-badge text-[10px] font-bold px-2 py-0.5 rounded border bg-red-50 text-red-700 border-red-200">✗ Critical</span>'
        border_color = 'border-l-crimson-accent'

    html_template += f"""
                <!-- {name} -->
                <div class="bg-white border border-slate-200 p-8 rounded-lg hover:shadow-lg transition-all border-l-4 {border_color} cursor-pointer" onclick="showReport('{name}', '{path}', 'current_month_pnl', document.querySelector('#node-{country_id} .sub-link:nth-child(1)')); toggleSubmenu('{country_id}');">
                    <div class="flex justify-between items-center mb-4">
                        <div class="flex items-center gap-3">
                            <span class="text-[10px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-1 rounded border border-slate-200 uppercase tracking-wider">{code_badge}</span>
                            <span class="text-lg font-headline font-bold text-primary">{name}</span>
                        </div>
                        {status_badge}
                    </div>
                    <p class="text-xs text-slate-500 leading-relaxed mb-6 h-12 overflow-hidden">
                        2026년 {cdata['month']:02d}월 YTD 누적 기준 Net Sales {sales_mil_str} (전년비 {sales_yoy_str}), 영업이익률(COI%)은 {coi_pct:.1f}% (전년비 {coi_yoy_str}), 한계이익률(MP%)은 {mp_pct:.1f}% (전년비 {mp_yoy_str})를 기록하였습니다.
                    </p>
                    
                    <div class="grid grid-cols-3 gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100 mb-6">
                        <div class="flex flex-col items-center justify-center text-center">
                            <span class="text-[9px] text-slate-400 uppercase font-bold">누적 Net Sales</span>
                            <span class="text-sm font-bold text-primary my-1">{sales_mil_str}</span>
                            <span class="text-[9px] {color_s} font-bold">{sales_yoy_str}</span>
                        </div>
                        <div class="flex flex-col items-center justify-center text-center border-x border-slate-200">
                            <span class="text-[9px] text-slate-400 uppercase font-bold">누적 영업이익률</span>
                            <span class="text-sm font-bold text-primary my-1">{coi_pct:.1f}%</span>
                            <span class="text-[9px] {color_c} font-bold">{coi_yoy_str}</span>
                        </div>
                        <div class="flex flex-col items-center justify-center text-center">
                            <span class="text-[9px] text-slate-400 uppercase font-bold">누적 한계이익률</span>
                            <span class="text-sm font-bold text-primary my-1">{mp_pct:.1f}%</span>
                            <span class="text-[9px] {color_m} font-bold">{mp_yoy_str}</span>
                        </div>
                    </div>

                    <div class="flex gap-4">
                        <button class="flex-1 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold py-2.5 rounded transition-all flex items-center justify-center gap-2" onclick="event.stopPropagation(); showReport('{name}', '{path}', 'current_month_pnl', document.querySelector('#node-{country_id} .sub-link:nth-child(1)')); toggleSubmenu('{country_id}');">당월 손익</button>
                        <button class="flex-1 bg-secondary hover:bg-primary-hover text-white text-xs font-semibold py-2.5 rounded transition-all flex items-center justify-center gap-2" onclick="event.stopPropagation(); showReport('{name}', '{path}', 'pl_structure', document.querySelector('#node-{country_id} .sub-link:nth-child(2)')); toggleSubmenu('{country_id}');">수익성 상세</button>
                    </div>
                </div>
    """

# Wrap up HTML template
html_template += """
                </div>
            </div>

            <!-- Report View Iframe -->
            <div class="w-full flex-1" id="report-view-container" style="display: none; height: calc(100vh - 80px);">
                <iframe id="report-iframe" class="w-full h-full border-none" src=""></iframe>
            </div>

        </div>
    </main>

    <!-- Navigation Script -->
    <script>
        let currentPath = '';
        let currentIframeBaseUrl = '';
        let justShownReport = false;

        function showHome() {
            const home = document.getElementById('home-view-container');
            const report = document.getElementById('report-view-container');
            const btnBack = document.getElementById('btn-back-home');

            home.classList.remove('hidden');
            home.style.display = 'block';
            
            report.classList.add('hidden');
            report.style.display = 'none';

            btnBack.classList.add('hidden');
            btnBack.style.display = 'none';

            document.getElementById('page-indicator').innerText = '대시보드 포털 홈';
            
            // Sidebar reset
            document.querySelectorAll('.sidebar-item').forEach(item => item.classList.remove('active'));
            document.getElementById('btn_summary').classList.add('active');
            
            document.querySelectorAll('.country-node').forEach(node => node.classList.remove('active'));
            document.querySelectorAll('.sub-menu').forEach(menu => {
                menu.classList.add('hidden');
                menu.style.display = 'none';
            });
            document.querySelectorAll('.sub-link').forEach(link => link.classList.remove('active'));
            
            // Reset all arrow indicators to 0deg rotation
            document.querySelectorAll('.country-node span[id^="arrow-"]').forEach(arrow => {
                arrow.style.transform = 'rotate(0deg)';
            });
            
            currentPath = '';
            currentIframeBaseUrl = '';
        }

        function toggleSubmenu(countryId) {
            if (justShownReport) return;
            document.querySelectorAll('.sub-menu').forEach(menu => {
                if (menu.id === 'sub-' + countryId) {
                    const isDisplayed = menu.style.display === 'flex' || (!menu.classList.contains('hidden') && getComputedStyle(menu).display !== 'none');
                    if (isDisplayed) {
                        menu.classList.add('hidden');
                        menu.style.display = 'none';
                        document.getElementById('arrow-' + countryId).style.transform = 'rotate(0deg)';
                    } else {
                        menu.classList.remove('hidden');
                        menu.style.display = 'flex';
                        document.getElementById('arrow-' + countryId).style.transform = 'rotate(180deg)';
                    }
                } else {
                    menu.classList.add('hidden');
                    menu.style.display = 'none';
                    const otherId = menu.id.replace('sub-', '');
                    const otherArrow = document.getElementById('arrow-' + otherId);
                    if (otherArrow) otherArrow.style.transform = 'rotate(0deg)';
                }
            });
        }

        function showReport(name, path, tabName, element) {
            justShownReport = true;
            setTimeout(() => { justShownReport = false; }, 0);

            const home = document.getElementById('home-view-container');
            const report = document.getElementById('report-view-container');
            const btnBack = document.getElementById('btn-back-home');

            home.classList.add('hidden');
            home.style.display = 'none';

            report.classList.remove('hidden');
            report.style.display = 'block';

            btnBack.classList.remove('hidden');
            btnBack.style.display = 'flex';

            document.getElementById('page-indicator').innerText = name + ' TV 리포트';
            
            const iframe = document.getElementById('report-iframe');
            const tabHash = '#route_' + tabName;
            
            if (currentPath !== path) {
                currentPath = path;
                const separator = path.includes('?') ? '&' : '?';
                const cacheBuster = 'cb=' + Date.now();
                currentIframeBaseUrl = path + separator + cacheBuster;
                iframe.src = currentIframeBaseUrl + tabHash;
            } else {
                try {
                    if (iframe.contentWindow) {
                        iframe.contentWindow.location.hash = tabHash;
                    } else {
                        iframe.src = currentIframeBaseUrl + tabHash;
                    }
                } catch(e) {
                    iframe.src = currentIframeBaseUrl + tabHash;
                }
            }
            
            // Sidebar active highlights
            document.querySelectorAll('.sidebar-item').forEach(item => item.classList.remove('active'));
            document.querySelectorAll('.country-node').forEach(node => node.classList.remove('active'));
            document.querySelectorAll('.sub-link').forEach(link => link.classList.remove('active'));
            
            if (element) {
                const parentNode = element.closest('.country-node');
                if (parentNode) {
                    parentNode.classList.add('active');
                    
                    // Collapse all other submenus first
                    document.querySelectorAll('.sub-menu').forEach(menu => {
                        if (menu !== parentNode.querySelector('.sub-menu')) {
                            menu.style.display = 'none';
                            const otherId = menu.id.replace('sub-', '');
                            const arrow = document.getElementById('arrow-' + otherId);
                            if (arrow) arrow.style.transform = 'rotate(0deg)';
                        }
                    });

                    const menu = parentNode.querySelector('.sub-menu');
                    if (menu) {
                        menu.classList.remove('hidden');
                        menu.style.display = 'flex';
                        const countryId = parentNode.id.replace('node-', '');
                        const arrow = document.getElementById('arrow-' + countryId);
                        if (arrow) arrow.style.transform = 'rotate(180deg)';
                    }
                }
                element.classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

# Write the final index.html
output_file = os.path.join(base_dir, "index.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Index HTML compiled successfully: {output_file}")
