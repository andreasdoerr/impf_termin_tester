import time

from datetime import datetime


class Runner:
    def __init__(self, urls, browser, notifiers):
        self.urls = urls
        self.browser = browser
        self.notifiers = notifiers

        self.wait_time = 5
        self.interval_time = 5 * 60

    def start(self):
        self._initialize()
        self._run()

    def _initialize(self):
        print()
        print("#" * 80)
        print(" Setup")
        print("-" * 80, flush=True)

        # Initialize browser
        print(f" - Initialize: Browser ...", end=" ", flush=True)
        self.browser.initialize()
        print("Done", flush=True)

        # Initialize all notification channels
        for notifier in self.notifiers:
            print(
                f" - Initialize notification channel: {notifier.name} ...",
                end=" ",
                flush=True,
            )
            notifier.initialize()
            print("Done", flush=True)

        print("#" * 80)
        print("", flush=True)

    def _run_url(self, url):
        result = self.browser.check_url(url)

        if result is None:
            print("   RESULT: No appointments available.", flush=True)
            return

        print("*" * 80)
        print("   RESULT: Appointments available", flush=True)
        print("*" * 80)

        for notifier in self.notifiers:
            print(f" - Sent notification: {notifier.name} ... ", end=" ", flush=True)
            success = notifier.sent_notification(result)
            if success:
                print("Success.", flush=True)
            else:
                print("Failed.", flush=True)
        print("*" * 80, flush=True)

    def _run(self):
        while True:
            print("#" * 80)
            print("Checking websites:")
            print(datetime.now().strftime("%d.%m.%Y - %H:%M"))
            print("-" * 80, flush=True)

            for i, url in enumerate(self.urls):
                try:
                    print(f" - {i+1} of {len(self.urls)}, open: {url}", flush=True)
                    self._run_url(url)
                except Exception as e:
                    print("   Failed", e, flush=True)

                time.sleep(self.wait_time)

            print("-" * 80, flush=True)
            print("Checking completed.")
            print("#" * 80)
            print("", flush=True)

            print(f"Wait {self.interval_time // 60}min\n", flush=True)
            time.sleep(self.interval_time)
