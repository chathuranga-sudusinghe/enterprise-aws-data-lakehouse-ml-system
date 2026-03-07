variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "project_name" {
  type        = string
  description = "Project name prefix"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "Public subnet CIDRs"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnet CIDRs"
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones"
}

variable "api_container_image" {
  type        = string
  description = "ECR image URI for API container"
}

variable "api_container_port" {
  type        = number
  description = "Container port for API"
  default     = 8000
}

variable "api_cpu" {
  type    = number
  default = 512
}

variable "api_memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 1
}