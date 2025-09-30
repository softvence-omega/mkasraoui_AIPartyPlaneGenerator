import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

def my_function():
    print("Function executed!")
    # Reschedule the function to run again after 10 seconds
    scheduler.enter(10, 1, my_function)

# Schedule the first run
scheduler.enter(10, 1, my_function)

# Start the scheduler
scheduler.run()