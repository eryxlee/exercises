

def createDaemon():
    import os

    # create - fork 1
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    # it separates the son from the father
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # create - fork 2
    try:
        pid = os.fork()
        if pid > 0:
            print 'Daemon PID %d' % pid
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    funzioneDemo() # function demo

def funzioneDemo():

    import time

    fd = open('/tmp/daemon.log', 'w')
    while True:
        fd.write(time.ctime()+'\n')
        fd.flush()
        time.sleep(2)
    fd.close()

if __name__ == '__main__':
    createDaemon()

