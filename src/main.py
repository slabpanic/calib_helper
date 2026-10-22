import time
import keyboard

from jaka import JakaRobot

import numpy as np
import pyautogui
import pygetwindow as gw
from paddleocr import PaddleOCR
from paddlex.inference.pipelines.ocr.result import OCRResult


def main():
    window = gw.getWindowsWithTitle("Eye to Hand")[0]
    window.activate()
    time.sleep(1.0)

    inner_left = window.left + 10
    inner_top = window.top + 10
    inner_width = window.width - 20
    inner_height = window.height - 20

    screenshot = pyautogui.screenshot(
        region=(inner_left, inner_top, inner_width, inner_height)
    )
    img = np.array(screenshot)

    window.minimize()

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        engine="paddle",
    )
    result: OCRResult = ocr.predict(img)[0]

    def calc_pos(text: str):
        index = result["rec_texts"].index(text)
        box = result["rec_boxes"][index].tolist()
        return (box[0] + box[2]) // 2, (box[1] + box[3]) // 2

    x1, y1 = calc_pos("预览采集图像")
    x2, y2 = calc_pos("添加图像并记录法兰位姿")

    def capture():
        pyautogui.click(x1, y1)

    def confirm():
        pyautogui.click(x2, y2)
        pyautogui.hotkey("ctrl", "a")

        with JakaRobot("192.168.36.100") as robot:
            pose = [f"{i:.3f}" for i in robot.get_tool_pose()]

        pyautogui.write(pose[0])
        pyautogui.press("tab", 1, 0.1)

        pyautogui.write(pose[1])
        pyautogui.press("tab", 1, 0.1)

        pyautogui.write(pose[2])
        pyautogui.press("tab", 5, 0.1)

        pyautogui.write(pose[3])
        pyautogui.press("tab", 2, 0.1)

        pyautogui.write(pose[4])
        pyautogui.press("tab", 2, 0.1)

        pyautogui.write(pose[5])
        pyautogui.press("tab", 1, 0.1)
        pyautogui.press("enter", 1, 0.1)

    keyboard.add_hotkey("-", capture)
    keyboard.add_hotkey("=", confirm)

    print("press '-' to capture\npress '=' to confirm\npress 'enter' to exit")
    input()


if __name__ == "__main__":
    main()
