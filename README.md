# Phoenix Application Problem
This problem is about to create a production ready infrastructure for the Phoenix Application.

## Problem

The development team has released the phoenix application code.
Your task, if you want to accept it, is to create the production infrastructure
for the Phoenix application. You must pay attention to some unwanted features
that were introduced during development. In particular:

- `GET /crash` kill the application process
- `GET /generatecert` is not optimized and creates resource consumption peaks

## Problem Requirements

1. Automate the creation of the infrastructure and the setup of the application.
2. Recover from crashes. Implement a method autorestart the service on crash
3. Backup the logs and database with rotation of 7 days
4. Notify any CPU peak
5. Implements a CI/CD pipeline for the code
6. Scale when the number of request are greater than 100 req /min

## Solution
I have tried to setup the following solution for the problem : 

    1. Github: code repo for the all the build including IaC code.
    2. AWS ECR: for the private docker image repository  
    3. AWS Fargate: for docker containers deployment (Web-app server & MongoDB)  
    4. AWS Application Load Balancer & Target Group: for Container Orchestration  
    5. ECS Fargate Service Autoscaling: for implementing containers autoscaling  
    6. CloudWatch:  
           - for containers logs   
           - containers autoscaling triggering  
    8.  AWS Route53: 
           - for public DNS
           - for AWS Fargate Services Communication using a private/public hosted zone
    9.  GitHub Workflow Action: for CI/CD  
    10. AWS CDK: for IaC code 

Problems:
    1. I got stuck with service descovery endpoint. Only way I can access the by database node is via public IP, which was not sustainable as the Fargate nodes are ephemeral in nature and changed IP will cause connection disruption.
    2. Unable to fetch ERC images as the requests gets timed out. Still looking into this.


## How to use.
1. Github workflow will push the code to AWS ECR one every merge or commit to main branch. Credentials are secured stored at envionmental variables. 
2. Once the docker images are pushed to ECR repos then you can use the code in "cdk_infra" folder to create the infrastructure. Again creditials can be configure in .aws/credentials file in local environment. 

```
cd cdk_infra

source .venv/bin/activate
python -m pip install -r requirements.txt

cdk deploy
```

# **AWS ECS Fargate :**  
* Created two seperate dockerfiles, one for the **Node server** and the other one was for **MongoDB**, after building both of them, they were pushed to **ECR**.
* Then I've created two task definitions one for each container using the images already pushed to ECR, Created an **ECS Fargate Cluster** and then a Service for each task Definition.
* For the Node server Fargate Service (**phoenixKataService**), I've created an **Application load balancer** which will orchestrate the service tasks (in case of multiple tasks) and will manage tasks health checks, so in case of failure a new task will be created (for example when calling the **/crash** api) the nodes will restart in 30 sec.
* For Autoscaling; I've created the following role to scale the node server (adding more **Fargate Tasks**) in case of increated traffic. I can upscale based on CPU and Memory utilization but based on number of request, I need to look into it once I have fixed the service discovery problem.
* Regarding Containers communication, as mentioned above, I've created a public hosed zone with **AWS Route53**, 
and by using **Service discovery integration** in **ECS Fargate** service a record has been created for the Service running **MongoDB** tasks.


## Future Improvements
1. Try implementing this architecture in AWS EKS or any other K8's clusters.
2. Implement a orchestration tool for fully automated pipeline like AWS Codepipline/codebuild.