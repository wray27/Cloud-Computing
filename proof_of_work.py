import random
import hashlib
import time
import getopt, sys
import os
import argparse
import threading


parser = argparse.ArgumentParser(
        description="Finding the golden nonce in the cloud.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code", choices=range(51), required=False, type=int, default=0)
parser.add_argument("-D", "--difficulty", help="difficulty",choices=range(256), type=int, default=0, required=False)
parser.add_argument("-L", "--confidence", help="confidence level between 0 and 1", default=1, type=float, required=False)
parser.add_argument("-T", "--time", help="time before stopping",choices= range(60,1801), type=int, default= 300, required=False)
parser.add_argument("-b", "--start", help="value to start checking", type=int, default= 0, required=False)
parser.add_argument("-e", "--stop", help="value to stop checking", type=int, default= 0, required=False)
parser.add_argument("-l", "--local", help="run the code on the local machine using threads", type=bool, default=False, required=False)
parser.add_argument("-p", "--performance", help="runs a performance test", type=bool, default=False, required=False)
parser.parse_args()

def split_work(number_of_vms, time_limit, confidence, speed):
    
    ranges = []
    # how many values its able to check per second
    performance = speed
    # print(confidence)
    # number of checks an instance can perform in given time
    total_instance_checks = performance * time_limit
    for i in range(number_of_vms):
        if confidence == 1:
            check_range = {'Start':i*total_instance_checks, 'Stop': (i+1) * total_instance_checks}
            ranges.append(check_range)
            
        else:
            #TODO: The confidence inetrval logic
            total_no_checks = performance * time_limit * number_of_vms
            
    return ranges

def hash_gen(nonce):
    
    block = "COMSM0010cloud"

    input = block + str(nonce)
    input = input.encode('utf-8')

    hash_squared = hashlib.sha256(
        str(hashlib.sha256(input).hexdigest())
        .encode('utf-8'))


    return hash_squared.hexdigest()

def golden_nonce(D, hash):
    Z = 0 
    base = 16
    is_golden = False
    bin_hash = bin(int(hash, base))[2:].zfill(256)
    
    for i in range(256):
        if(int(bin_hash[i]) == 0):
            Z += 1
        else:
            break
    
    if Z >= D:
        is_golden = True
    
    return is_golden


def check_nonce_in_range(start, stop, time_limit, D):
    golden = False
    nonce = []
    start_time = time.time()
    for i in range(start,stop):
        end_time = time.time()
        elapsed_time = end_time - start_time
        golden = golden_nonce(D, hash_gen(i))
        
        if golden: 
            nonce.append(i)
            nonce.append(elapsed_time)
            break
        elif elapsed_time >= time_limit:
            break
        

    return nonce
    
def local_nonce_test():
    
    start = time.time()
    proof_of_work = check_nonce_in_range(start=0, stop=100000000, time_limit=300, D=24)
    end = time.time()

    print(end - start)
    print(proof_of_work)
    # print()

def performance_test(time_limit=300):
    golden = False
    number_checked = 0
    print("running performance test...")
    start_time = time.time()
    performance = performance_test()
    for i in range(sys.maxsize):
        end_time = time.time()
        elapsed_time = end_time - start_time
        golden = golden_nonce(256, hash_gen(i))
        
        
        if golden: 
            # not expecting it to be golden
            performance = 0
            break
        elif elapsed_time >= time_limit:
            number_checked = i
            break
        
    performance = number_checked / time_limit
    print("hash rate on local machine is approxiamtely ", performance, "per second")
    return performance
    
def main(args):
    number_of_vms = args.number_of_vms
    confidence = args.confidence
    time= args.time
    difficulty = args.difficulty
    start = args.start
    stop = args.stop
    performance = args.performance
    local = args.local
    
    # runs a performanc etest which calculate how many nonces can be checked per seconfd on a machine
    if performance: 
        performance_test()
        return 
   
    # code is intended to run on the cloud but obviously can be run from local machine to
    # this is done by settin gth e local parameter
    if local:
        print("running on local machine.")
    else:
        nonce = check_nonce_in_range(start, stop, time, difficulty)
        print(nonce)
 

if __name__ == "__main__":
    main(parser.parse_args())

