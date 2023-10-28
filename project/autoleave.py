import pyautogui
import argparse
import time
import os
import json
from pytesseract import pytesseract
from pynput import mouse, keyboard

positions = [[-1, -1], [-1, -1]]
json_data = {}

def mouse_click(x, y, button, pressed):
    global positions
    if pressed:
        positions[0] = [x, y]
    else:
        positions[1] = [x, y]
        return False

def shift_press(key):
    if key == keyboard.Key.shift:
        with mouse.Listener(on_click=mouse_click) as listener:
            listener.join()
        return False
    
def getPosition():
    with keyboard.Listener(on_press=shift_press) as listener:
        listener.join()
    
def savePositionToJson(key: str, val: tuple, file_path: str):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
        json_data[key] = val
    with open(file_path, 'w') as f:
        f.write(json.dumps(json_data, indent=4))
        
def getPositionFromJson(key: str, file_path: str) -> tuple:
    with open(file_path, "r") as f:
        json_data = json.load(f)
        return json_data[key]
    
def getScreenshotFromPosition(position):
    ss_pos = (position[0][0], position[0][1], position[1][0] - position[0][0], position[1][1] - position[0][1])
    return ss_pos

def getCenterOfPosition(pos: tuple) -> tuple:
    center = ((pos[0][0] + pos[1][0]) / 2, (pos[0][1] + pos[1][1]) / 2)
    return center

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

def clickAt(x: int, y: int):
    pyautogui.moveTo(x, y)
    pyautogui.click()
    
def getNumberOfPeople(s: str) -> int:
    if s.startswith("Contributors"):
        n = -1
        for i in reversed(range(len(s))):
            if not s[i].isdigit():
                n = i+1
                break
        
        return int(s[n:])
    
    return -1

def main():
    pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    current_path = os.path.dirname(__file__)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delay", nargs="?", default="5", help="delay before program start", dest="delay")
    parser.add_argument("-t", "--threshold", nargs="?", type=int, default=10, help="the amount before leaving", dest="threshold")
    parser.add_argument("-f", "--frequency", nargs="?", default=10, help="how frequent to check the number of people", dest="frequency")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.2.0-alpha")
    
    subparser = parser.add_subparsers(dest="command")
    pos = subparser.add_parser("position", help="save position")
    pos.add_argument("--button", action="store_true", help="save position of leave button", dest="button")
    pos.add_argument("--people", action="store_true", help="save position of number of people", dest="people")
    
    args = parser.parse_args()
    delay = 5
    threshold = 10
    frequency = 5
    if args.command == "position":
        if args.button or args.people:
            getPosition()
            if args.button:
                savePositionToJson("button", positions, os.path.join(current_path, "sample.json"))
            elif args.people:
                savePositionToJson("people", positions, os.path.join(current_path, "sample.json"))
        exit()
    else:
        delay = convertInterval(args.delay)
        threshold = args.threshold
        frequency = convertInterval(args.frequency)
    
    json_path = os.path.join(current_path, "sample.json")
    time.sleep(delay)
    print("[START] Press Ctrl+C to end process")
    while True: 
        ss = pyautogui.screenshot(region=getScreenshotFromPosition(getPositionFromJson("people", json_path)))
        people = pytesseract.image_to_string(ss, lang='eng', config="--psm 10")
        number_of_people = getNumberOfPeople(people)
        if number_of_people < 0:
            print("[WARNING] Cannot find number of people")
            time.sleep(frequency)
            continue
        
        print("[INFO] Number of people: " + str(people), end="")
        
        if number_of_people < threshold:
            click_pos = getCenterOfPosition(getPositionFromJson("button", json_path))
            clickAt(click_pos[0], click_pos[1])
            break
        
        time.sleep(frequency)
        
    print("[END] Program finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[END] Program terminated")
    