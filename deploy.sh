#!/bin/bash

# Flix-Finder Kubernetes Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="flix-finder"
IMAGE_NAME="flix-finder"
IMAGE_TAG="latest"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    print_status "kubectl is installed"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
    docker build -t $IMAGE_NAME:$IMAGE_TAG .
    print_status "Docker image built successfully"
}

# Function to create namespace and persistent volumes
setup_namespace() {
    print_status "Setting up namespace and persistent volumes"
    kubectl apply -f k8s-namespace-pv.yaml
    print_status "Namespace and PVs created"
}

# Function to deploy development version
deploy_dev() {
    print_status "Deploying development version"
    kubectl apply -f k8s-dev-deployment.yaml
    print_status "Development deployment created"
    
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/flix-finder-dev -n $NAMESPACE
    
    print_status "Getting service information..."
    kubectl get svc flix-finder-dev-service -n $NAMESPACE
    
    NODE_PORT=$(kubectl get svc flix-finder-dev-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}')
    print_status "Application will be available on NodePort: $NODE_PORT"
    print_status "Access via: http://localhost:$NODE_PORT (if using local cluster)"
}

# Function to deploy production version
deploy_prod() {
    print_status "Deploying flix-finder to Kubernetes"
    kubectl apply -f k8s-flix-finder.yaml
    print_status "Deployment created"
    
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/flix-finder -n $NAMESPACE
    
    print_status "Getting service information..."
    kubectl get svc flix-finder-service -n $NAMESPACE
}

# Function to show status
show_status() {
    print_status "Current deployment status:"
    echo
    print_status "Namespaces:"
    kubectl get ns | grep flix-finder || echo "No flix-finder namespace found"
    echo
    print_status "Deployments in flix-finder namespace:"
    kubectl get deployments -n $NAMESPACE || echo "No deployments found"
    echo
    print_status "Services in flix-finder namespace:"
    kubectl get svc -n $NAMESPACE || echo "No services found"
    echo
    print_status "Pods in flix-finder namespace:"
    kubectl get pods -n $NAMESPACE || echo "No pods found"
}

# Function to cleanup
cleanup() {
    print_warning "This will delete all flix-finder resources"
    read -p "Are you sure you want to cleanup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up resources..."
        kubectl delete -f k8s-flix-finder.yaml --ignore-not-found=true
        print_status "Cleanup completed"
    fi
}

# Main script
main() {
    case ${1:-""} in
        "build")
            check_docker
            build_image
            ;;
        "setup")
            check_kubectl
            setup_namespace
            ;;
        "dev")
            check_kubectl
            check_docker
            build_image
            setup_namespace
            deploy_dev
            ;;
        "prod")
            check_kubectl
            check_docker
            build_image
            deploy_prod
            ;;
        "status")
            check_kubectl
            show_status
            ;;
        "cleanup")
            check_kubectl
            cleanup
            ;;
        *)
            echo "Flix-Finder Kubernetes Deployment Script"
            echo
            echo "Usage: $0 {build|setup|dev|prod|status|cleanup}"
            echo
            echo "Commands:"
            echo "  build   - Build Docker image"
            echo "  setup   - Create namespace and persistent volumes"
            echo "  dev     - Deploy development version (HTTP, NodePort)"
            echo "  prod    - Deploy production version (HTTPS, LoadBalancer)"
            echo "  status  - Show deployment status"
            echo "  cleanup - Remove all resources"
            echo
            echo "Examples:"
            echo "  $0 dev     # Quick development deployment"
            echo "  $0 prod    # Production deployment"
            echo "  $0 status  # Check current status"
            ;;
    esac
}

main "$@"