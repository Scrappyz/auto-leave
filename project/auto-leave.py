import pyautogui
import argparse
import time
import os
from pytesseract import pytesseract
# from PIL import Image, ImageFilter

def find(image_path: str):
    print(pyautogui.locateOnScreen(image_path))

def convertInterval(freq) -> float:
    if type(freq) != str:
        return float(freq)
    
    t = ""
    unit = ""
    for i in range(len(freq)):
        if not freq[i].isdigit() and freq[i] != ' ':
            t = freq[:i]
            unit = freq[i:]
            break
        if i == len(freq)-1:
            i += 1
            t = freq[:i]
            unit = freq[i:]
            break
    
    t = float(t)
    if unit.startswith("ms"):
        t /= 1000
    elif unit.startswith("m"):
        t *= 60
    elif unit.startswith("h"):
        t *= 60*60
    
    return t

def leave():
    pyautogui.moveTo(1187, 981) # location of leave button in gmeet
    pyautogui.click()

def main():
    pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    current_path = os.path.dirname(__file__)
    
    parser = argparse.ArgumentParser(prog="Auto Leave")
    parser.add_argument("-d", "--delay", nargs="?", default="5", help="delay before program start", dest="delay")
    parser.add_argument("-t", "--threshold", nargs="?", type=int, default=10, help="the amount before leaving", dest="threshold")
    parser.add_argument("-f", "--frequency", nargs="?", default=10, help="how frequent to check the number of people", dest="frequency")
    
    args = parser.parse_args()
    delay = convertInterval(args.delay)
    threshold = args.threshold
    frequency = convertInterval(args.frequency)
    
    print("Press Ctrl+C to end program")
    time.sleep(delay)
    
    while True: 
        ss = pyautogui.screenshot(region=(1770, 436, 60, 27))
        people = pytesseract.image_to_string(ss, lang='eng', config="--psm 10 -c tessedit_char_whitelist=0123456789")
        if not people or int(people) < threshold:
            leave()
            break
        time.sleep(frequency)
        
    print("[Program Finished Successfully]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[Program Terminated]")
        
# Locations (on 1920x1080)
# people2 = (1770, 436, 60, 27)
    