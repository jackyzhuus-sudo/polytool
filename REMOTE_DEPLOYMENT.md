# 远程服务器部署指南

本指南介绍如何将 Polymarket 交易员分析工具部署到远程服务器。

## 服务器信息

```
服务器地址: 155.138.162.162
用户名: root
密码: 2U$kG$DF??f%wa*R
```

## 方法一：手动部署（推荐）

### 步骤 1: 连接到服务器

```bash
ssh root@155.138.162.162
# 输入密码: 2U$kG$DF??f%wa*R
```

### 步骤 2: 上传项目文件

**选项 A - 使用 SCP（从本地机器）:**

```bash
# 压缩项目文件
cd /home/user
tar -czf polytool.tar.gz polytool/

# 上传到服务器
scp polytool.tar.gz root@155.138.162.162:/root/

# 在服务器上解压
ssh root@155.138.162.162 "cd /root && tar -xzf polytool.tar.gz"
```

**选项 B - 使用 Git（如果有仓库）:**

```bash
# 在服务器上
cd /root
git clone <your-repo-url> polytool
cd polytool
```

**选项 C - 手动创建文件（如果文件较少）:**

```bash
# 在服务器上
mkdir -p /root/polytool
cd /root/polytool

# 然后逐个创建文件，或使用编辑器创建
```

### 步骤 3: 安装依赖

```bash
cd /root/polytool

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 步骤 4: 测试连接

```bash
# 测试 Polymarket API 连接
python3 test_api.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
```

### 步骤 5: 运行分析

```bash
# 如果 API 可用
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 如果 API 不可用，使用演示模式
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo

# 导出结果
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --export results.json
```

## 方法二：使用一键部署脚本

### 步骤 1: 上传脚本

```bash
# 从本地上传部署脚本
scp /home/user/polytool/deploy_remote.sh root@155.138.162.162:/root/
```

### 步骤 2: 上传项目文件

```bash
# 上传整个项目
scp -r /home/user/polytool/* root@155.138.162.162:/root/polytool/
```

### 步骤 3: 运行部署脚本

```bash
# 连接到服务器
ssh root@155.138.162.162

# 运行部署脚本
cd /root
chmod +x deploy_remote.sh
./deploy_remote.sh
```

## 方法三：使用 rsync 同步文件

```bash
# 从本地同步到远程服务器
rsync -avz --progress \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  /home/user/polytool/ \
  root@155.138.162.162:/root/polytool/

# 然后连接并运行
ssh root@155.138.162.162 "cd /root/polytool && pip3 install -r requirements.txt && python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
```

## 方法四：创建 Docker 容器（高级）

如果服务器支持 Docker：

### 创建 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "analyze_trader.py"]
CMD ["--help"]
```

### 构建和运行

```bash
# 在服务器上
cd /root/polytool

# 构建镜像
docker build -t polymarket-analyzer .

# 运行分析
docker run polymarket-analyzer 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

## 快速命令参考

### 连接服务器

```bash
ssh root@155.138.162.162
```

### 上传单个文件

```bash
scp /local/file.py root@155.138.162.162:/root/polytool/
```

### 上传整个目录

```bash
scp -r /home/user/polytool root@155.138.162.162:/root/
```

### 下载分析结果

```bash
scp root@155.138.162.162:/root/polytool/results.json ./
```

### 远程执行命令

```bash
ssh root@155.138.162.162 "cd /root/polytool && python3 analyze_trader.py 0x... --demo"
```

## 一键操作脚本（本地运行）

创建 `local_deploy.sh`：

```bash
#!/bin/bash
# 本地一键部署脚本

HOST="155.138.162.162"
USER="root"
PASS="2U\$kG\$DF??f%wa*R"
REMOTE_DIR="/root/polytool"
LOCAL_DIR="/home/user/polytool"
TRADER="0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

echo "上传文件到服务器..."
sshpass -p "$PASS" scp -r -o StrictHostKeyChecking=no \
  "$LOCAL_DIR"/* "$USER@$HOST:$REMOTE_DIR/"

echo "安装依赖并运行分析..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" << EOF
cd $REMOTE_DIR
pip3 install -q -r requirements.txt
python3 analyze_trader.py $TRADER
EOF

echo "完成！"
```

使用：

```bash
chmod +x local_deploy.sh
./local_deploy.sh
```

## 常见问题

### Q1: SSH 连接超时

**检查方法:**
```bash
# 测试网络连接
ping 155.138.162.162

# 测试 SSH 端口
nc -zv 155.138.162.162 22
telnet 155.138.162.162 22
```

**可能的原因:**
- 防火墙阻止
- 服务器未启动
- 网络问题
- SSH 服务未运行

### Q2: 权限被拒绝

```bash
# 检查文件权限
ls -la /root/polytool/

# 修改权限
chmod +x /root/polytool/*.py
chmod +x /root/polytool/*.sh
```

### Q3: Python 模块缺失

```bash
# 重新安装依赖
pip3 install --upgrade -r requirements.txt

# 或单独安装
pip3 install requests tabulate
```

### Q4: API 访问失败

```bash
# 使用演示模式
python3 analyze_trader.py 0x... --demo

# 或尝试子图模式
python3 analyze_trader.py 0x... --subgraph
```

## 验证部署

部署完成后，运行以下命令验证：

```bash
# 1. 检查文件是否存在
ls -la /root/polytool/

# 2. 测试 Python 导入
python3 -c "import requests, tabulate; print('OK')"

# 3. 运行帮助命令
python3 analyze_trader.py --help

# 4. 运行演示模式
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

## 自动化脚本（完整版）

将以下内容保存为 `auto_deploy.py`：

```python
#!/usr/bin/env python3
import paramiko
import sys
from pathlib import Path

HOST = "155.138.162.162"
USER = "root"
PASS = "2U$kG$DF??f%wa*R"
REMOTE_DIR = "/root/polytool"
LOCAL_DIR = "/home/user/polytool"

def deploy():
    print("连接到服务器...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)

    print("上传文件...")
    sftp = client.open_sftp()
    for file in Path(LOCAL_DIR).rglob('*.py'):
        remote_path = f"{REMOTE_DIR}/{file.name}"
        sftp.put(str(file), remote_path)
        print(f"  ✓ {file.name}")

    print("安装依赖...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {REMOTE_DIR} && pip3 install -q -r requirements.txt"
    )
    stdout.channel.recv_exit_status()

    print("运行分析...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {REMOTE_DIR} && python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
    )
    print(stdout.read().decode())

    client.close()
    print("完成！")

if __name__ == '__main__':
    deploy()
```

运行：
```bash
python3 auto_deploy.py
```

## 推荐工作流程

### 首次部署

1. 压缩项目文件
2. 上传到服务器
3. 解压并安装依赖
4. 测试 API 连接
5. 运行分析

### 后续更新

1. 使用 rsync 同步更改的文件
2. 直接运行分析（依赖已安装）

### 定期分析

创建 cron 任务自动运行：

```bash
# 在服务器上编辑 crontab
crontab -e

# 添加每天运行一次
0 0 * * * cd /root/polytool && python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --export /root/results/$(date +\%Y\%m\%d).json
```

## 需要帮助？

- 查看日志: `python3 analyze_trader.py 0x... 2>&1 | tee analysis.log`
- 测试模式: `python3 analyze_trader.py 0x... --demo`
- 查看文档: `less README.md`
- API 指南: `less API_GUIDE.md`
