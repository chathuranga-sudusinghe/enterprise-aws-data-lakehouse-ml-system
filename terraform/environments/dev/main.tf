locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  tags                 = local.common_tags
}

module "s3" {
  source = "../../modules/s3"

  bucket_name = "${local.name_prefix}-data"
  tags        = local.common_tags
}

module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}

module "alb" {
  source = "../../modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  container_port    = var.api_container_port
  tags              = local.common_tags
}

module "ecs" {
  source = "../../modules/ecs"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  private_subnet_ids      = module.vpc.private_subnet_ids
  ecs_task_execution_role = module.iam.ecs_task_execution_role_arn
  ecs_task_role           = module.iam.ecs_task_role_arn
  target_group_arn        = module.alb.target_group_arn
  alb_security_group_id   = module.alb.alb_security_group_id
  container_image         = var.api_container_image
  container_port          = var.api_container_port
  cpu                     = var.api_cpu
  memory                  = var.api_memory
  desired_count           = var.desired_count
  tags                    = local.common_tags
}