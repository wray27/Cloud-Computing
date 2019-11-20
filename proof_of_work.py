import random
import hashlib
import time
import getopt, sys
import os



 
   
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


def check_nonce_in_range(start, stop, D):
    golden = False
    nonce = []
    for i in range(start,stop):
        golden = golden_nonce(D, hash_gen(i))
        if golden: 
            nonce.append(i)
            break

    return nonce
    
def local_nonce_test():

    start = time.time()
    proof_of_work = check_nonce_in_range(0,100000000,4)
    end = time.time()

    print(end - start)
    print(proof_of_work)
    print()



if __name__ == "__main__":
    arguments = len(sys.argv) - 1
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]

    unix_options = "htd:i:"
    gnu_options = ["help", "difficulty", "no-instances", "test"]

    try:
        arguments, values = getopt.getopt(argument_list, unix_options, gnu_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print()
        elif current_argument in ("-d", "--difficulty"):
            print()
        elif current_argument in ("-t", "test"):
            local_nonce_test()
            # cloud_access()
