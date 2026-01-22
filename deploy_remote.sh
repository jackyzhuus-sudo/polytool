#!/bin/bash
# Polymarket 工具远程服务器一键部署脚本
# 在远程服务器上运行此脚本

set -e  # 遇到错误立即退出

echo "========================================================================"
echo "  Polymarket 交易员分析工具 - 远程部署"
echo "========================================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
WORK_DIR="/root/polytool"
TRADER_ADDRESS="0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

echo -e "\n${GREEN}[1/6]${NC} 检查系统环境..."

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ Python: $PYTHON_VERSION"
else
    echo -e "  ${RED}✗ Python3 未安装${NC}"
    echo "  正在安装 Python3..."
    if command -v apt-get &> /dev/null; then
        apt-get update -qq && apt-get install -y -qq python3 python3-pip
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip
    else
        echo -e "  ${RED}错误: 无法自动安装 Python${NC}"
        exit 1
    fi
fi

# 检查 pip
if command -v pip3 &> /dev/null; then
    echo "  ✓ pip3 可用"
else
    echo "  正在安装 pip3..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y -qq python3-pip
    fi
fi

# 检查 git
if command -v git &> /dev/null; then
    echo "  ✓ Git 可用"
else
    echo "  正在安装 Git..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y -qq git
    elif command -v yum &> /dev/null; then
        yum install -y git
    fi
fi

echo -e "\n${GREEN}[2/6]${NC} 创建工作目录..."
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
echo "  ✓ 工作目录: $WORK_DIR"

echo -e "\n${GREEN}[3/6]${NC} 下载或更新代码..."

# 如果当前目录已有文件，询问是否继续
if [ -f "analyze_trader.py" ]; then
    echo -e "  ${YELLOW}⚠ 目录中已存在文件${NC}"
    echo "  将使用现有文件..."
else
    echo "  请选择获取代码的方式:"
    echo "  1) 从 Git 仓库克隆 (需要访问权限)"
    echo "  2) 手动上传文件"
    echo "  3) 跳过 (已有文件)"

    read -p "  选择 [1-3]: " choice

    case $choice in
        1)
            echo "  克隆代码仓库..."
            # 这里需要替换为实际的仓库地址
            # git clone <repo_url> .
            echo -e "  ${YELLOW}提示: 请手动克隆仓库或上传文件${NC}"
            ;;
        2)
            echo -e "  ${YELLOW}请使用 scp 或 rsync 上传文件到 $WORK_DIR${NC}"
            echo "  示例: scp -r /path/to/polytool/* root@155.138.162.162:$WORK_DIR/"
            exit 0
            ;;
        3)
            echo "  跳过代码下载"
            ;;
    esac
fi

echo -e "\n${GREEN}[4/6]${NC} 安装 Python 依赖..."

# 创建 requirements.txt（如果不存在）
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'EOF'
requests>=2.31.0
tabulate>=0.9.0
EOF
    echo "  ✓ 创建 requirements.txt"
fi

pip3 install -q -r requirements.txt
echo "  ✓ 依赖安装完成"

echo -e "\n${GREEN}[5/6]${NC} 测试 Polymarket API 连接..."

if [ -f "test_api.py" ]; then
    python3 test_api.py "$TRADER_ADDRESS" || echo -e "  ${YELLOW}⚠ API 测试失败，将使用演示模式${NC}"
else
    echo -e "  ${YELLOW}⚠ test_api.py 不存在，跳过测试${NC}"
fi

echo -e "\n${GREEN}[6/6]${NC} 运行交易员分析..."
echo "  分析地址: $TRADER_ADDRESS"
echo ""

if [ -f "analyze_trader.py" ]; then
    # 首先尝试真实 API
    if python3 analyze_trader.py "$TRADER_ADDRESS" 2>&1 | grep -q "No trades found"; then
        echo -e "\n${YELLOW}API 不可用，使用演示模式...${NC}\n"
        python3 analyze_trader.py "$TRADER_ADDRESS" --demo
    fi
else
    echo -e "${RED}错误: analyze_trader.py 不存在${NC}"
    echo "请先上传项目文件到 $WORK_DIR"
    exit 1
fi

echo ""
echo "========================================================================"
echo -e "  ${GREEN}部署和分析完成！${NC}"
echo "========================================================================"
echo ""
echo "可用命令:"
echo "  • 分析其他地址: python3 analyze_trader.py <address>"
echo "  • 使用演示模式: python3 analyze_trader.py <address> --demo"
echo "  • 测试 API: python3 test_api.py <address>"
echo "  • 查看帮助: python3 analyze_trader.py --help"
echo ""
