import random
import hashlib
import time
import getopt, sys
import os
import argparse
from multiprocessing import Process, Queue


# this file finds the golden nonce and is designed to be ran in the cloud or on a local machine

# splits up work over multiple instacne
def split_work(number_of_vms, time_limit, speed, start_val=0):
    ranges = []
    # how many values its able to check per second
    performance = speed
    # number of checks an instance can perform in given time
    total_instance_checks = performance * time_limit
    for i in range(number_of_vms):
        check_range = {'Start':i*total_instance_checks + start_val, 'Stop': (i+1) * total_instance_checks + start_val}
        ranges.append(check_range)
              
    return ranges

# given a nonce apply the sha256 cryptographic hash function to pre chosen block of data concatted with the nonce
def hash_gen(nonce):
    
    block = "COMSM0010cloud"

    input = block + str(nonce)
    input = input.encode('utf-8')

    hash_squared = hashlib.sha256(
        str(hashlib.sha256(input).hexdigest())
        .encode('utf-8'))


    return hash_squared.hexdigest()

# determines whether a nonce is golden by comparing the leading number of zeroes in a hash  with a Difficulty D
def golden_nonce(D, hash):
    Z = 0 
    base = 16
    is_golden = False
    # converts hash to binary
    bin_hash = bin(int(hash, base))[2:].zfill(256)
    
    # checking the number of leading zeroes
    for i in range(256):
        if(int(bin_hash[i]) == 0):
            Z += 1
        else:
            break
    
    if Z >= D:
        is_golden = True
    
    return is_golden

# checks nonces with in a set range
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

# finding a golden nonce on local machine using a set  number of threads in a set range
def threaded_nonce_check_in_range(start, stop, time_limit, D, result):
    result.put(check_nonce_in_range(start, stop, time_limit, D))

#finding a golden nonce on local machine printing what it is and the time it takes
def local_nonce_test():
    
    start = time.time()
    proof_of_work = check_nonce_in_range(start=0, stop=100000000, time_limit=300, D=24)
    end = time.time()

    print(end - start)
    print(proof_of_work)
    # print()

# finding a golden nonce on local machine using a set  number of threads
def threaded_nonce_check(number_of_threads, time_limit, difficulty, start_val=0, speed=160000):
    
    # split up the equally work using the ranges 
    ranges = split_work(number_of_threads, time_limit,  speed, start_val=0)
    processes = []
    wait = True
    result = Queue()
   
    # starting up processes to check nonces in set ranges
    for i in range(number_of_threads):
        processes.append(Process(target=threaded_nonce_check_in_range, args=(ranges[i]['Start'], ranges[i]['Stop'], time_limit, difficulty, result)))
        processes[i].start()
        print("Starting Process ", i)
        
    while wait:
        # print("waiting")
        for i in range(number_of_threads):
            if not processes[i].is_alive():
               wait = False
               for j in range(number_of_threads):
                   if not i == j:
                       processes[j].terminate()
    
    return result.get()

# used to find how many nonces can be checked per second
def performance_test(time_limit=300):
    golden = False
    number_checked = 0
    # print("running performance test...")
    start_time = time.time()
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
    return performance

#  used to find how many nonces can be checked per second
def performance_test2(time_limit=300):
    golden = False
    number_checked = 0
    # print("running performance test...")
    start_time = time.time()
    
    golden = golden_nonce(256, hash_gen(0))
    end_time = time.time()
    performance = end_time - start_time
    
    return performance

# used to find how many nonces can be checked per second
def performance_test3():
    golden = False
    number_checked = 0
    # print("running performance test...")
    start_time = time.time()
    check_nonce_in_range(0, 100000, time_limit=300, D=256)
    end_time = time.time()
    performance = end_time - start_time
    
  
    
    return performance
    
    
def main(args):
    
    #storing parser arguments 
    number_of_vms = args.number_of_vms
    time= args.time
    difficulty = args.difficulty
    start = args.start
    stop = args.stop
    performance = args.performance
    local = args.local

    # runs a performance test which calculate how many nonces can be checked per second on a machine
    if performance: 
        print(performance_test3())
        return 
   
    # code is intended to run on the cloud but obviously can be run from local machine to
    # this is done by settin gth e local parameter
    if local:
        print("running on local machine.")
        output = threaded_nonce_check(number_of_threads= number_of_vms, time_limit=time, difficulty=difficulty, start_val=0)
        print(output)
    else:
        nonce = check_nonce_in_range(start, stop, time, difficulty)
        print(nonce)
 

if __name__ == "__main__":
    
    # arguments to be parsed 
    parser = argparse.ArgumentParser(
        description="Finding the golden nonce in the cloud.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-N", "--number-of-vms", help="number of vms to run the code, if running on local machine its the number of threads", choices=range(51), required=False, type=int, default=0)
    parser.add_argument("-D", "--difficulty", help="difficulty", type=int, default=0, required=False)
    parser.add_argument("-T", "--time", help="time before stopping", type=int, default= 300, required=False)
    parser.add_argument("-P", "--performance", help="runs a performance test", action='store_true', default=False, required=False)
    parser.add_argument("-b", "--start", help="value to start checking", type=int, default= 0, required=False)
    parser.add_argument("-e", "--stop", help="value to stop checking", type=int, default= 0, required=False)
    parser.add_argument("-l", "--local", help="run the code on the local machine using threads", action='store_true', default=False, required=False)
    parser.parse_args()

    main(parser.parse_args())

