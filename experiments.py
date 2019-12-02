import cloud_access
import proof_of_work
import matplotlib.pyplot as plt
import numpy as np



# Experiment 2a:
# an experiment to show the runtimes of 1 Thread
# with varying difficulty
def experiment2a():
    time_limit = 90*60
    result = []
    difficulty = 25
    for d in range(difficulty):
            result.append(proof_of_work.threaded_nonce_check(number_of_threads= 1, time_limit=time_limit, difficulty=d, start_val=0,speed=190000)[1])
            print(d+1, "difficulty level checked")
 
    x = np.linspace(1, difficulty, difficulty)
    plt.plot(x, result)

    plt.xlabel('Difficulty')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of CND on a single thread")

    # plt.legend()
    plt.grid()
    plt.savefig('experiment2a.png')
    plt.show()
    plt.close()

# Experiment 2a:
# an experiment to show the runtimes of 1 AWS t2.micro instance
# with varying difficulty
def experiment2b():
    time_limit = 90*60
    result = []
    difficulty = 25
    for d in range(difficulty):
        try:
            string = cloud_access.run_experiment(1,time_limit,d)
            print(string)
            int_result = float(string.strip("[]\n").split(",", 1)[1])
            result.append(int_result)
        except:
            result.append(np.nan)
 
    x = np.linspace(0, difficulty, difficulty)
    plt.plot(x, result)

    plt.xlabel('Difficulty')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of CND on a single AWS t2.micro instance")

    # plt.legend()
    plt.grid()

    plt.savefig('experiment2b.png')
    plt.show()
    plt.close()


# Experiment 3:
# an experiment to show the runtimes of running the nonce discovery using multiple processes
# with varying difficulty
# split amongst 2 workers
def experiment3():
    difficulty = 25
    time_limit = 90*60
    result = []
    threads = 4
    for p in range(1, threads+1):
        process =[]
        for d in range(difficulty):
            process.append(proof_of_work.threaded_nonce_check(number_of_threads= p, time_limit=time_limit, difficulty=d, start_val=0,speed=190000))
            print(d+1, "difficulty checked")
        
        result.append(process)
    
    y = [[] for i in range(threads)]
    print(result)
    for i in range(difficulty):
        for j in range(threads):
            y[j].append(result[j][i][1])
        
    x = np.linspace(0, difficulty, difficulty)

    for i in range(threads):
        plt.plot(x, y[i], label=f"{i+1} thread(s)")
        

    plt.xlabel('Difficulty')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of CND using multiple threads")

    plt.legend()
    plt.grid()

    plt.savefig('experiment3.png')
    plt.show()

# Experiment 4:
# an experiment to show the runtimes of running the nonce discovery in the cloud over N horizontal machines
# with diffculty set to 24
def experiment4():
    time_limit = 90*60
    result = []
    total = 16
    for p in range(1, total+ 1):
        try:
            string = cloud_access.run_experiment(p,time_limit,24)
            print(string)
            int_result = float(string.strip("[]\n").split(",", 1)[1])
            result.append(int_result)
        except:
            result.append(np.nan)
 
    x = np.linspace(1, total, total)
    plt.plot(x, result)

    plt.xlabel('Number of Virtual Machines')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of nonce discovery algorithm using N virtual machines")

    plt.legend()
    plt.grid()

    plt.savefig('experiment4.png')
    plt.show()

# Experiment 5:
# an experiment to show the runtimes of CND in the cloud over 16 horizontal machines
# with varying difficulty  up to 25
def experiment5():
    time_limit = 90*60
    result = []
    total = 16
    difficulty = 25
    for d in range(difficulty):
        try:
            string = cloud_access.run_experiment(16,time_limit, d)
            print(string)
            int_result = float(string.strip("[]\n").split(",", 1)[1])
            result.append(int_result)
        except:
            result.append(np.nan)
 
    x = np.linspace(0, difficulty, difficulty)
    plt.plot(x, result)

    plt.xlabel('Difficulty')
    plt.ylabel('Runtime (seconds)')

    plt.title("Graph to show performance of CND 16 virtual machines")

    plt.legend()
    plt.grid()

    plt.savefig('experiment5.png')
    plt.show()

# UNCOMMENT an experiment to run it
# experiment1()
# experiment2a()
experiment2b()
# experiment3()
# experiment4()
# experiment5()