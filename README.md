Horizontal Scaling for an Embarrassingly Parallel Task: Blockchain Proof-of-Work in the Cloud
===============

The Cloud Nonce Discovery (CND) system,  utilizes horizontal scaling hosted by Amazon Web Service's (AWS) Elastic Compute Cloud (EC2) for a parallel computational task. The computational task is to compute a Blockchain proof-of-work.

## Background

In a Blockchain distributed ledger protocol, the proof-of-work stage consists of using a block of data and an arbitrary random 32-bit number that is only used once (nonce), as inputs to the SHA256 cryptographic hash function. The output of SHA256 is then used as input to the function again. The output is a hash value, a random number in the range 0 to 2^256-1. The aim of proof of work is to determine whether a nonce is golden. For a given data block, a nonce is golden if the hash value returned has a difficulty-level D leading number of bits which are zero.

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

## Running The Code

* When running the code for the first time a keypair will be created automatically, as well as an AWS IAM role, group and other security settings

* Running the code in the cloud can be done by running the cloud_access.py code

* A table of command line options are given below

<!-- parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code", choices=range(51), required=False, type=int, default=0)
parser.add_argument("-D", "--difficulty", help="difficulty",choices=range(256), type=int, default=0, required=False)
parser.add_argument("-L", "--confidence", help="confidence level between 0 and 1", default=1, type=float, required=False)
parser.add_argument("-T", "--time", help="time before stopping", type=int, default= 300, required=False)
parser.add_argument("-P", "--performance", help="runs a performance test", action='store_true', default=False, required=False) -->

| Short Argument| Long Argument|Description|Type |Required|
|:-------------|:-------------|:------------|:---------|:----------|
|-N|--number-of-vms  |Allows a user to specify the number of VMs to run the code. By default is 0, and CND will automatically calculate a desire number of virtual machines to use.|int| No|
|-D|--difficulty|Allows a user to set the difficulty level for the proof-of-work, difficulty is the number of leading bits that are zero in the returned hash value.| int   |Yes|
|-L|--confidence|A user can set the desired confidence level, between 0 and 1 of whether a golden nonce can be found in time T| float    | No    |
|-T|--time|Time limit given to find a golden nonce before all Virtual machines are terminated. Default value is 300 seconds.|int|No|
|-P|--performance|Runs a performance test|boolean|No|

*  An example of how the code is ran in the terminal is shown below. The example will set the difficulty level to 24 and the time limit to 200 and splut the work over 4 virtual machines


``` 
$ python cloud_access.py -D 24 -T 200 -N 4
```
## Cleanup

* To delete the key pair and AWS other configurations run

```
$ . ./clean.sh
```
