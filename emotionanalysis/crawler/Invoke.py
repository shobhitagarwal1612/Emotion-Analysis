
result_queue = Queue()
crawler = CrawlerWorker(amazon(), result_queue)
crawler.start()
for item in result_queue.get():
    yield item