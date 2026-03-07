aws_region           = "ap-south-1"
project_name         = "enterprise-lakehouse-ml"
environment          = "dev"
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
availability_zones   = ["ap-south-1a", "ap-south-1b"]

api_container_image = "839406385866.dkr.ecr.ap-south-1.amazonaws.com/lakehouse-api:latest"
api_container_port  = 8000
api_cpu             = 512
api_memory          = 1024
desired_count       = 1