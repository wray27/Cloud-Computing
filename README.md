Horizontal Scaling for an Embarrassingly Parallel Task: Blockchain Proof-of-Work in the Cloud
===============

The Cloud Nonce Discovery (CND) system,  utilizes horizontal scaling hosted by Amazon Web Service's (AWS) Elastic Compute Cloud (EC2) for a parallel computational task. The computational task is to compute a Blockchain proof-of-work.

## Setup

* The required version of python is **_Python 3.6.x and up_**.

* Start by installing aws cli and boto3 python package and make sure you have an aws account created.

* Then run the aws configure command inputting your own AWS Access Key ID and AWS Secret Access Key. Please ensure your default region is set to **_eu-west-2_**.

``` 
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: eu-west-2
Default output format [None]: json
```

## Running the Code

* Running the code in the cloud can be done by running the cloud_access.py code

*  A table of command line options are given below

<!-- parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code", choices=range(51), required=False, type=int, default=0)
parser.add_argument("-D", "--difficulty", help="difficulty",choices=range(256), type=int, default=0, required=False)
parser.add_argument("-L", "--confidence", help="confidence level between 0 and 1", default=1, type=float, required=False)
parser.add_argument("-T", "--time", help="time before stopping", type=int, default= 300, required=False)
parser.add_argument("-P", "--performance", help="runs a performance test", action='store_true', default=False, required=False) -->

| Short Argument| Long Argument|Description|Type |Required|
|:-------------|:-------------|:------------|:---------|:----------|
|-N|--number-of-vms|Allows a user to specify the number of VMs to run the code. By default is 0, and CND will automatically calculate a desire number of virtual machines to use.|int| No|
| col 2 is       | centered       |   $12        |  x    |No    |
| zebra stripes  | are neat       |    $1        |   y   | No       |


``` 
$ python cloud_access -N 
