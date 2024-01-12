import time
import multiprocessing

time_start = time.perf_counter()

def my_f(seconds):
    time.sleep(seconds)
    print('I slept for 2 seconds.')



if __name__ == '__main__':
    processes = []
    for i in range(10):
        process = processes.append(multiprocessing.Process(target = my_f, args = [2,]))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

print('I still ran') 
time_ran = time.perf_counter()
print(time_ran-time_start)

