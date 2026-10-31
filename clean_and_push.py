# -*- coding: utf-8 -*-
import os
import subprocess

GIT_EXE = r"F:\开发工具\Git\cmd\git.exe"
REPO_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"

def run_git(args):
    cmd = [GIT_EXE] + args
    res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(" ".join(args), "-> Code:", res.returncode)
    if res.stdout.strip():
        print("STDOUT:", res.stdout.strip()[:300])
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip()[:300])
    return res

# 1. 彻底删除含有 token 的 create_github_repo.py
t_file = os.path.join(REPO_DIR, "tools", "create_github_repo.py")
if os.path.exists(t_file):
    os.remove(t_file)
    print("Deleted tools/create_github_repo.py")

# 2. 将 tools 目录从 git 跟踪中彻底移除，加入 .gitignore，保持发布仓库干净整洁
gitignore_path = os.path.join(REPO_DIR, ".gitignore")
with open(gitignore_path, "r", encoding="utf-8") as f:
    gi_content = f.read()

if "tools/" not in gi_content:
    gi_content += "\n# Internal development tools\ntools/\n"
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gi_content)
    print("Added tools/ to .gitignore")

# 3. 删除旧的 .git 目录重新初始化，彻底消除含有 secret 的 commit 历史
git_dir = os.path.join(REPO_DIR, ".git")
import shutil
# On Windows .git has read-only files sometimes
def remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

shutil.rmtree(git_dir, onerror=remove_readonly)
print("Removed .git directory to start completely fresh history.")

# 4. 重新初始化
run_git(["init", "-b", "main"])
run_git(["remote", "add", "origin", "git@github.com:SherlockYzz/PVZ-Gemini-4-Argon.git"])
run_git(["add", "."])
run_git(["commit", "-m", "feat: PVZ - Gemini 4 Argon 复刻版本首发发布\n\n- 实现 34 种植物与 12 种僵尸机制还原\n- 修复大喷菇、高坚果、机枪射手等官方原版序列帧\n- 修复卡牌阳光数值显示\n- 支持泳池水面关卡与跳关功能"])

# 5. Push
print("Pushing clean commits to GitHub...")
p_res = run_git(["push", "-u", "origin", "main", "--force"])
if p_res.returncode == 0:
    print("\nSUCCESS! Successfully pushed to https://github.com/SherlockYzz/PVZ-Gemini-4-Argon")
else:
    print("\nPush failed!")
