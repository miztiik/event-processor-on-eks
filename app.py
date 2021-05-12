#!/usr/bin/env python3

from aws_cdk import core as cdk

from stacks.back_end.vpc_stack import VpcStack
from stacks.back_end.s3_stack.s3_stack import S3Stack
from stacks.back_end.eks_cluster_stack.eks_cluster_stack import EksClusterStack
from stacks.back_end.eks_s3_producer_stack.eks_s3_producer_stack import EksS3ProducerStack

app = cdk.App()

# S3 Bucket to hold our sales events
sales_events_bkt_stack = S3Stack(
    app,
    # f"{app.node.try_get_context('project')}-sales-events-bkt-stack",
    f"sales-events-bkt-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: S3 Bucket to hold our sales events"
)


# VPC Stack for hosting Secure workloads & Other resources
vpc_stack = VpcStack(
    app,
    # f"{app.node.try_get_context('project')}-vpc-stack",
    "eks-cluster-vpc-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: Custom Multi-AZ VPC"
)

# EKS Cluster to process event processor
eks_cluster_stack = EksClusterStack(
    app,
    f"eks-cluster-stack",
    stack_log_level="INFO",
    vpc=vpc_stack.vpc,
    description="Miztiik Automation: EKS Cluster to process event processor"
)


# S3 Sales Event Data Producer on EKS Pods
sales_events_producer_stack = EksS3ProducerStack(
    app,
    f"sales-events-producer-stack",
    stack_log_level="INFO",
    eks_cluster=eks_cluster_stack.eks_cluster_1,
    sales_event_bkt=sales_events_bkt_stack.data_bkt,
    description="Miztiik Automation: S3 Sales Event Data Producer on EKS Pods")

# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(
                k, v, apply_to_launched_instances=True, priority=300)

app.synth()
