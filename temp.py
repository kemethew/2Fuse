import time
import multiprocessing

# BOOST_IS_ACTIVE = False
# BOOST_START_TIME = time.time()

# def activate_boost():
#     global BOOST_START_TIME, BOOST_IS_ACTIVE
#     BOOST_RUNNING_TIME = time.time() - BOOST_START_TIME
#     if not BOOST_IS_ACTIVE:
#         BOOST_IS_ACTIVE = True
#         BOOST_START_TIME = time.time()
#     else:
#         if BOOST_RUNNING_TIME >= 7:
#             BOOST_IS_ACTIVE = False
#         elif BOOST_RUNNING_TIME < 1:
#             BOOST_START_TIME += BOOST_RUNNING_TIME
#         else:
#             BOOST_START_TIME += 1

# print(BOOST_START_TIME)
# activate_boost()
# time.sleep(3)
# activate_boost()
# print(BOOST_START_TIME)

n = 1

if n == 0:
    pass

if n==1:
    print('its working')