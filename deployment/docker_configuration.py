"""
Akhi Real Estate Intelligence - Deployment Configuration
Docker, Kubernetes, CI/CD pipelines, and infrastructure automation
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import json


class DockerConfiguration:
    """Docker containerization configuration"""
    
    def __init__(self):
        self.app_name = "akhi-real-estate"
        self.version = "2.0.0"
        self.registry = "akhiproperties"
    
    def generate_dockerfile(self) -> str:
        """Generate optimized Dockerfile for production"""
        return f"""
# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    make \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libpq5 \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
        """
    
    def generate_docker_compose(self) -> str:
        """Generate Docker Compose configuration for local development"""
        return f"""
version: '3.8'

services:
  # Main application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {self.app_name}-app
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/akhi_realestate
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
      - ./data:/app/data
      - ./models:/app/models
    networks:
      - akhi-network
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: {self.app_name}-db
    environment:
      - POSTGRES_DB=akhi_realestate
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - akhi-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: {self.app_name}-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - akhi-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: {self.app_name}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf
      - ./deployment/ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - akhi-network
    restart: unless-stopped

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: {self.app_name}-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - akhi-network
    restart: unless-stopped

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: {self.app_name}-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./deployment/grafana-dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    networks:
      - akhi-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  akhi-network:
    driver: bridge
        """
    
    def generate_kubernetes_deployment(self) -> str:
        """Generate Kubernetes deployment configuration"""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {self.app_name}
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {self.app_name}
  template:
    metadata:
      labels:
        app: {self.app_name}
        version: {self.version}
    spec:
      containers:
      - name: {self.app_name}
        image: {self.registry}/{self.app_name}:{self.version}
        ports:
        - containerPort: 8501
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {self.app_name}
  namespace: production
spec:
  selector:
    app: {self.app_name}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {self.app_name}-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {self.app_name}
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
        """
    
    def generate_kubernetes_service(self) -> str:
        """Generate Kubernetes service configuration"""
        return f"""
apiVersion: v1
kind: Service
metadata:
  name: {self.app_name}-service
  namespace: production
  labels:
    app: {self.app_name}
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
    protocol: TCP
    name: http
  selector:
    app: {self.app_name}
  sessionAffinity: ClientIP
        """


class CIConfiguration:
    """CI/CD pipeline configuration"""
    
    def generate_github_actions_workflow(self) -> str:
        """Generate GitHub Actions workflow for CI/CD"""
        return f"""
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ created ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: black --check .
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{{{ secrets.DOCKER_USERNAME }}}}
        password: ${{{{ secrets.DOCKER_PASSWORD }}}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          akhiproperties/akhi-real-estate:latest
          akhiproperties/akhi-real-estate:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
        aws-region: ap-south-1
    
    - name: Deploy to AWS ECS (Staging)
      run: |
        aws ecs update-service --cluster akhi-staging --service akhi-app --force-new-deployment

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
        aws-region: ap-south-1
    
    - name: Deploy to AWS ECS (Production)
      run: |
        aws ecs update-service --cluster akhi-production --service akhi-app --force-new-deployment
    
    - name: Run database migrations
      run: |
        aws ecs run-task --cluster akhi-production --task-definition akhi-migrations

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: akhiproperties/akhi-real-estate:latest
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
        """
    
    def generate_gitlab_ci_pipeline(self) -> str:
        """Generate GitLab CI pipeline configuration"""
        return f"""
stages:
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_IMAGE: ${{CI_REGISTRY_IMAGE}}:${{CI_COMMIT_SHORT_SHA}}
  DOCKER_IMAGE_LATEST: ${{CI_REGISTRY_IMAGE}}:latest

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov flake8 black
  script:
    - flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - black --check .
    - pytest --cov=. --cov-report=xml --cov-report=html
  coverage: '/Total coverage: \d+\.\d+%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u ${{CI_REGISTRY_USER}} -p ${{CI_REGISTRY_PASSWORD}} ${{CI_REGISTRY}}
    - docker build -t $DOCKER_IMAGE -t $DOCKER_IMAGE_LATEST .
    - docker push $DOCKER_IMAGE
    - docker push $DOCKER_IMAGE_LATEST
  only:
    - main
    - develop

deploy-staging:
  stage: deploy-staging
  image: alpine/k8s:1.28.0
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/akhi-app akhi-app=$DOCKER_IMAGE
    - kubectl rollout status deployment/akhi-app
  environment:
    name: staging
    url: https://staging.akhiproperties.com
  only:
    - develop

deploy-production:
  stage: deploy-production
  image: alpine/k8s:1.28.0
  script:
    - kubectl config use-context production
    - kubectl set image deployment/akhi-app akhi-app=$DOCKER_IMAGE
    - kubectl rollout status deployment/akhi-app
  environment:
    name: production
    url: https://akhiproperties.com
  when: manual
  only:
    - main
        """


class InfrastructureConfiguration:
    """Infrastructure as Code configuration"""
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for AWS infrastructure"""
        return f"""
# Terraform configuration for AWS infrastructure

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "ap-south-1"
}}

# VPC Configuration
resource "aws_vpc" "main" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = {{
    Name        = "akhi-vpc"
    Environment = "production"
    Project     = "akhi-real-estate"
  }}
}}

# Subnets
resource "aws_subnet" "public" {{
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index + 1}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {{
    Name = "akhi-public-subnet-${{count.index + 1}}"
  }}
}}

resource "aws_subnet" "private" {{
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${{count.index + 4}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  
  tags = {{
    Name = "akhi-private-subnet-${{count.index + 1}}"
  }}
}}

# Database Subnet Group
resource "aws_db_subnet_group" "main" {{
  name       = "akhi-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = {{
    Name = "akhi-db-subnet-group"
  }}
}}

# RDS PostgreSQL
resource "aws_db_instance" "main" {{
  identifier     = "akhi-production-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 1000
  max_allocated_storage = 5000
  storage_type         = "gp3"
  storage_encrypted     = true
  
  db_name  = "akhi_realestate"
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"
  
  performance_insights_enabled = true
  monitoring_interval          = 60
  
  skip_final_snapshot = false
  
  tags = {{
    Name = "akhi-production-db"
  }}
}}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {{
  name       = "akhi-cache-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}}

resource "aws_elasticache_replication_group" "main" {{
  replication_group_id = "akhi-redis-cluster"
  description           = "Akhi Real Estate Redis Cluster"
  node_type             = "cache.r6g.large"
  num_cache_clusters    = 3
  engine                = "redis"
  engine_version        = "7.0"
  port                  = 6379
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  automatic_failover_enabled = true
  
  tags = {{
    Name = "akhi-redis-cluster"
  }}
}}

# ECS Cluster
resource "aws_ecs_cluster" "main" {{
  name = "akhi-production-cluster"
  
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {{
  family                   = "akhi-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"
  
  container_definitions = jsonencode([
    {{
      name      = "akhi-app"
      image     = "akhiproperties/akhi-real-estate:latest"
      cpu       = 2048
      memory    = 4096
      essential = true
      
      port_mappings = [
        {{
          containerPort = 8501
          protocol      = "tcp"
        }}
      ]
      
      environment = [
        {{
          name  = "ENVIRONMENT"
          value = "production"
        }}
      ]
      
      secrets = [
        {{
          name      = "DATABASE_URL"
          valueFrom = aws_secretsmanager_secret.database_url.arn
        }}
      ]
    }}
  ])
}}

# ECS Service
resource "aws_ecs_service" "app" {{
  name            = "akhi-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  
  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }}
  
  load_balancer {{
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "akhi-app"
    container_port   = 8501
  }}
}}

# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "akhi-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = true
  
  tags = {{
    Name = "akhi-alb"
  }}
}}

resource "aws_lb_target_group" "app" {{
  name        = "akhi-app-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {{
    enabled             = true
    path                = "/_stcore/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }}
}}

# Security Groups
resource "aws_security_group" "app" {{
  name        = "akhi-app-sg"
  description = "Security group for Akhi app"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

resource "aws_security_group" "alb" {{
  name        = "akhi-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.main.id
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# CloudWatch
resource "aws_cloudwatch_log_group" "app" {{
  name = "/ecs/akhi-app"
}}

# Secrets Manager
resource "aws_secretsmanager_secret" "database_url" {{
  name = "akhi/database-url"
}}

resource "aws_secretsmanager_secret_version" "database_url" {{
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}}

# Variables
variable "db_username" {{
  description = "Database username"
  type        = string
  sensitive   = true
}}

variable "db_password" {{
  description = "Database password"
  type        = string
  sensitive   = true
}}

variable "database_url" {{
  description = "Database connection URL"
  type        = string
  sensitive   = true
}}

# Outputs
output "alb_dns_name" {{
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}}

output "db_endpoint" {{
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}}
        """
    
    def generate_ansible_playbook(self) -> str:
        """Generate Ansible playbook for server configuration"""
        return f"""
---
- name: Akhi Real Estate Infrastructure Setup
  hosts: webservers
  become: yes
  vars:
    app_name: akhi-real-estate
    app_version: 2.0.0
    docker_registry: akhiproperties
  
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
    
    - name: Install Docker
      apt:
        name: docker.io
        state: present
    
    - name: Install Docker Compose
      apt:
        name: docker-compose
        state: present
    
    - name: Start Docker service
      service:
        name: docker
        state: started
        enabled: yes
    
    - name: Create application directory
      file:
        path: /opt/{{ app_name }}
        state: directory
        mode: '0755'
    
    - name: Copy Docker Compose file
      copy:
        src: docker-compose.yml
        dest: /opt/{{ app_name }}/docker-compose.yml
    
    - name: Pull latest Docker image
      docker_image:
        name: {{ docker_registry }}/{{ app_name }}:{{ app_version }}
        source: pull
    
    - name: Start application with Docker Compose
      docker_compose:
        project_src: /opt/{{ app_name }}
        state: present
    
    - name: Setup Nginx reverse proxy
      apt:
        name: nginx
        state: present
    
    - name: Copy Nginx configuration
      copy:
        src: nginx.conf
        dest: /etc/nginx/sites-available/{{ app_name }}
    
    - name: Enable Nginx site
      file:
        src: /etc/nginx/sites-available/{{ app_name }}
        dest: /etc/nginx/sites-enabled/{{ app_name }}
        state: link
    
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
    
    - name: Setup firewall rules
      ufw:
        rule: allow
        port: '80,443,22'
        proto: tcp
    
    - name: Enable firewall
      ufw:
        state: enabled
        policy: deny
    
    - name: Setup monitoring agent
      apt:
        name: prometheus-node-exporter
        state: present
    
    - name: Start monitoring agent
      service:
        name: prometheus-node-exporter
        state: started
        enabled: yes
        """


class DeploymentSystem:
    """
    Main deployment system combining all configurations
    """
    
    def __init__(self):
        self.docker_config = DockerConfiguration()
        self.ci_config = CIConfiguration()
        self.infra_config = InfrastructureConfiguration()
    
    def generate_complete_deployment_package(self) -> Dict[str, str]:
        """Generate complete deployment package"""
        return {
            'dockerfile': self.docker_config.generate_dockerfile(),
            'docker_compose': self.docker_config.generate_docker_compose(),
            'kubernetes_deployment': self.docker_config.generate_kubernetes_deployment(),
            'kubernetes_service': self.docker_config.generate_kubernetes_service(),
            'github_actions': self.ci_config.generate_github_actions_workflow(),
            'gitlab_ci': self.ci_config.generate_gitlab_ci_pipeline(),
            'terraform_config': self.infra_config.generate_terraform_config(),
            'ansible_playbook': self.infra_config.generate_ansible_playbook()
        }
    
    def generate_deployment_guide(self) -> str:
        """Generate comprehensive deployment guide"""
        return f"""
# Akhi Real Estate Intelligence - Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.28+ (for production)
- AWS CLI (for cloud deployment)
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/akhiproperties/akhi-real-estate.git
cd akhi-real-estate
```

### 2. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start Services with Docker Compose
```bash
docker-compose up -d
```

### 5. Run Database Migrations
```bash
docker-compose exec app python -m alembic upgrade head
```

### 6. Access Application
- Main Application: http://localhost:8501
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## Production Deployment

### AWS Infrastructure Setup

1. **Configure AWS Credentials**
```bash
aws configure
```

2. **Initialize Terraform**
```bash
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

3. **Build and Push Docker Images**
```bash
docker build -t akhiproperties/akhi-real-estate:latest .
docker push akhiproperties/akhi-real-estate:latest
```

4. **Deploy to Kubernetes**
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### CI/CD Pipeline

The CI/CD pipeline automatically:
- Runs tests on every push
- Builds Docker images
- Deploys to staging on develop branch
- Deploys to production on main branch
- Runs security scans
- Performs health checks

### Monitoring Setup

1. **Prometheus** - Metrics collection
2. **Grafana** - Visualization and dashboards
3. **CloudWatch** - AWS-native monitoring
4. **Sentry** - Error tracking and alerting

### Backup Strategy

- **Database**: Daily automated backups, 30-day retention
- **Redis**: Weekly snapshots
- **Application**: Version control and rollback capability

### Scaling Strategy

- **Horizontal**: Auto-scaling based on CPU/memory
- **Vertical**: Instance size adjustments
- **Database**: Read replicas for analytics queries
- **CDN**: CloudFront for static assets

## Security Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Database encryption enabled
- [ ] API authentication configured
- [ ] Firewall rules configured
- [ ] Security scanning enabled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting setup

## Troubleshooting

### Database Connection Issues
```bash
docker-compose logs db
docker-compose exec db psql -U postgres -d akhi_realestate
```

### Application Not Starting
```bash
docker-compose logs app
docker-compose exec app streamlit --version
```

### Performance Issues
```bash
# Check resource usage
docker stats
# Check logs
docker-compose logs --tail=100 app
```

## Support

For deployment issues, contact: devops@akhiproperties.com
        """


# Initialize global instances
docker_configuration = DockerConfiguration()
ci_configuration = CIConfiguration()
infrastructure_configuration = InfrastructureConfiguration()
deployment_system = DeploymentSystem()