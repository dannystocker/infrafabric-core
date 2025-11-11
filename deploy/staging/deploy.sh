#!/bin/bash
# IF.swarm WebRTC Staging Deployment Script
#
# Purpose: One-command deployment of complete WebRTC stack
# Usage: ./deploy.sh [options]
#
# Philosophy:
# - IF.ground: Reproducible deployment
# - IF.witness: All steps logged
# - IF.TTT: Transparent process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_witness() {
    local event="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[IF.witness] $timestamp - $event"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."

    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found, creating from example..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"

        # Generate TURN auth secret
        TURN_SECRET=$(openssl rand -base64 32)
        sed -i "s/CHANGE_ME_USE_OPENSSL_RAND/$TURN_SECRET/" "$ENV_FILE"

        log_success "Created .env file with generated secrets"
        log_warning "Please review and update $ENV_FILE with your configuration"
        log_warning "Especially: EXTERNAL_IP, TLS certificates, and TURN credentials"
    else
        log_success "Environment file exists"
    fi
}

# Check TURN configuration
check_turn_config() {
    log_info "Checking TURN configuration..."

    local coturn_conf="$SCRIPT_DIR/coturn.conf"

    if ! grep -q "^user=" "$coturn_conf" && ! grep -q "^static-auth-secret=" "$coturn_conf"; then
        log_warning "No TURN credentials found in coturn.conf"
        log_warning "Please add either:"
        log_warning "  user=username:password"
        log_warning "or ensure TURN_AUTH_SECRET is set in .env"
    else
        log_success "TURN credentials configured"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    log_witness "docker_build_started"

    cd "$PROJECT_ROOT"
    docker build -t ifswarm-signaling:staging -f Dockerfile .

    log_witness "docker_build_completed"
    log_success "Docker images built"
}

# Deploy stack
deploy_stack() {
    log_info "Deploying WebRTC stack..."
    log_witness "deployment_started"

    cd "$SCRIPT_DIR"

    # Determine deployment profile
    local profiles=""

    if [ "$WITH_LB" = "true" ]; then
        profiles="$profiles --profile loadbalancer"
        log_info "Including load balancer"
    fi

    if [ "$WITH_MONITORING" = "true" ]; then
        profiles="$profiles --profile monitoring"
        log_info "Including monitoring stack"
    fi

    # Deploy with docker-compose
    docker-compose $profiles up -d

    log_witness "deployment_completed"
    log_success "Stack deployed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    log_witness "verification_started"

    # Wait for services to start
    sleep 5

    # Check running containers
    log_info "Running containers:"
    docker-compose ps

    # Check signaling server
    if curl -f -s http://localhost:8443 > /dev/null 2>&1 || nc -z localhost 8443 2>/dev/null; then
        log_success "Signaling server is accessible"
    else
        log_warning "Signaling server may not be ready yet"
    fi

    # Check TURN server
    if nc -z localhost 3478 2>/dev/null; then
        log_success "TURN server is accessible"
    else
        log_warning "TURN server may not be ready yet"
    fi

    # Check Redis
    if nc -z localhost 6379 2>/dev/null; then
        log_success "Redis is accessible"
    else
        log_warning "Redis may not be ready yet"
    fi

    log_witness "verification_completed"
}

# Show deployment info
show_deployment_info() {
    echo ""
    log_success "============================================"
    log_success "IF.swarm WebRTC Stack Deployed!"
    log_success "============================================"
    echo ""
    log_info "Services:"
    log_info "  - Signaling Server: ws://localhost:8443"
    log_info "  - TURN Server: turn://localhost:3478"
    log_info "  - Redis: redis://localhost:6379"

    if [ "$WITH_LB" = "true" ]; then
        log_info "  - Nginx: http://localhost:80, https://localhost:443"
    fi

    if [ "$WITH_MONITORING" = "true" ]; then
        log_info "  - Prometheus: http://localhost:9090"
        log_info "  - Grafana: http://localhost:3000 (admin/admin)"
    fi

    echo ""
    log_info "Useful commands:"
    log_info "  View logs:    docker-compose logs -f"
    log_info "  Stop stack:   docker-compose down"
    log_info "  Restart:      docker-compose restart"
    log_info "  Status:       docker-compose ps"
    echo ""
    log_info "Next steps:"
    log_info "  1. Review .env file and update configuration"
    log_info "  2. Add TURN credentials to coturn.conf"
    log_info "  3. Test WebRTC connectivity"
    log_info "  4. Check deployment guide: docs/WEBRTC-DEPLOYMENT.md"
    echo ""
}

# Parse arguments
WITH_LB=false
WITH_MONITORING=false
BUILD_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-lb|--loadbalancer)
            WITH_LB=true
            shift
            ;;
        --with-monitoring|--monitoring)
            WITH_MONITORING=true
            shift
            ;;
        --build)
            BUILD_IMAGES=true
            shift
            ;;
        --help|-h)
            echo "IF.swarm WebRTC Deployment Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --with-lb, --loadbalancer    Deploy with Nginx load balancer"
            echo "  --with-monitoring            Deploy with Prometheus + Grafana"
            echo "  --build                      Build Docker images before deploying"
            echo "  --help, -h                   Show this help message"
            echo ""
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "IF.swarm WebRTC Staging Deployment"
    log_info "===================================="
    echo ""

    check_prerequisites
    setup_environment
    check_turn_config

    if [ "$BUILD_IMAGES" = "true" ]; then
        build_images
    fi

    deploy_stack
    verify_deployment
    show_deployment_info

    log_witness "deployment_script_completed"
}

# Run main function
main
