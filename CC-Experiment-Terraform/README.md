# Terraform Multiple Docker Containers

## Objective
To use Terraform to create and manage multiple Docker containers.

## Tools and Technologies
- Terraform
- Docker Desktop
- Nginx (Alpine)
- Python 3.12
- Visual Studio Code

## Project Description
This experiment uses Terraform to provision two Docker containers:

1. **Nginx Container**
   - Docker image: `nginx:alpine`
   - Container name: `terraform-nginx`
   - Host port: `8080`
   - Container port: `80`

2. **Python Container**
   - Docker image: `python:3.12-slim`
   - Container name: `terraform-python`
   - Runs a Python HTTP server on port `8000`
   - Host port: `8081`
   - Container port: `8000`

## Prerequisites
- Docker Desktop installed and running.
- Terraform installed.
- Git installed.

## Execution Steps

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Validate the configuration:
   ```bash
   terraform validate
   ```

3. Format the Terraform files:
   ```bash
   terraform fmt
   ```

4. View the execution plan:
   ```bash
   terraform plan
   ```

5. Create the Docker containers:
   ```bash
   terraform apply
   ```

6. Verify running containers:
   ```bash
   docker ps
   ```

## Browser Verification

- Nginx: http://localhost:8080
- Python HTTP Server: http://localhost:8081

## Expected Result
Terraform successfully creates two Docker images and two Docker containers. Both containers run simultaneously and can be accessed through their respective host ports.

## Author
Krupa1310
