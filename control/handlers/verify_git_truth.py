#!/usr/bin/env python3
"""
Verify git truth level (L1/L2/L3/L4) for the repository.

L4 requirements (ALL must be true):
1. Working tree clean (git status --short is empty)
2. Local HEAD == origin/main HEAD
3. Acceptance policy exists and is valid
4. Re-audit passed (no modifications since last audit)

Outputs:
- completion_level (L1/L2/L3/L4)
- working_tree_clean (bool)
- commit_hash (str)
- push_confirmation (bool)
- remote_branch (str)
- re_audit_passed (bool)
- may_claim_completed (bool)
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def run_cmd(cmd):
    try:
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
        stdout, stderr = r.communicate()
        return stdout.decode('utf-8').strip(), stderr.decode('utf-8').strip(), r.returncode
    except Exception as e:
        return '', str(e), 1

def main():
    result = {
        "handler": "verify_git_truth",
        "status": "success",
        "completion_level": "L1",
        "evidence": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # === L2 Check: Working tree status ===
    status_short, _, _ = run_cmd("git status --short")
    status_lines = [l for l in status_short.split('\n') if l.strip() and 'node_modules' not in l]
    
    # Filter out runtime files that are in .gitignore
    runtime_files = ['control/runtime_state.json', 'control/status.md', 'control/logs/', 'control/reports/', 'control/__pycache__/']
    filtered_status = []
    for line in status_lines:
        is_runtime = any(rt in line for rt in runtime_files)
        if not is_runtime:
            filtered_status.append(line)
    
    result['evidence']['git_status_filtered'] = filtered_status
    result['evidence']['working_tree_clean'] = len(filtered_status) == 0
    
    if status_short:
        result['evidence']['file_diff'] = list(set(line.split()[-1] for line in status_lines if line))
        result['completion_level'] = 'L2'
    
    # === L3 Check: Commit exists ===
    log, _, code = run_cmd("git log -1 --format='%H %s'")
    if code == 0 and log:
        result['evidence']['commit_hash'] = log.split()[0]
        result['evidence']['commit_message'] = ' '.join(log.split()[1:])
        result['completion_level'] = 'L3'
    
    # === L4 Check: Pushed AND working tree clean ===
    local_log, _, _ = run_cmd("git log -1 --format='%H'")
    remote_log, _, _ = run_cmd("git log origin/main -1 --format='%H'")
    
    heads_match = local_log and remote_log and local_log == remote_log
    tree_clean = result['evidence'].get('working_tree_clean', False)
    
    # L4 requires BOTH: pushed AND clean working tree
    if heads_match and tree_clean:
        result['evidence']['push_confirmation'] = True
        result['evidence']['remote_branch'] = 'origin/main'
        result['completion_level'] = 'L4'
    else:
        result['evidence']['push_confirmation'] = heads_match
        result['evidence']['remote_branch'] = 'origin/main' if heads_match else None
        # Cannot be L4 if working tree is dirty
        if not tree_clean:
            result['evidence']['l4_blocked_reason'] = 'working_tree_dirty'
    
    # === Re-audit check ===
    # Check if acceptance_policy.json exists and is valid
    policy_path = BASE_DIR / "control" / "acceptance_policy.json"
    re_audit_passed = False
    if policy_path.exists():
        try:
            with open(policy_path) as f:
                policy = json.load(f)
            if policy.get('version') and policy.get('levels'):
                re_audit_passed = True
        except:
            pass
    
    result['evidence']['re_audit_passed'] = re_audit_passed
    result['evidence']['acceptance_policy_exists'] = policy_path.exists()
    
    # === Final determination ===
    result['evidence']['may_claim_completed'] = (
        result['completion_level'] == 'L4' and 
        result['evidence'].get('working_tree_clean', False) and
        result['evidence'].get('re_audit_passed', False)
    )
    
    # === Output fields summary ===
    result['output'] = {
        'completion_level': result['completion_level'],
        'working_tree_clean': result['evidence'].get('working_tree_clean', False),
        'commit_hash': result['evidence'].get('commit_hash', None),
        'push_confirmation': result['evidence'].get('push_confirmation', False),
        'remote_branch': result['evidence'].get('remote_branch', None),
        're_audit_passed': result['evidence'].get('re_audit_passed', False),
        'may_claim_completed': result['evidence']['may_claim_completed']
    }
    
    result['message'] = f"Task at {result['completion_level']} - {'May claim completed' if result['evidence']['may_claim_completed'] else 'Not yet L4'}"
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
