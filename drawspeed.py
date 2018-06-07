'''
author: Michael liu (michaelliu92@163.com)
new thread, draw network speed
'''
import threading, os
import matplotlib.pyplot as plt
from testspeed import realtime_q
from mininet.log import info

shut_down_draw = False

def get_shut_down_draw():
    global shut_down_draw
    return shut_down_draw

def change_shut_down_draw():
    global shut_down_draw
    shut_down_draw = not shut_down_draw

class Drawspeed(threading.Thread):
    def __init__(self, thread_name, imagename):
        threading.Thread.__init__(self, name=thread_name)
        self.imagename = imagename


    def draw_realtime_speed(self):
        realtime_q_draw_x = []
        realtime_q_draw_y = []
        info('draw_realtime_speed start\n')
        global shut_down_draw
        image_count = 0
        plt.ion()

        # ax = plt.gca()
        # ax.spines['bottom'].set_position(('data', 0))
        # ax.spines['left'].set_position(('data', 0))
        while not shut_down_draw:
            if not realtime_q.empty():
                [t, s] = realtime_q.get(block=True)
                realtime_q_draw_x.append(t)
                realtime_q_draw_y.append(s)
            plt.xlabel('time(seconds)')
            plt.ylabel('realtime speed(Kbps)')
            plt.plot(realtime_q_draw_x, realtime_q_draw_y, 'r')
            plt.pause(0.05)
            #almost 10min refresh figure and save image
            if len(realtime_q_draw_y)>600 and len(realtime_q_draw_x)>600:
                realtime_q_draw_x = []
                realtime_q_draw_y = []
                image_count += 1
                plt.grid()
                plt.savefig(self.imagename+str(image_count)+'.png')
            # plt.show()
        plt.grid()
        plt.savefig(self.imagename+str(image_count)+'.png')
        plt.close()

    def run(self):
        info('%s start\n' % self.getName())
        self.draw_realtime_speed()


