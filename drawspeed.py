'''
author: Michael liu (michaelliu92@163.com)
new thread, draw network speed
'''
import threading, os
import matplotlib.pyplot as plt
from testspeed import realtime_q
from mininet.log import info

shut_down = False

def get_shut_down():
    global shut_down
    return shut_down

def change_shut_down():
    global shut_down
    shut_down = not shut_down

class Drawspeed(threading.Thread):
    def __init__(self, thread_name, imagename):
        threading.Thread.__init__(self, name=thread_name)
        self.imagename = imagename


    def draw_realtime_speed(self):
        realtime_q_draw_x = []
        realtime_q_draw_y = []
        info('draw_realtime_speed start\n')
        if os.path.exists(self.imagename):
            os.remove(self.imagename)
        global shut_down
        while not shut_down:
            if not realtime_q.empty():
                [t, s] = realtime_q.get(block=True)
                realtime_q_draw_x.append(t)
                realtime_q_draw_y.append(s)
            plt.ion()
            plt.xlabel('s')
            plt.ylabel('Kbps')
            plt.plot(realtime_q_draw_x, realtime_q_draw_y, 'r')
            plt.pause(0.05)
            # plt.show()
        plt.savefig(self.imagename)
        plt.close()

    def run(self):
        info('%s start\n' % self.getName())
        self.draw_realtime_speed()


