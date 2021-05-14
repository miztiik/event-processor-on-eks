from aws_cdk import aws_eks as _eks
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

        # The EKS cluster is used throughout, so we add it here
        self.eks_cluster = eks_cluster

        ########################################
        #######                          #######
        #######   Stream Data Producer   #######
        #######                          #######
        ########################################

        app_01_name = "sales-event-producer"
        app_01_label = {"app": "sales-event-producer"}

        producer_ns = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                    "name": f"{app_01_name}-ns",
                    "labels": {
                        "name": f"{app_01_name}-ns"
                    }
            }
        }

        producer_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{app_01_name}-svc",
                "namespace": f"{app_01_name}-ns"
            },
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": app_01_label},
                "template": {
                    "metadata": {"labels": app_01_label},
                    "spec": {
                        "containers": [{
                            "name": f"{app_01_name}-svc",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"containerPort": 8080, "protocol": "TCP"}]
                        }
                        ]
                    }
                }
            }
        }

        producer_svc = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app_01_name}-svc",
                "namespace": f"{app_01_name}-ns"
            },
            "spec": {
                "type": "LoadBalancer",
                "ports": [{"port": 80, "targetPort": 8080}],
                "selector": app_01_label
            }
        }

        # apply a kubernetes manifest to the cluster
        sales_event_producer = _eks.KubernetesManifest(
            self,
            "miztSalesEventProducerSvc",
            cluster=eks_cluster,
            manifest=[
                producer_ns,
                producer_deployment,
                producer_svc
            ]
        )

        ####### APP 02 #######
        app_02_name = "sales-event-producer-02"
        app_02_label = {"app": "sales-event-producer-02"}

        producer_ns_02 = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                    "name": f"{app_02_name}-ns",
                    "labels": {
                        "name": f"{app_02_name}-ns"
                    }
            }
        }
        """
        {
            "apiVersion": "batch/v1beta1",
            "kind": "CronJob",
            "metadata": {
                "name": "cronjob2"
            },
            "spec": {
                "schedule": "*/1 * * * *",
                "concurrencyPolicy": "Allow",
                "jobTemplate": {
                    "spec": {
                        "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "cronjob",
                                    "image": "busybox",
                                    "args": [
                                    "/bin/sh",
                                    "-c",
                                    "date; echo sleeping....; sleep 90s; echo exiting...;"
                                    ]
                                }
                            ],
                            "restartPolicy": "Never"
                        }
                        }
                    }
                }
            }
            }

        """

        producer_deployment_02 = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{app_02_name}-svc",
                "namespace": f"{app_02_name}-ns"
            },
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": f"{app_02_name}-svc",
                                "image": "perl",
                                "command": [
                                    "perl",
                                    "-Mbignum=bpi",
                                    "-wle",
                                    "print bpi(2000)"
                                ]
                            }
                        ],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        sales_event_producer_02 = _eks.KubernetesManifest(
            self,
            "miztSalesEventProducerSvc02",
            cluster=eks_cluster,
            manifest=[
                producer_ns_02,
                producer_deployment_02
            ]
        )

        ####### APP 02 #######
        app_03_name = "sale-events-producer-03"
        app_03_label = {"app": "sales-event-producer-03"}

        producer_ns_03 = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                    "name": f"{app_03_name}-ns",
                    "labels": {
                        "name": f"{app_03_name}-ns"
                    }
            }
        }
        producer_deployment_03 = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{app_03_name}-svc",
                "namespace": f"{app_03_name}-ns"
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": app_03_label},
                "template": {
                    "metadata": {"labels": app_03_label},
                    "spec": {
                        "containers": [{
                            "name": f"{app_03_name}-svc",
                            "image": "python:3.8.10-alpine",
                            "command": ["sh", "-c"],
                            "args":
                            [
                                "apk get boto3;",
                                "wget https://raw.githubusercontent.com/miztiik/event-processor-on-eks/master/stacks/back_end/eks_s3_producer_stack/lambda_src/stream_data_producer.py;",
                                "python3 stream_data_producer.py;",
                                "sh"
                            ],
                            "env": [
                                {
                                    "name": "S3_BKT_NAME",
                                    "value": "sales-events-bkt-stack-databucketd8691f4e-uaxjd1d2l831"
                                },
                                {
                                    "name": "S3_PREFIX",
                                    "value": "sales_events"
                                }
                            ]
                        }
                        ]
                    }
                }
            }
        }

        producer_svc_03 = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{app_03_name}-svc",
                "namespace": f"{app_03_name}-ns"
            },
            "spec": {
                "ports": [{"port": 80, "targetPort": 8080}],
                "selector": app_03_label
            }
        }

        # apply a kubernetes manifest to the cluster
        sales_event_producer_03 = _eks.KubernetesManifest(
            self,
            "miztSalesEventProducerSvc03",
            cluster=eks_cluster,
            manifest=[
                producer_ns_03,
                producer_deployment_03,
                producer_svc_03
            ]
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page.",
        )

    # Helper functions
    def create_namespace(self, name: str) -> _eks.KubernetesManifest:
        return self.eks_cluster.add_manifest(
            name,
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": name,
                    "labels": {
                        "name": name
                    }
                }
            }
        )
