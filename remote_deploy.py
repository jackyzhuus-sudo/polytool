#!/usr/bin/env python3
"""
SSH 部署和运行脚本
通过 SSH 将 Polymarket 工具部署到远程服务器并运行分析
"""
import paramiko
import sys
import os
from pathlib import Path


def connect_ssh(host, username, password):
    """连接到 SSH 服务器"""
    print(f"正在连接到 {username}@{host}...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        print("✅ SSH 连接成功！\n")
        return client
    except Exception as e:
        print(f"❌ SSH 连接失败: {e}")
        return None


def execute_command(client, command, description=""):
    """在远程服务器执行命令"""
    if description:
        print(f"[执行] {description}")

    stdin, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if output:
        print(output)

    if error and exit_code != 0:
        print(f"错误: {error}")

    return exit_code, output, error


def upload_directory(client, local_path, remote_path):
    """上传整个目录到远程服务器"""
    print(f"\n上传文件从 {local_path} 到 {remote_path}...")

    sftp = client.open_sftp()

    # 创建远程目录
    try:
        sftp.mkdir(remote_path)
    except:
        pass  # 目录可能已存在

    # 上传所有文件
    local_dir = Path(local_path)
    uploaded = 0

    for item in local_dir.rglob('*'):
        if item.is_file():
            # 跳过不需要的文件
            if any(skip in str(item) for skip in ['.git', '__pycache__', '.pyc', '.DS_Store']):
                continue

            relative_path = item.relative_to(local_dir)
            remote_file = os.path.join(remote_path, str(relative_path)).replace('\\', '/')

            # 创建远程子目录
            remote_dir = os.path.dirname(remote_file)
            try:
                sftp.mkdir(remote_dir)
            except:
                pass

            # 上传文件
            try:
                sftp.put(str(item), remote_file)
                uploaded += 1
                print(f"  ✓ {relative_path}")
            except Exception as e:
                print(f"  ✗ {relative_path}: {e}")

    sftp.close()
    print(f"\n上传完成！共上传 {uploaded} 个文件")


def main():
    # SSH 连接信息
    HOST = "155.138.162.162"
    USERNAME = "root"
    PASSWORD = "2U$kG$DF??f%wa*R"
    REMOTE_PATH = "/root/polytool"

    # 交易员地址
    TRADER_ADDRESS = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

    print("="*70)
    print("  Polymarket 工具远程部署和执行")
    print("="*70)

    # 1. 连接到服务器
    client = connect_ssh(HOST, USERNAME, PASSWORD)
    if not client:
        sys.exit(1)

    try:
        # 2. 检查远程环境
        print("检查远程服务器环境...")
        execute_command(client, "uname -a", "系统信息")
        execute_command(client, "python3 --version", "Python 版本")
        execute_command(client, "which pip3", "检查 pip3")

        # 3. 上传文件
        local_path = "/home/user/polytool"
        upload_directory(client, local_path, REMOTE_PATH)

        # 4. 安装依赖
        print("\n" + "="*70)
        print("安装 Python 依赖...")
        print("="*70)
        execute_command(
            client,
            f"cd {REMOTE_PATH} && pip3 install -q -r requirements.txt",
            "安装依赖包"
        )

        # 5. 测试 API 连接
        print("\n" + "="*70)
        print("测试 Polymarket API 连接...")
        print("="*70)
        execute_command(
            client,
            f"cd {REMOTE_PATH} && python3 test_api.py {TRADER_ADDRESS}",
            "测试 API"
        )

        # 6. 运行分析
        print("\n" + "="*70)
        print("运行交易员分析...")
        print("="*70)
        exit_code, output, error = execute_command(
            client,
            f"cd {REMOTE_PATH} && python3 analyze_trader.py {TRADER_ADDRESS}",
            "分析交易员数据"
        )

        # 7. 如果 API 不可用，使用演示模式
        if "No trades found" in output or "No trades found" in error or exit_code != 0:
            print("\n" + "="*70)
            print("API 不可用，使用演示模式...")
            print("="*70)
            execute_command(
                client,
                f"cd {REMOTE_PATH} && python3 analyze_trader.py {TRADER_ADDRESS} --demo",
                "演示模式分析"
            )

        # 8. 下载结果（如果需要）
        print("\n" + "="*70)
        print("分析完成！")
        print("="*70)

        # 提供交互选项
        print("\n可用命令:")
        print("  1. 下载分析结果")
        print("  2. 在远程服务器运行其他命令")
        print("  3. 退出")

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
    finally:
        client.close()
        print("\nSSH 连接已关闭")


if __name__ == '__main__':
    try:
        import paramiko
    except ImportError:
        print("错误: 需要安装 paramiko 库")
        print("运行: pip3 install paramiko")
        sys.exit(1)

    main()
