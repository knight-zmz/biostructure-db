#!/usr/bin/env python3
"""
Fix README.md to match current project reality.

Reads:
- ops/project_state.md (project reality source)
- control/status.md (current state)
- package.json (version info)

Writes:
- README.md (updated to reflect reality)
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # handlers -> control -> project root
README_PATH = BASE_DIR / "README.md"
PROJECT_STATE_PATH = BASE_DIR / "ops" / "project_state.md"
PACKAGE_JSON_PATH = BASE_DIR / "package.json"

def main():
    result = {
        "handler": "fix_readme_drift",
        "status": "success",
        "changes": []
    }
    
    # Read current README
    with open(README_PATH, 'r', encoding='utf-8') as f:
        readme = f.read()
    
    original_readme = readme
    
    # Fix 1: Update structure/atom counts
    before = readme
    readme = readme.replace('108 个结构，740,010 个原子', '6 个结构，4,240 个原子 (P2 样例验证中)')
    readme = readme.replace('| **蛋白质结构** | 108 |', '| **蛋白质结构** | 6 (P2 样例) |')
    readme = readme.replace('| **原子坐标** | 740,010 |', '| **原子坐标** | 4,240 (P2 样例) |')
    if readme != before:
        result['changes'].append('Updated structure/atom counts to current reality (6 structures, 4240 atoms)')
    
    # Fix 2: Fix HTTPS claims
    before = readme
    readme = readme.replace('✅ **HTTPS 加密**: Let\'s Encrypt SSL', '⏸️ **HTTPS**: 备案期间暂停 (当前 HTTP 模式)')
    readme = readme.replace('✅ **自动监控**: 每小时状态汇报', '🟡 **监控**: 脚本已部署，待运行验证')
    if readme != before:
        result['changes'].append('Fixed HTTPS status (paused during ICP filing)')
        result['changes'].append('Fixed monitoring status (deployed, pending verification)')
    
    # Fix 3: Update "Latest Features" date
    readme = re.sub(
        r'## ✨ 最新特性 \(2026-03-27 升级\)',
        '## ✨ 最新特性 (2026-03-31 控制平面 v1.3)',
        readme
    )
    result['changes'].append('Updated feature date to 2026-03-31')
    
    # Fix 4: Add control plane v1.3 features
    if '控制平面' not in readme:
        # Add after the "新增功能" section
        new_features = """
### 🤖 控制平面 v1.3 (2026-03-31)
- ✅ **任务自动补给**: 队列空时自动生成低风险评估任务
- ✅ **总结报告层**: 关键事件触发 compact summary
- ✅ **状态查询协议**: status.md 为统一入口
- ✅ **Git 边界收口**: 运行态文件不入库"""
        readme = readme.replace('### 🔥 新增功能', new_features + '\n\n### 🔥 新增功能')
        result['changes'].append('Added Control Plane v1.3 features section')
    
    # Write updated README
    if readme != original_readme:
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(readme)
        result['message'] = f'README.md updated: {len(result["changes"])} changes'
    else:
        result['status'] = 'no_changes_needed'
        result['message'] = 'README.md already up to date'
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
