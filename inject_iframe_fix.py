# -*- coding: utf-8 -*-
import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
branches = ['01. AG', '02. BN', '03. CK', '05. Swiss', '08. HS', '10. LA', '16. UK']

target_files = []
# Collect templates and compiled reports
for b in branches:
    template_path = os.path.join(base_dir, '법인별', b, 'report_template.html')
    if os.path.exists(template_path):
        target_files.append(template_path)
        
    for f in os.listdir(os.path.join(base_dir, '법인별', b)):
        if f.endswith('_TV_Profitability_Report.html'):
            target_files.append(os.path.join(base_dir, '법인별', b, f))

print(f"Target files to update: {len(target_files)}")

for file_path in target_files:
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Inject iframe check in <head> if not already there
    # If there is already an iframe style helper, remove or skip it. Let's make sure it's clean.
    # We will search for '<script id="iframe-helper">' or standard style check.
    if 'if (window.self !== window.top)' not in content:
        iframe_style_script = """<head>
<script>
    if (window.self !== window.top) {
        const style = document.createElement('style');
        style.textContent = `
            aside { display: none !important; }
            main { margin-left: 0 !important; }
            header { display: none !important; }
        `;
        document.head.appendChild(style);
    }
</script>"""
        content = content.replace("<head>", iframe_style_script, 1)
    else:
        # If it is there, let's verify if it contains 'header { display: none !important; }'
        if 'header { display: none !important; }' not in content:
            # Update the style replacement
            content = content.replace('main { margin-left: 0 !important; }', 'main { margin-left: 0 !important; }\n            header { display: none !important; }')

    # 2. Inject scroll reset in switchTab function
    # Use regex to find function switchTab(tabId) { ... currentTab = tabId;
    # Ensure window.scrollTo(0, 0); is called at the top of switchTab.
    if 'window.scrollTo(0, 0);' not in content:
        content = re.sub(
            r'function switchTab\(tabId\)\s*\{\s*currentTab\s*=\s*tabId;',
            'function switchTab(tabId) {\n        window.scrollTo(0, 0);\n        currentTab = tabId;',
            content
        )

    # 3. Clean up old DOMContentLoaded routing block and replace with the route-based hash routing
    # We will replace any DOMContentLoaded and hashchange listeners that we created earlier
    # Let's search for old_dom_content or any hash-routing block
    # A generic way is to look for window.addEventListener('DOMContentLoaded', ...) that references location.hash
    # We will replace it with the new #route_ namespace router.
    
    # First, let's remove any previous DOMContentLoaded/hashchange scripts that we added
    pattern_to_remove = r"window\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{\s*const hash = window\.location\.hash;.*?\}\);\s*window\.addEventListener\('hashchange',\s*\(\)\s*=>\s*\{.*?\}\);"
    content = re.sub(pattern_to_remove, '', content, flags=re.DOTALL)
    
    # Also clean up basic DOMContentLoaded listener if it exists
    content = re.sub(r"window\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{\s*switchTab\('current_month_pnl'\);\s*\}\);", '', content)

    # Now append the new clean routing code just before </script> at the end of the file
    new_routing_code = """    window.addEventListener('DOMContentLoaded', () => {
        const hash = window.location.hash;
        let defaultTab = 'current_month_pnl';
        if (hash) {
            defaultTab = hash.replace('#route_', '').replace('#tab_', '').replace('#', '');
        }
        switchTab(defaultTab);
    });

    window.addEventListener('hashchange', () => {
        const hash = window.location.hash;
        if (hash) {
            const tabId = hash.replace('#route_', '').replace('#tab_', '').replace('#', '');
            switchTab(tabId);
        }
    });
</script>"""
    
    # Replace the last </script> with our routing block and </script>
    # We find the last occurrences of </script>
    if 'hashchange' not in content:
        # Replace the last </script> in the file
        parts = content.rsplit('</script>', 1)
        if len(parts) == 2:
            content = parts[0] + new_routing_code + parts[1]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("All sub-reports and templates updated successfully.")
