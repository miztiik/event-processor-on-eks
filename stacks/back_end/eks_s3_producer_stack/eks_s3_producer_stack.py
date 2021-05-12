from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_logs as _logs
from aws_cdk import core as cdk
from stacks.miztiik_global_args import GlobalArgs


class EksS3ProducerStack(cdk.Stack):
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

        ########################################
        #######                          #######
        #######   Stream Data Producer   #######
        #######                          #######
        ########################################

        app_label = {"app": "sales-event-producer"}

        producer_deployment = {
            "api_version": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "sales-event-producer"},
            "spec": {
                "replicas": 3,
                "selector": {"match_labels": app_label},
                "template": {
                    "metadata": {"labels": app_label},
                    "spec": {
                        "containers": [{
                            "name": "sales-event-producer",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"container_port": 8080}]
                        }
                        ]
                    }
                }
            }
        }

        producer_svc = {
            "api_version": "v1",
            "kind": "Service",
            "metadata": {"name": "sales-event-producer"},
            "spec": {
                "type": "LoadBalancer",
                "ports": [{"port": 80, "target_port": 8080}],
                "selector": app_label
            }
        }

        # apply a kubernetes manifest to the cluster
        sales_event_producer = eks_cluster.add_manifest(
            "miztSalesEventProducer",
            {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {
                    "name": "sales-event-producer",
                    "labels": {"name": "py-producer"}
                },
                "spec": {
                    "containers": [
                        {
                            "name": "hello",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"containerPort": 8080}]
                        }

                    ]
                }
            }
        )

        print(sales_event_producer)

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page.",
        )
