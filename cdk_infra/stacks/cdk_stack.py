from constructs import Construct
from aws_cdk import (
    Stack, 
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_servicediscovery as servicediscovery,
    aws_ecs_patterns as ecs_patterns,
    CfnOutput
)

class AppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc.from_lookup(self, "vpc-ec667a87", is_default=True)

        # execution_role = iam.Role(self, "ecsTaskExecutionRole", 
        #                             assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"), 
        #                             role_name="ecsTaskExecutionRole")

        # execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"))


        # Create a ECS Cluster
        cluster = ecs.Cluster(self, 'phoenix-cdk-cluster', vpc=vpc)

        # Creating fargate task defination 
        task_definition = ecs.FargateTaskDefinition( self, "mongodb-cdk-td", 
                cpu=512, 
                memory_limit_mib=1024,
                # execution_role=execution_role
                )

        image = ecs.ContainerImage.from_ecr_repository(repository=
                        ecr.Repository.from_repository_name(
                                self, 
                                "773124578159.dkr.ecr.eu-central-1.amazonaws.com/mongodb", 
                                "mongodb")
                                )
        
        container = task_definition.add_container( "mongodb-cdk-container", 
                    image=image,
                    port_mappings=[ecs.PortMapping(container_port=27017, host_port=27017)],
                    logging= ecs.LogDrivers.aws_logs(stream_prefix="my-mongo-log"))

        # Created a public DNS Namespace for the db service exposure
        namespace = servicediscovery.PublicDnsNamespace(self, "mongodb-local", name="phoenixdb.com")

        # Security Group for the fargate service to access the Images
        security_group = ec2.SecurityGroup(self , id="sg-690269" ,security_group_name="cdk-mongodb", vpc=vpc, allow_all_outbound=True )
        security_group.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.all_traffic())

        # Start the fargate service with service discovery endpoint
        # Unable to start the service as the image requests gets denied from the ECR. Tried with other Fargate platform
        # version like 1.3 but still facing the same problem.
        service = ecs.FargateService(self, "mongodb-service",
                cluster=cluster,
                task_definition=task_definition,
                desired_count=1,
                platform_version= ecs.FargatePlatformVersion.LATEST,
                security_groups=[security_group],
                cloud_map_options=ecs.CloudMapOptions(
                    cloud_map_namespace=namespace,
                    dns_record_type=servicediscovery.DnsRecordType.A,
                    dns_ttl= Duration.seconds(60)
                )
            )


        # This whole sections is for creation of the Web app infra after the deployment of the Mongodb.
        #
        # Creating fargate task defination 
        task_definition_webapp = ecs.FargateTaskDefinition( self, "webapp-cdk-td", 
                cpu=1024, 
                memory_limit_mib=2048
                )

        # Fetch the image from the repos.
        image_webapp = ecs.ContainerImage.from_ecr_repository(repository=
                        ecr.Repository.from_repository_name(
                                self, 
                                "773124578159.dkr.ecr.eu-central-1.amazonaws.com/web-app", 
                                "web-app")
                                )

        # Configure the container image with ports and environment variables
        container_webapp = task_definition_webapp.add_container( "webapp-cdk-container", 
                    image=image_webapp,
                    port_mappings=[ecs.PortMapping(container_port=3000, host_port=3000)],
                    environment={"PORT":"3000", "DB_CONNECTION_STRING":"mongodb://test:test@<service_endpoint/publicIP:27017/testDB>"},
                    logging= ecs.LogDrivers.aws_logs(stream_prefix="my-webapp-log"))


        # Network Load balanced Fargate Service
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=image_webapp
            )
        )

        # Network rules for the Fargate Service
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )


       