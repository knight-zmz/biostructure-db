#!/usr/bin/env python3
"""
Fix README.md public-facing drift (online demo links, HTTPS claims, table counts).

Minimal fix for external reader confusion.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
README_PATH = BASE_DIR / "README.md"

def main():
    result = {
        "handler": "fix_readme_public_drift",
        "status": "success",
        "changes": []
    }
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        readme = f.read()
    original = readme
    
    # Fix 1: Online demo link (domain paused, use IP)
    readme = readme.replace(
        '**🌐 在线演示**: [https://jlupdb.me](https://jlupdb.me)',
        '**🌐 在线演示**: http://101.200.53.98 (IP 直连，域名备案期间暂停)'
    )
    if readme != original:
        result['changes'].append('Fixed online demo link (jlupdb.me → IP direct)')
    original = readme
    
    # Fix 2: API link
    readme = readme.replace(
        '**📊 API**: [https://jlupdb.me/api/stats](https://jlupdb.me/api/stats)',
        '**📊 API**: http://101.200.53.98/api/stats (IP 直连)'
    )
    if readme != original:
        result['changes'].append('Fixed API link (jlupdb.me → IP direct)')
    original = readme
    
    # Fix 3: HTTPS auto-renewal claim
    readme = readme.replace(
        '🔄 **自动部署**: GitHub Actions + HTTPS 自动续期',
        '🔄 **自动部署**: GitHub Actions (HTTP 模式，备案完成后恢复 HTTPS)'
    )
    if readme != original:
        result['changes'].append('Fixed deployment description (HTTPS paused)')
    original = readme
    
    # Fix 4: Table count (verify from schema)
    readme = readme.replace('💾 **PostgreSQL**: 18 个数据表', '💾 **PostgreSQL**: 15 个核心数据表')
    readme = readme.replace('| **数据表** | 18 |', '| **数据表** | 15 |')
    if readme != original:
        result['changes'].append('Fixed table count (18 → 15)')
    
    # Write
    if readme != open(README_PATH, 'r').read():
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme)
        result['message'] = f'README.md updated: {len(result["changes"])} changes'
    else:
        result['status'] = 'no_changes_needed'
        result['message'] = 'README.md already up to date'
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
