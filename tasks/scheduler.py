from apscheduler.schedulers.background import BackgroundScheduler

# Single global scheduler instance for the app lifecycle

autostart = True  # Toggle for unit tests

scheduler = BackgroundScheduler()

if autostart:
    scheduler.start()
