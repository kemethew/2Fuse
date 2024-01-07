from concurrent.futures import ProcessPoolExecutor
import time

process = ProcessPoolExecutor(max_workers=1)


def function(argument):
    print('I will sleep now')
    time.sleep(1)
    print(f'Done sleeping with {argument}')

ts = time.time()

if __name__ == '__main__':
    argument = ('pillow', 'blanket')
    process.submit(function, *('pillow', ))