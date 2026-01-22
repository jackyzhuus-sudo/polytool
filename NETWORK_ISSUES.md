# 网络隔离问题说明和解决方案

## 问题诊断

当前环境存在网络限制：

### 代理配置
环境使用受限的 HTTP/HTTPS 代理，只允许访问特定的域名白名单：
```
https_proxy=http://container_...@21.0.0.123:15004
```

### 被阻止的域名
以下域名不在白名单中，无法访问：
- ❌ `gamma-api.polymarket.com` (Polymarket API)
- ❌ `api.thegraph.com` (The Graph 子图)
- ❌ `strapi-matic.poly.market` (Polymarket 元数据)
- ❌ `155.138.162.162` (你的远程服务器)

### 影响
1. 无法直接调用 Polymarket API 获取真实交易数据
2. 无法通过 SSH 连接到远程服务器 (155.138.162.162)
3. 所有对 Polymarket 相关服务的网络请求返回 403 Forbidden

## 解决方案

### 方案 1: 使用演示模式（立即可用）✅

这是当前环境唯一可行的方案：

```bash
cd /home/user/polytool
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

**优点**:
- 无需网络访问
- 立即可用
- 展示完整功能

**缺点**:
- 数据是模拟的，不是真实数据

### 方案 2: 手动部署到远程服务器

由于当前环境无法连接到你的服务器，需要在**本地机器**执行以下步骤：

#### 步骤 1: 准备部署包

在当前环境创建部署包：

```bash
cd /home/user
tar -czf polytool-deploy.tar.gz polytool/
ls -lh polytool-deploy.tar.gz
```

已创建: `/home/user/polytool-deploy.tar.gz` (75KB)

#### 步骤 2: 下载部署包到本地

你需要从当前环境将文件下载到你的本地机器。

#### 步骤 3: 从本地上传到服务器

在你的**本地机器**执行：

```bash
# 上传部署包
scp /path/to/polytool-deploy.tar.gz root@155.138.162.162:/root/

# 连接到服务器
ssh root@155.138.162.162
# 密码: 2U$kG$DF??f%wa*R

# 在服务器上解压
cd /root
tar -xzf polytool-deploy.tar.gz
cd polytool

# 安装依赖
pip3 install -r requirements.txt

# 测试 API 连接
python3 test_api.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 运行分析
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
```

### 方案 3: 使用 Git 仓库

如果你已经将代码推送到 Git 仓库：

```bash
# 在服务器上
ssh root@155.138.162.162

# 克隆仓库
cd /root
git clone <你的仓库URL> polytool
cd polytool

# 安装和运行
pip3 install -r requirements.txt
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
```

### 方案 4: 逐文件复制

如果文件不多，可以逐个文件复制：

```bash
# 从本地机器
scp analyze_trader.py root@155.138.162.162:/root/polytool/
scp polymarket_client.py root@155.138.162.162:/root/polytool/
scp trader_analyzer.py root@155.138.162.162:/root/polytool/
# ... 其他文件
```

## 当前可用的文件

已在 `/home/user/polytool/` 创建以下文件：

```
polytool/
├── analyze_trader.py        # 主分析工具 ✅
├── polymarket_client.py     # API 客户端 ✅
├── polymarket_subgraph.py   # 子图客户端 ✅
├── trader_analyzer.py       # 分析引擎 ✅
├── demo_data.py            # 演示数据生成器 ✅
├── test_api.py             # API 连接测试 ✅
├── examples.py             # 代码示例 ✅
├── remote_deploy.py        # SSH 部署脚本 ✅
├── deploy_remote.sh        # 远程部署脚本 ✅
├── requirements.txt        # Python 依赖 ✅
├── README.md              # 项目文档 ✅
├── API_GUIDE.md           # API 使用指南 ✅
├── QUICK_START.md         # 快速开始 ✅
├── REMOTE_DEPLOYMENT.md   # 远程部署指南 ✅
└── NETWORK_ISSUES.md      # 本文档 ✅
```

## 推荐工作流程

### 在当前受限环境

```bash
# 只能使用演示模式
cd /home/user/polytool
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

### 在你的远程服务器 (155.138.162.162)

```bash
# 1. 连接到服务器（从本地）
ssh root@155.138.162.162

# 2. 创建工作目录
mkdir -p /root/polytool
cd /root/polytool

# 3. 上传文件（从本地执行）
scp -r /local/path/polytool/* root@155.138.162.162:/root/polytool/

# 4. 安装依赖
pip3 install -r requirements.txt

# 5. 测试连接
python3 test_api.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 6. 运行分析
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 7. 如果 API 可用，应该能看到真实数据
# 8. 如果 API 不可用，会自动降级到演示模式
```

## 一键命令（在本地机器执行）

### 方法 A: 使用 rsync

```bash
# 同步整个目录到服务器
rsync -avz -e "ssh" \
  --exclude '.git' \
  --exclude '__pycache__' \
  /local/path/polytool/ \
  root@155.138.162.162:/root/polytool/

# 远程执行
ssh root@155.138.162.162 "cd /root/polytool && pip3 install -r requirements.txt && python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
```

### 方法 B: 使用 scp + 脚本

创建本地脚本 `deploy.sh`:

```bash
#!/bin/bash
SERVER="root@155.138.162.162"
REMOTE_DIR="/root/polytool"
TRADER="0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

echo "上传文件..."
scp -r ./polytool/* $SERVER:$REMOTE_DIR/

echo "运行分析..."
ssh $SERVER << EOF
cd $REMOTE_DIR
pip3 install -q -r requirements.txt
python3 analyze_trader.py $TRADER
EOF

echo "完成！"
```

运行：
```bash
chmod +x deploy.sh
./deploy.sh
```

## 文件获取

### 从当前环境获取文件

如果你需要从当前环境获取这些文件到你的本地机器：

1. **下载压缩包**:
   ```bash
   # 在当前环境
   tar -czf /tmp/polytool.tar.gz -C /home/user polytool
   ```

2. **或者查看并复制文件内容** (对于单个文件):
   ```bash
   cat /home/user/polytool/analyze_trader.py
   # 复制内容到本地
   ```

## 测试清单

在远程服务器上，按顺序运行以下命令验证：

```bash
# 1. 检查 Python
python3 --version

# 2. 检查文件
ls -la /root/polytool/

# 3. 安装依赖
cd /root/polytool
pip3 install -r requirements.txt

# 4. 测试导入
python3 -c "from polymarket_client import PolymarketClient; print('OK')"

# 5. 运行帮助
python3 analyze_trader.py --help

# 6. 测试 API
python3 test_api.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 7. 运行分析（真实 API）
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 8. 如果失败，使用演示模式
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

## 总结

**当前环境限制**:
- ❌ 无法访问 Polymarket API
- ❌ 无法连接远程服务器
- ✅ 可以使用演示模式

**推荐操作**:
1. 在当前环境使用演示模式测试功能
2. 手动将文件部署到远程服务器
3. 在远程服务器上运行真实分析

**需要的操作** (在本地机器):
1. 获取项目文件
2. 上传到远程服务器 155.138.162.162
3. 在服务器上安装依赖并运行

需要我提供具体某个步骤的详细指导吗？
