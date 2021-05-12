# Simple EKS Cluster

Can you show the developers in Miztiik Unicorn Corp how to launch a kubernetes cluster in AWS and use `kubectl` to interact with the cluster.

## 🎯 Solutions

In this demo, let us launch a EKS[1] cluster in a custom VPC using AWS CDK. The cluster will have the following attributes

- **VPC**:
  - 2-AZ Subnets with Public, Private and Isolated Subnets.
  - 1 NAT GW for internet access from private subnets
- **EKS**
  - The control pane is launched with public access. _i.e_ the cluster can be access without a bastion host
  - `c_admin` IAM role added to _aws-auth_ configMap to administer the cluster from CLI
  - One managed EC2 node group
    - Launch template Two `t3.medium` instances running Amazon Linux 2
    - Auto-scaling Group with `2` desired instances.

![Miztiik Automation: Simple EKS Cluster Architecture](images/miztiik_automation_event_simple_eks_cluster_00.png)

1.  ## 🧰 Prerequisites

    This demo, instructions, scripts and cloudformation template is designed to be run in `us-east-1`. With few modifications you can try it out in other regions as well(_Not covered here_).

    - 🛠 AWS CLI Installed & Configured - [Get help here](https://youtu.be/TPyyfmQte0U)
    - 🛠 AWS CDK Installed & Configured - [Get help here](https://www.youtube.com/watch?v=MKwxpszw0Rc)
    - 🛠 Python Packages, _Change the below commands to suit your OS, the following is written for amzn linux 2_
      - Python3 - `yum install -y python3`
      - Python Pip - `yum install -y python-pip`
      - Virtualenv - `pip3 install virtualenv`

1.  ## ⚙️ Setting up the environment

    - Get the application code

      ```bash
      git clone https://github.com/miztiik/simple-eks-cluster
      cd simple-eks-cluster
      ```

1.  ## 🚀 Prepare the dev environment to run AWS CDK

    We will use `cdk` to make our deployments easier. Lets go ahead and install the necessary components.

    ```bash
    # You should have npm pre-installed
    # If you DONT have cdk installed
    npm install -g aws-cdk

    # Make sure you in root directory
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    ```

    The very first time you deploy an AWS CDK app into an environment _(account/region)_, you’ll need to install a `bootstrap stack`, Otherwise just go ahead and deploy using `cdk deploy`.

    ```bash
    cdk bootstrap
    cdk ls
    # Follow on screen prompts
    ```

    You should see an output of the available stacks,

    ```bash
    eks-cluster-vpc-stack
    eks-cluster-stack
    ```

1.  ## 🚀 Deploying the application

    Let us walk through each of the stacks,

    - **Stack: eks-cluster-stack**
      As we are starting out a new cluster, we will use most default. No logging is configured or any add-ons.

      Initiate the deployment with the following command,

      ```bash
      cdk deploy eks-cluster-vpc-stack
      cdk deploy eks-cluster-stack
      ```

      After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `*ConfigCommand*` that allows yous to interact with your cluster using `kubectl`

1.  ## 🔬 Testing the solution

    1. **Connect To EKS Cluster Consumer**:

       Connect the `KafkaAdminInstance` instance using SSM Session Manager<sup>[3]</sup>. Navigate to `/var/kafka/` directory. Kafka has been preinstalled and _if_ user-data script had ran successfully, we should have a kafka topic created automatically for us. You can check the user data script status in logs on the instance at `/var/log/miztiik-automation-*.log`. The same log had been pushed to cloudwatch as well.

       Let us verify the kafka topic exists

       ```bash
        # Set kubeconfig
        aws eks update-kubeconfig \
          --name 1_cdk_c \
          --region us-east-1 \
          --role-arn arn:aws:iam::111122223333:role/eks-cluster-stack-cAdminRole655A13CE-XBF2V3PPV4FI

       # List nodes
       kubectl get no

       # Sample Output
       (.venv) simple-eks-cluster]# kubectl get no
       NAME                          STATUS   ROLES    AGE   VERSION
       ip-10-10-0-90.ec2.internal    Ready    <none>   36h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   36h   v1.18.9-eks-d1db3c
       ```

       ```sh
       # Watching the status of nodes,
       (.venv) simple-eks-cluster]# kubectl get nodes --watch
       NAME                          STATUS   ROLES    AGE   VERSION
       ip-10-10-0-90.ec2.internal    Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   15h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-0-90.ec2.internal    Ready    <none>   16h   v1.18.9-eks-d1db3c
       ip-10-10-1-229.ec2.internal   Ready    <none>   16h   v1.18.9-eks-d1db3c
       ```

       You may face an error on the GUI[2]. For example, _You may not be able to see workloads or nodes in your AWS Management Console_.
       Make sure you using the same user/role you used to deploy the cluster. If they are different then you need to update the console user to kubernetes configmap. This doc[3] has the instructions for the same

1.  ## 📒 Conclusion

    Here we have demonstrated how to use AWS for launching highly available EKS cluster. You can extend this launching your workloads using `service` and `deployment` manifests.

1.  ## 🧹 CleanUp

    If you want to destroy all the resources created by the stack, Execute the below command to delete the stack, or _you can delete the stack from console as well_

    - Resources created during [Deploying The Application](#-deploying-the-application)
    - Delete CloudWatch Lambda LogGroups
    - _Any other custom resources, you have created for this demo_

    ```bash
    # Delete from cdk
    cdk destroy

    # Follow any on-screen prompts

    # Delete the CF Stack, If you used cloudformation to deploy the stack.
    aws cloudformation delete-stack \
      --stack-name "MiztiikAutomationStack" \
      --region "${AWS_REGION}"
    ```

    This is not an exhaustive list, please carry out other necessary steps as maybe applicable to your needs.

## 📌 Who is using this

This repository aims to show how to use AWS EKS to new developers, Solution Architects & Ops Engineers in AWS. Based on that knowledge these Udemy [course #1][102], [course #2][101] helps you build complete architecture in AWS.

### 💡 Help/Suggestions or 🐛 Bugs

Thank you for your interest in contributing to our project. Whether it is a bug report, new feature, correction, or additional documentation or solutions, we greatly value feedback and contributions from our community. [Start here](/issues)

### 👋 Buy me a coffee

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q41QDGK) Buy me a [coffee ☕][900].

### 📚 References

1. [AWS Docs: EKS Getting Started][1]
1. [AWS EKS Troubleshooting - EKS IAM][2]
1. [AWS EKS Troubleshooting - Resolve user/role does not have access to objects][3]
1. [AWS EKS Troubleshooting - Resolve an unauthorized server][4]

### 🏷️ Metadata

![miztiik-success-green](https://img.shields.io/badge/Miztiik:Automation:Level-200-green)

**Level**: 200

[1]: https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html
[2]: https://docs.aws.amazon.com/eks/latest/userguide/troubleshooting_iam.html
[3]: https://aws.amazon.com/premiumsupport/knowledge-center/eks-kubernetes-object-access-error/
[4]: https://aws.amazon.com/premiumsupport/knowledge-center/eks-api-server-unauthorized-error/
[100]: https://www.udemy.com/course/aws-cloud-security/?referralCode=B7F1B6C78B45ADAF77A9
[101]: https://www.udemy.com/course/aws-cloud-security-proactive-way/?referralCode=71DC542AD4481309A441
[102]: https://www.udemy.com/course/aws-cloud-development-kit-from-beginner-to-professional/?referralCode=E15D7FB64E417C547579
[103]: https://www.udemy.com/course/aws-cloudformation-basics?referralCode=93AD3B1530BC871093D6
[899]: https://www.udemy.com/user/n-kumar/
[900]: https://ko-fi.com/miztiik
[901]: https://ko-fi.com/Q5Q41QDGK
