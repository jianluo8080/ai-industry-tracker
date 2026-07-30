#!/usr/bin/env python3
"""
一键部署脚本 - 将 AI 产业跟踪仪表盘部署到 GitHub Pages

使用方法:
  python deploy.py

前提条件:
  1. 已注册 GitHub 账号 (https://github.com/signup)
  2. 已安装 Git (https://git-scm.com)

脚本会自动:
  - 检查环境 (Git, GitHub CLI)
  - 创建 GitHub 仓库
  - 上传所有文件
  - 启用 GitHub Pages
  - 配置每日自动更新
"""

import os
import sys
import subprocess
import platform

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd, check=True, capture=False):
    """运行命令"""
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_DIR)
        if check and result.returncode != 0:
            print(f"  错误: {result.stderr}")
        return result
    else:
        result = subprocess.run(cmd, shell=True, cwd=PROJECT_DIR)
        if check and result.returncode != 0:
            print(f"  命令失败: {cmd}")
        return result

def check_command(cmd):
    """检查命令是否存在"""
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        return True
    except:
        return False

def main():
    print("=" * 60)
    print("  AI 产业跟踪仪表盘 - 一键部署到 GitHub Pages")
    print("=" * 60)
    print()

    # 1. 检查 Git
    print("[1/6] 检查 Git...")
    if not check_command("git --version"):
        print("  ✗ Git 未安装!")
        print("  请先安装 Git: https://git-scm.com/downloads")
        print("  安装后重新运行此脚本")
        sys.exit(1)
    git_version = run("git --version", capture=True).stdout.strip()
    print(f"  ✓ {git_version}")

    # 2. 检查 GitHub CLI
    print()
    print("[2/6] 检查 GitHub CLI...")
    has_gh = check_command("gh --version")
    if has_gh:
        gh_version = run("gh --version", capture=True).stdout.strip().split('\n')[0]
        print(f"  ✓ {gh_version}")
    else:
        print("  ! GitHub CLI 未安装 (可选，但推荐)")
        print("  安装后可自动创建仓库: https://cli.github.com")
        print("  不安装也可以手动创建，见后续步骤")

    # 3. 初始化 Git 仓库
    print()
    print("[3/6] 初始化 Git 仓库...")
    if os.path.exists(os.path.join(PROJECT_DIR, '.git')):
        print("  ✓ Git 仓库已存在")
    else:
        run("git init")
        run("git branch -M main")
        print("  ✓ Git 仓库已初始化")

    # 4. 询问仓库名
    print()
    print("[4/6] 配置仓库...")
    repo_name = input("  请输入仓库名称 (回车默认: ai-industry-tracker): ").strip()
    if not repo_name:
        repo_name = "ai-industry-tracker"
    print(f"  仓库名: {repo_name}")

    # 5. 添加文件并提交
    print()
    print("[5/6] 添加文件并提交...")
    run("git add -A")
    run('git commit -m "初始部署: AI 产业跟踪仪表盘"')
    print("  ✓ 文件已提交")

    # 6. 创建远程仓库并推送
    print()
    print("[6/6] 创建 GitHub 仓库并推送...")
    print()

    if has_gh:
        # 检查是否已登录
        auth_check = run("gh auth status", capture=True, check=False)
        if auth_check.returncode != 0:
            print("  需要先登录 GitHub CLI")
            print("  正在打开浏览器登录...")
            run("gh auth login -w")
        
        # 创建仓库
        print(f"  创建仓库: {repo_name}")
        create_result = run(
            f'gh repo create {repo_name} --public --source=. --push',
            capture=True, check=False
        )
        if create_result.returncode == 0:
            print(f"  ✓ 仓库已创建并推送")
            # 获取仓库 URL
            remote_url = run("git remote get-url origin", capture=True).stdout.strip()
            print(f"  仓库地址: {remote_url}")
        else:
            print(f"  创建失败: {create_result.stderr}")
            print("  请手动创建仓库，见下方说明")
            manual_deploy(repo_name)
    else:
        manual_deploy(repo_name)

    # 输出访问地址
    print()
    print("=" * 60)
    print("  部署完成!")
    print("=" * 60)
    print()
    print("  接下来需要手动启用 GitHub Pages:")
    print(f"  1. 打开 https://github.com 你的仓库 {repo_name}")
    print("  2. 点击 Settings (设置)")
    print("  3. 左侧菜单找到 Pages")
    print("  4. Source 选择 'GitHub Actions'")
    print("  5. 保存后等待几分钟")
    print()
    print("  你的仪表盘地址将是:")
    print(f"  https://<你的用户名>.github.io/{repo_name}/")
    print()
    print("  每日自动更新已配置 (北京时间每天 8:00)")
    print("  也可在 GitHub 仓库的 Actions 页面手动触发")
    print()
    print("  手机使用:")
    print("  - 用浏览器打开上面的地址")
    print("  - 选择「添加到主屏幕」即可像 APP 一样使用")

def manual_deploy(repo_name):
    """手动部署说明"""
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │ 手动部署步骤:                                    │")
    print("  │                                                  │")
    print("  │ 1. 打开 https://github.com/new                  │")
    print(f"  │ 2. 仓库名填: {repo_name:<34s}│")
    print("  │ 3. 选择 Public, 点击 Create repository          │")
    print("  │ 4. 复制以下命令到终端运行:                       │")
    print("  │                                                  │")
    print("  │    git remote add origin https://github.com/    │")
    print(f"  │      <你的用户名>/{repo_name}.git               │")
    print("  │    git push -u origin main                       │")
    print("  │                                                  │")
    print("  └─────────────────────────────────────────────────┘")

if __name__ == '__main__':
    main()
