"""
scheduledResultsScrape.py

credit to: https://stackoverflow.com/questions/44228851/scrapy-on-a-schedule
"""
from twisted.internet import reactor
from gradResultScraper.spiders.gradResultScraper import gradResultScraper
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
import sched, time
import sys




def run_crawl():
    """
    Run a spider within Twisted. Once it completes,
    wait 5 seconds and run another spider.
    """
    runner = CrawlerRunner({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        })
    deferred = runner.crawl(gradResultScraper)

    # you can use reactor.callLater or task.deferLater to schedule a function
    deferred.addCallback(reactor.callLater, 3600*6, run_crawl)
    return deferred

def run_sched_crawl(s, hours):
    """
    Run a spider using sched.when it finishes add another to the queue.
    """
    # runner = CrawlerRunner({
    #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    #     })
    # deferred = runner.crawl(gradResultScraper)
    try:
        process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
        process.crawl(gradResultScraper)
        process.start() # the script will block here until the crawling is finished
        print(time.time())
    except:
        return
    s.enter(3600*hours, 1, run_sched_crawl, kwargs={'s': s})
    return

def print_yes(s):
    print('yes')
    print(time.time())
    print('\n')
    s.enter(5, 1, print_yes, kwargs={'s': s})
    return

if  __name__=='__main__':
    if len(sys.argv)>1:
        hours=float(str(sys.argv[1]))
    else:
        hours=1
    # run_crawl()
    # reactor.run()   # you have to run the reactor yourself
    s = sched.scheduler(time.time, time.sleep)
    # s.enter(5, 1, print_yes, kwargs={'s': s})
    s.enter(0, 1, run_sched_crawl, kwargs={'s': s, 'hours':hours})
    s.run()
