import threading
import time
import schedule

from parsing import Main


def ekatalog_update():

    def run_threaded():
        e = Main.Ekatalog()
        job_thread = threading.Thread(target=e.update)
        job_thread.start()

    schedule.every().wednesday.at("02:40").do(run_threaded)

    while True:
        schedule.run_pending()
        time.sleep(1)
