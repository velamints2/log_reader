#!/bin/bash
# 机器人日志分析系统 - 一键部署脚本
# 用法: chmod +x deploy.sh && ./deploy.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示欢迎信息
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🤖 机器人日志分析系统 - Docker 部署脚本              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查 Docker 是否安装
check_docker() {
    print_info "检查 Docker 环境..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装！请先安装 Docker"
        echo "  安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装！请先安装 Docker Compose"
        exit 1
    fi
    
    print_success "Docker 环境检查通过"
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    mkdir -p logs reports temp_reports reports_new final_reports
    print_success "目录创建完成"
}

# 配置环境变量
setup_env() {
    if [ ! -f .env ]; then
        print_info "创建环境配置文件..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "已创建 .env 文件，请编辑填写 API Key:"
            echo "  nano .env 或 vim .env"
        else
            print_warning ".env.example 不存在，跳过环境配置"
        fi
    else
        print_info ".env 文件已存在"
    fi
}

# 构建镜像
build_image() {
    print_info "构建 Docker 镜像..."
    
    # 检查是否使用 docker-compose 或 docker compose
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi
    
    print_success "镜像构建完成"
}

# 启动服务
start_service() {
    print_info "启动服务..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "服务启动完成"
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        docker compose down
    fi
    
    print_success "服务已停止"
}

# 查看日志
show_logs() {
    print_info "显示服务日志..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose logs -f
    else
        docker compose logs -f
    fi
}

# 检查服务状态
check_status() {
    print_info "检查服务状态..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    print_info "测试 API 连接..."
    sleep 3
    
    if curl -s http://localhost:8080/api/status > /dev/null 2>&1; then
        print_success "✅ 服务运行正常！"
        echo ""
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║  🎉 部署成功！访问地址: http://localhost:8080            ║"
        echo "╚══════════════════════════════════════════════════════════╝"
    else
        print_warning "服务正在启动中，请稍后再试..."
    fi
}

# 完整部署流程
full_deploy() {
    check_docker
    create_directories
    setup_env
    build_image
    start_service
    check_status
}

# 显示帮助信息
show_help() {
    echo "用法: ./deploy.sh [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    完整部署 (默认)"
    echo "  build     仅构建镜像"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志"
    echo "  status    查看状态"
    echo "  clean     清理容器和镜像"
    echo "  help      显示帮助"
}

# 清理
clean_all() {
    print_warning "即将清理所有容器和镜像..."
    read -p "确认继续? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose down --rmi all --volumes
        else
            docker compose down --rmi all --volumes
        fi
        print_success "清理完成"
    else
        print_info "已取消"
    fi
}

# 主逻辑
case "${1:-deploy}" in
    deploy)
        full_deploy
        ;;
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        start_service
        check_status
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        start_service
        check_status
        ;;
    logs)
        show_logs
        ;;
    status)
        check_status
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
