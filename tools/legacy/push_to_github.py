# -*- coding: utf-8 -*-
import subprocess
import os

GIT_EXE = r"F:\开发工具\Git\cmd\git.exe"
REPO_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"
REMOTE_URL = "git@github.com:SherlockYzz/PVZ-Gemini-4-Argon.git"

def run_git(args):
    cmd = [GIT_EXE] + args
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("STDOUT:", res.stdout.strip())
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip())
    if res.returncode != 0:
        raise RuntimeError(f"Git command failed: {args}")
    return res.stdout

def main():
    # 1. git init
    run_git(["init", "-b", "main"])
    
    # 2. Check remote
    try:
        remotes = run_git(["remote", "-v"])
        if "origin" not in remotes:
            run_git(["remote", "add", "origin", REMOTE_URL])
        else:
            run_git(["remote", "set-url", "origin", REMOTE_URL])
    except Exception:
        run_git(["remote", "add", "origin", REMOTE_URL])
        
    # 3. git add
    run_git(["add", "."])
    
    # 4. git status
    status = run_git(["status", "--short"])
    print(f"Staged changes count: {len(status.splitlines())}")
    
    # 5. git commit
    run_git(["commit", "-m", "feat: PVZ - Gemini 4 Argon 复刻版本首发发布\n\n- 实现 34 种植物与 12 种僵尸机制还原\n- 修复大喷菇、高坚果、机枪射手等官方原版序列帧\n- 修复卡牌阳光数值显示\n- 支持泳池水面关卡与跳关功能"])
    
    # 6. git push
    print("Pushing to GitHub main branch...")
    run_git(["push", "-u", "origin", "main", "--force"])
    print("\nSuccessfully pushed to GitHub: https://github.com/SherlockYzz/PVZ-Gemini-4-Argon")

if __name__ == "__main__":
    main()
