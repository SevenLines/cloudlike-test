from multiprocessing import cpu_count

def max_workers():
    return cpu_count() + 1
