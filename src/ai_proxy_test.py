# A test file for ai_proxy.py
import time
import ai_proxy

def enqueue(*x):
    pass

def main():
    ai_paths = ['./cpp_headers/ai_test.dll']
    ai_paths *= 8
    ai_proxy.start(ai_paths, enqueue)

if __name__ == '__main__':
    main()

