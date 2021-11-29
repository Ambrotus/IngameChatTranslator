from easyocr import Reader
import numpy as np
import cv2 as cv2
from PIL import ImageGrab
# https://realpython.com/pysimplegui-python/
import PySimpleGUI as sg
import time
import torch.multiprocessing as mp
from deep_translator import GoogleTranslator

gui_queue = None
ocr_queue = None
reader = Reader(['en'], gpu = False)

class UserInterface:

    def __init__(self):
        global gui_queue
        global ocr_queue
        sg.theme('DarkBlack') # give our window a spiffy set of colors

        layout = [
                [sg.Output(size=(50, 10), font=('Helvetica', '8','bold'), text_color = 'White', key = '_OUTPUT_',background_color= 'grey')],
                [sg.Button('Start'), sg.Button('Stop'), sg.Button('Exit')]]

        self.window = sg.Window('Chat window', layout, font=('Helvetica', ' 13','bold'),background_color='grey', default_button_element_size=(1,1), use_default_focus=False,
                    transparent_color='grey',alpha_channel=1,titlebar_background_color='black', no_titlebar=True,grab_anywhere=True,keep_on_top=True)

        while True:  # Event Loop
            event, values = self.window.read()
            # self.window.KeepOnTop = True
            self.window.bring_to_front()
            print(event, values)
            if event in (None, 'Exit'):
                gui_queue.put('Stop')
                break
            if event == 'Start':
                # Update the "output" text element to be the value of "input" element
                self.window['_OUTPUT_'].update("started")
                begin(gui_queue, ocr_queue)
            if event == 'Stop':
                gui_queue.put('Stop')
            self.window.TKroot.after(1000, self.printOutput)
        self.window.close()

    def printOutput(self):
        self.window['_OUTPUT_'].Update('')
        # print(ocr_queue.get())
        for msg in ocr_queue.get():
        # https://medium.com/analytics-vidhya/how-to-translate-text-with-python-9d203139dcf5
            print(msg)
        self.window.TKroot.after(1000, self.printOutput)


def begin(gui_queue, ocr_queue):
    ocrProc = mp.Process(target=startOcr, args=(gui_queue,ocr_queue))
    ocrProc.start()
    return ocrProc

def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def startOcr(gui_queue, ocr_queue):
    # outputText = []
    # langs =["en"]
    x = 560
    y = 595
    x2= 1310
    y2= 760
    color1 = np.asarray([225])
    color2 = np.asarray([227])
    i=1
    while True:
        # sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, 'Loading', text_color='black', transparent_color='blue', background_color='blue', time_between_frames=100)
        try:
            message = gui_queue.get_nowait()    # see if something has been posted to Queue
        except Exception as e:                     # get_nowait() will get exception when Queue is empty
            message = None                      # nothing in queue so do nothing
        if message:
            print(f'Got a queue message {message}!!!')
            break
    # while(i == 1):
        deskimage = ImageGrab.grab()
        image = np.array(deskimage)
        crop_img = image[y:y2, x:x2]
        image = crop_img

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('image', image)
        mask = cv2.inRange(image, color1, color2)
        # cv2.imshow('mask', mask)
        # cv2.waitKey(5)
        results = reader.readtext(mask)
        outputText = []
        # loop over the results
        for (bbox, text, prob) in results:
            text = cleanup_text(text)
            # print(text)
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            outputText.append(translated)#+'\n'
        ocr_queue.put(outputText)
        time.sleep(1)
        # print(outputText)
        # i=0
    # return outputText


def main():
    global gui_queue
    global ocr_queue
    ocr_queue = mp.Queue()
    gui_queue = mp.Queue()
    ui = UserInterface()

if __name__ == '__main__':
    main()

# # https://github.com/PySimpleGUI/PySimpleGUI/issues/1077
# # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Notification_Window_Multiprocessing.py
# # https://stackoverflow.com/questions/60213167/pysimplegui-how-to-make-transparent-click-through-window
# # https://github.com/PySimpleGUI/PySimpleGUI/issues/2525
# # https://docs.python.org/3/library/multiprocessing.html
