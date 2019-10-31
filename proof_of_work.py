import random
import hashlib
import time
import sys


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

    

start = time.time()
proof_of_work = check_nonce_in_range(0,100000000,25)
end = time.time()

print(end - start)
print(proof_of_work)