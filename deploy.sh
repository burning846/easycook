#!/bin/bash

# EasyCook一键部署脚本
# 用于快速部署和初始化Vercel项目

set -e  # 遇到错误立即退出

echo "🚀 EasyCook一键部署脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印彩色消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查必要工具
check_requirements() {
    print_info "检查必要工具..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI 未安装，正在安装..."
        npm install -g vercel
    fi
    
    print_success "所有必要工具已就绪"
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    # 安装前端依赖
    if [ -d "frontend" ]; then
        print_info "安装前端依赖..."
        cd frontend
        npm install
        cd ..
        print_success "前端依赖安装完成"
    fi
    
    # 安装后端依赖
    if [ -f "backend/requirements.txt" ]; then
        print_info "安装后端依赖..."
        pip3 install -r backend/requirements.txt
        print_success "后端依赖安装完成"
    fi
}

# 构建前端
build_frontend() {
    print_info "构建前端项目..."
    
    if [ -d "frontend" ]; then
        cd frontend
        npm run build
        cd ..
        print_success "前端构建完成"
    else
        print_warning "未找到前端目录，跳过前端构建"
    fi
}

# 部署到Vercel
deploy_to_vercel() {
    print_info "部署到Vercel..."
    
    # 检查是否已登录
    if ! vercel whoami &> /dev/null; then
        print_info "请登录Vercel..."
        vercel login
    fi
    
    # 部署项目
    vercel --prod
    
    print_success "项目部署完成"
}

# 初始化数据库
init_database() {
    print_info "初始化数据库..."
    
    # 拉取环境变量
    print_info "拉取Vercel环境变量..."
    vercel env pull .env.local
    
    # 初始化数据库
    print_info "运行数据库初始化..."
    if [ -f "vercel_db.py" ]; then
        python3 vercel_db.py init
    else
        python3 backend/init_db.py
    fi
    
    print_success "数据库初始化完成"
}

# 验证部署
verify_deployment() {
    print_info "验证部署状态..."
    
    # 检查数据库状态
    if [ -f "vercel_db.py" ]; then
        python3 vercel_db.py check
    fi
    
    print_success "部署验证完成"
}

# 主函数
main() {
    echo "开始部署流程..."
    echo ""
    
    # 检查参数
    SKIP_DEPS=false
    SKIP_BUILD=false
    SKIP_DEPLOY=false
    SKIP_DB=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-deploy)
                SKIP_DEPLOY=true
                shift
                ;;
            --skip-db)
                SKIP_DB=true
                shift
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --skip-deps    跳过依赖安装"
                echo "  --skip-build   跳过前端构建"
                echo "  --skip-deploy  跳过Vercel部署"
                echo "  --skip-db      跳过数据库初始化"
                echo "  --help         显示帮助信息"
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行部署步骤
    check_requirements
    
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    else
        print_warning "跳过依赖安装"
    fi
    
    if [ "$SKIP_BUILD" = false ]; then
        build_frontend
    else
        print_warning "跳过前端构建"
    fi
    
    if [ "$SKIP_DEPLOY" = false ]; then
        deploy_to_vercel
    else
        print_warning "跳过Vercel部署"
    fi
    
    if [ "$SKIP_DB" = false ]; then
        init_database
        verify_deployment
    else
        print_warning "跳过数据库初始化"
    fi
    
    echo ""
    print_success "🎉 部署完成！"
    echo ""
    print_info "接下来你可以："
    echo "  1. 访问你的Vercel项目URL查看应用"
    echo "  2. 使用 'python3 vercel_db.py check' 检查数据库状态"
    echo "  3. 使用 'python3 backend/db_manager.py status' 查看详细统计"
    echo ""
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@"