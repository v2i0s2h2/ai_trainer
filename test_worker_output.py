"""
Test worker process output with explicit flush
"""

if __name__ == '__main__':
    import sys
    import time
    from multiprocessing import Process, Queue
    import pyttsx3
    
    def test_worker(queue):
        sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)
        print("[WORKER] Starting...", flush=True)
        
        engine = pyttsx3.init()
        print("[WORKER] Engine initialized", flush=True)
        
        count = 0
        while True:
            msg = queue.get()
            print(f"[WORKER] Got: {msg}", flush=True)
            if msg is None:
                break
            count += 1
            print(f"[WORKER] Speaking {count}: {msg}", flush=True)
            engine.say(msg)
            engine.runAndWait()
            print(f"[WORKER] Done {count}", flush=True)
    
    print("Testing worker output...")
    q = Queue()
    p = Process(target=test_worker, args=(q,))
    p.start()
    
    print("Sending 3 messages...")
    q.put("Message one")
    q.put("Message two")
    q.put("Message three")
    
    print("Waiting 10 seconds...")
    time.sleep(10)
    
    print("Stopping...")
    q.put(None)
    p.join(timeout=5)
    
    print("Done! Did you hear 3 messages?")

