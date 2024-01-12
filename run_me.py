from concurrent.futures import ProcessPoolExecutor, as_completed
import time, pygame

pygame.init()

def countdown_timer(milliseconds):
    while milliseconds > 0:
        print(milliseconds)
        pygame.time.delay(100)
        milliseconds -= 100


if __name__ == '__main__':
    futures = []
    start_time = 0
    remaining_time = 3000
    p = ProcessPoolExecutor(max_workers = 1)
    def activate_countdown_timer():
        global start_time, remaining_time
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        processed_elapsed_time = round(elapsed_time/100) * 100
        if elapsed_time > remaining_time:
            time_adjustment = max(0, round((300 - (elapsed_time - remaining_time))/100) * 100)
            print(time_adjustment)
            start_time = time.time()
            remaining_time = 3000
            futures.append(p.submit(countdown_timer, 3000 - time_adjustment))
        elif remaining_time - elapsed_time > 2000:
            start_time = time.time()
            remaining_time = 3000
            futures.append(p.submit(countdown_timer, processed_elapsed_time - 100))
        else:
            start_time = time.time()
            remaining_time = remaining_time - processed_elapsed_time + 1000
            futures.append(p.submit(countdown_timer, 800))


    program_start = time.perf_counter()
    # activate_countdown_timer()
    # pygame.time.delay(7300)
    activate_countdown_timer()
    pygame.time.delay(900)
    activate_countdown_timer()
    pygame.time.delay(1200)
    activate_countdown_timer()
    # pygame.time.delay(900)
    # activate_countdown_timer()

    for future in as_completed(futures):
        future.result()

    program_end = time.perf_counter()

    print(program_end - program_start)