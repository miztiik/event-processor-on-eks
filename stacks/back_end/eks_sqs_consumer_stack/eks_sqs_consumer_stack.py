from aws_cdk import aws_eks as _eks
from aws_cdk import core as cdk

from stacks.miztiik_global_args import GlobalArgs


class EksSqsConsumerStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        stack_log_level: str,
        eks_cluster,
        reliable_q,
        sales_event_bkt,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add your stack resources below):

        ########################################
        #######                          #######
        #######   Stream Data consumer   #######
        #######                          #######
        ########################################

        app_grp_name = "sales-events-consumer"
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

        app_01_consumer_deployment = {
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
                                "name": f"{app_grp_name}",
                                "image": "python:3.8.10-alpine",
                                "command": [
                                    "sh",
                                    "-c"
                                ],
                                "args": [
                                    "wget https://raw.githubusercontent.com/miztiik/event-processor-on-eks/master/stacks/back_end/eks_sqs_consumer_stack/lambda_src/stream_data_consumer.py;pip3 install --user boto3;python3 stream_data_consumer.py;"
                                ],
                                "env":
                                [
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
                                        "value": f"{reliable_q.queue_name}"
                                    },
                                    {
                                        "name": "AWS_REGION",
                                        "value": f"{cdk.Aws.REGION}"
                                    },
                                    {
                                        "name": "MAX_MSGS_PER_BATCH",
                                        "value": "5"
                                    },
                                    {
                                        "name": "MSG_POLL_BACKOFF",
                                        "value": "2"
                                    },
                                    {
                                        "name": "MSG_PROCESS_DELAY",
                                        "value": "10"
                                    },
                                    {
                                        "name": "TOT_MSGS_TO_PROCESS",
                                        "value": "10000"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        # apply a kubernetes manifest to the cluster
        app_01_manifest = _eks.KubernetesManifest(
            self,
            "miztSalesEventConsumerSvc",
            cluster=eks_cluster,
            manifest=[
                app_01_consumer_deployment
            ]
        )

        app_01_manifest.node.add_dependency(
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
