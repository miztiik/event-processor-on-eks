from aws_cdk import aws_eks as _eks
from aws_cdk import aws_sqs as _sqs
from aws_cdk import core as cdk

from stacks.miztiik_global_args import GlobalArgs


class EksSqsProducerStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        stack_log_level: str,
        eks_cluster,
        sales_event_bkt,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add your stack resources below):

        self.reliable_q = _sqs.Queue(
            self,
            "reliableQueue01",
            delivery_delay=cdk.Duration.seconds(2),
            queue_name=f"reliable_message_q",
            retention_period=cdk.Duration.days(2),
            visibility_timeout=cdk.Duration.seconds(30)
        )

        # Grant our EKS Node Producer privileges to write to SQS
        # Due to cyclic dependency should be done before the EKS cluster is created
        # self.reliable_q.grant_send_messages(_eks_node_role)

        ########################################
        #######                          #######
        #######   Stream Data Producer   #######
        #######                          #######
        ########################################

        app_grp_name = "sales-events-producer"
        app_grp_label = {"app": f"{app_grp_name}"}

        app_grp_ns = eks_cluster.add_manifest(
            f"{app_grp_name}-ns-01",
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                        "name": f"{app_grp_name}-ns",
                        "labels": {
                            "name": f"{app_grp_name}-ns"
                        }
                }
            }
        )

        app_01_producer_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "hello-world-svc",
                "namespace": f"{app_grp_name}-ns"
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": app_grp_label},
                "template": {
                    "metadata": {"labels": app_grp_label},
                    "spec": {
                        "containers": [{
                            "name": "hello-world",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"containerPort": 8080, "protocol": "TCP"}]
                        }
                        ]
                    }
                }
            }
        }

        app_01_producer_svc = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "hello-world-svc",
                "namespace": f"{app_grp_name}-ns"
            },
            "spec": {
                "type": "LoadBalancer",
                "ports": [{"port": 80, "targetPort": 8080}],
                "selector": app_grp_label
            }
        }

        # apply a kubernetes manifest to the cluster
        app_01_manifest = _eks.KubernetesManifest(
            self,
            "miztSalesEventproducerSvc",
            cluster=eks_cluster,
            manifest=[
                app_01_producer_deployment,
                app_01_producer_svc
            ]
        )

        app_01_manifest.node.add_dependency(
            app_grp_ns)

        ####### APP 02 #######

        app_02_producer_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{app_grp_name}",
                "namespace": f"{app_grp_name}-ns"
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": app_grp_label},
                "template": {
                    "metadata": {"labels": app_grp_label},
                    "spec": {
                        "containers": [
                            {
                                "name": f"{app_grp_name}-02-svc",
                                "image": "python:3.8.10-alpine",
                                "command": [
                                    "sh",
                                    "-c"
                                ],
                                "args": [
                                    "wget https://raw.githubusercontent.com/miztiik/event-processor-on-eks/master/stacks/back_end/eks_sqs_producer_stack/lambda_src/stream_data_producer.py;pip3 install --user boto3;python3 stream_data_producer.py;"
                                ],
                                "env": [
                                    {
                                        "name": "STORE_EVENTS_BKT",
                                        "value": f"{sales_event_bkt.bucket_name}"
                                    },
                                    {
                                        "name": "S3_PREFIX",
                                        "value": "sales_events"
                                    },
                                    {
                                        "name": "RELIABLE_QUEUE_NAME",
                                        "value": f"{self.reliable_q.queue_name}"
                                    },
                                    {
                                        "name": "AWS_REGION",
                                        "value": f"{cdk.Aws.REGION}"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        # apply a kubernetes manifest to the cluster
        app_02_manifest = _eks.KubernetesManifest(
            self,
            "miztSalesEventproducer02Svc",
            cluster=eks_cluster,
            manifest=[
                app_02_producer_deployment,
            ]
        )

        app_02_manifest.node.add_dependency(
            app_grp_ns)

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page.",
        )
