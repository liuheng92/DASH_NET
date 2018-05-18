'''
author: Michael liu (michaelliubnu@163.com)
new thread for checking the download packet speed of the specified network card
'''
import os
import Queue
import threading, time
from mininet.log import info
from subprocess import ( Popen, PIPE )

#save realtime network speed
realtime_q = Queue.Queue(0)

#save setting network speed
setting_q = Queue.Queue(0)

def sh( cmd ):
    "Print a command and send it to the shell"
    return Popen( [ '/bin/sh', '-c', cmd ], stdout=PIPE ).communicate()[ 0 ]

class Testspeed(threading.Thread):
    def __init__(self, thread_name, intf_name, file):
        threading.Thread.__init__(self, name=thread_name)
        self.intf_name = intf_name
        self.file = file

    #Check the download packet speed of the specified network card
    def test_speed(self):
        #remove old output file
        if os.path.exists(self.file):
            os.remove(self.file)

        realtime_q.put([0, 0])
        temp_time = 0

        with open(self.file, 'a') as f:
            f.write('(0, 0)\n')
        while True:
            pre = sh("ifconfig %s | grep bytes | awk '{ print $6 }' | awk -F ':' '{ print $2 }'" % self.intf_name)
            time.sleep(1)
            temp_time += 1
            pro = sh("ifconfig %s | grep bytes | awk '{ print $6 }' | awk -F ':' '{ print $2 }'" % self.intf_name)
            if  float(pro) > float(pre) :
                #unit Kbit/s
                realtime_speed = (float(pro)-float(pre))*8/1024
                realtime_q.put([temp_time, realtime_speed])
                info(str(realtime_speed)+'Kbit/s\n')
                with open(self.file, 'a') as f:
                    f.write('(%s, %s)\n' % (temp_time, realtime_speed))

    def run(self):
        info('%s start\n' % self.getName())
        self.test_speed()