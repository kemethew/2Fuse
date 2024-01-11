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
    remaining_time = 7000
    p = ProcessPoolExecutor(max_workers = 1)
    def activate_countdown_timer():
        global start_time, remaining_time
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        if elapsed_time > remaining_time:
            if elapsed_time - remaining_time > 500:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 7000))
            elif elapsed_time - remaining_time > 400:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 6900))
            elif elapsed_time - remaining_time > 300:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 6800))
            elif elapsed_time - remaining_time > 200:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 6700))
            elif elapsed_time - remaining_time > 100:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 6600))
            else:
                start_time = time.time()
                remaining_time = 7000
                futures.append(p.submit(countdown_timer, 6500))
        elif remaining_time - elapsed_time > 6000:
            start_time = time.time()
            remaining_time = 7000
            futures.append(p.submit(countdown_timer, round(elapsed_time/100) * 100 - 500))
        else:
            start_time = time.time()
            remaining_time = remaining_time - round(elapsed_time/100) * 100 + 1000
            futures.append(p.submit(countdown_timer, 500))

    program_start = time.perf_counter()
    activate_countdown_timer() # 7000 start to countdown
    pygame.time.delay(7300) # delay of 300 after the whole 7000
    activate_countdown_timer() # 7000 start to countdown
    pygame.time.delay(800) # 6200 now
    activate_countdown_timer() # called so add 800 to countdown
    pygame.time.delay(1200) # 5800 now
    activate_countdown_timer() # called so add 1000 to countdown

    for future in as_completed(futures):
        future.result()

    program_end = time.perf_counter()

    print(program_end - program_start)