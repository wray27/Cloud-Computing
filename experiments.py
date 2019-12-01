import cloud_access
import proof_of_work
import matplotlib.pyplot as plt
import numpy as np


# Experiment 1:
# performance of runtime against difficulty(up to 28)
def experiment1():
    difficulty = 28
    time_limit = 90*60
    result = []
    for p in range(1, 8):
        process =[]
        for d in range(difficulty):
            process.append(proof_of_work.threaded_nonce_check(number_of_threads= p, time_limit=time_limit, difficulty=d, start_val=0,speed=190000))
            print(d+1, "difficulty checked")
        
        result.append(process)
    
    y = [[] for i in range(8)]
    print(result)
    for i in range(difficulty):
        y[0].append(result[0][i][1])
        y[1].append(result[1][i][1])

    x = np.linspace(0, difficulty, difficulty)

    for i in range(1,8):
        plt.plot(x, y[i], label=f"{i} thread(s)")
        

    plt.xlabel('Difficulty')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of nonce discovery algorithm using multiple threads")

    plt.legend()

    plt.show()
    plt.savefig('experiment1b.png')

def experiment2():
    time_limit = 90*60
    result = []
    total = 16
    for p in range(1, total+ 1):
        string = cloud_access.run_experiment(p,time_limit,25)
        int_result = float(string.strip("[]\n").split(",", 1)[1])
        result.append(int_result)
 
    x = np.linspace(1, total, total)
    plt.plot(x, result)

    plt.xlabel('Number of Virtual Machines')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of nonce discovery algorithm using N virtual machines")

    plt.legend()

    plt.show()
    plt.savefig('experiment2.png')

# experiment1(28)
experiment2()