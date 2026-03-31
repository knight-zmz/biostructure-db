#!/usr/bin/env python3
"""
Verify git truth level (L1/L2/L3/L4) for a given task or file set.

Checks:
- git diff (L2)
- git status (L2/L3)
- git log (L3)
- git push status (L4)

Outputs completion_level and evidence.
"""
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10, cwd=BASE_DIR)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def main():
    result = {
        "handler": "verify_git_truth",
        "status": "success",
        "completion_level": "L1",
        "evidence": {}
    }
    
    # Check git diff (L2 evidence)
    diff, _ = run_cmd("git diff --name-only")
    if diff:
        result['evidence']['file_diff'] = diff.split('\n')
        result['completion_level'] = 'L2'
    
    # Check git status (L2/L3)
    status, _ = run_cmd("git status --short")
    result['evidence']['git_status'] = status.split('\n') if status else []
    
    # Check git log (L3 evidence)
    log, code = run_cmd("git log -1 --format='%H %s'")
    if code == 0 and log:
        result['evidence']['commit_hash'] = log.split()[0]
        result['evidence']['commit_message'] = ' '.join(log.split()[1:])
        result['completion_level'] = 'L3'
    
    # Check git push status (L4 evidence)
    ahead, _ = run_cmd("git status | grep 'Your branch is ahead'")
    if not ahead:
        # Check if last commit is pushed
        local_log, _ = run_cmd("git log -1 --format='%H'")
        remote_log, _ = run_cmd("git log origin/main -1 --format='%H'")
        if local_log and remote_log and local_log == remote_log:
            result['evidence']['push_confirmation'] = True
            result['evidence']['remote_branch'] = 'origin/main'
            result['completion_level'] = 'L4'
    
    # Check acceptance policy
    policy_path = BASE_DIR / "control" / "acceptance_policy.json"
    if policy_path.exists():
        result['evidence']['acceptance_policy_exists'] = True
    
    result['message'] = f"Task at {result['completion_level']} - {'May claim completed' if result['completion_level'] == 'L4' else 'Not yet L4'}"
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
