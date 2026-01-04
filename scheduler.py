import time
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from arb_finder import main as run_arb_job

# Set up logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

def job_wrapper():
    logging.info("Starting scheduled scan...")
    try:
        run_arb_job()
    except Exception as e:
        logging.error(f"Job failed with error: {e}")
    logging.info("Scan complete.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Run every 5 minutes
    trigger = IntervalTrigger(minutes=5)
    scheduler.add_job(job_wrapper, trigger, id='arb_scanner', replace_existing=True)
    
    logging.info("Scheduler started. Running job every 5 minutes. Press Ctrl+C to exit.")
    
    # Run once immediately on startup
    job_wrapper()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
