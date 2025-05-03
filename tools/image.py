from cv2 import (imread, resize,
                 matchTemplate, minMaxLoc, TM_CCOEFF_NORMED,
                 cvtColor, COLOR_BGR2HSV, COLOR_RGB2BGR)
from colorsys import rgb_to_hsv
from win32api import SetCursorPos
from PIL import ImageGrab
from os import remove
from os.path import isfile
from numpy import asarray, ndarray
from .system import *
from time import time
color_zone = {"red": [[156, 180], [0, 10], 43, 255, 46, 255], 
              "orange": [11, 25, 43, 255, 46, 255],
              "yellow": [26, 34, 43, 255, 46, 255],
              "green": [35, 77, 43, 255, 46, 255],
              "cyan": [78, 99, 43, 255, 46, 255],
              "blue": [100, 124, 43, 255, 46, 255],
              "purple": [125, 155, 43, 255, 46, 255],
              "white": [0, 180, 0, 300, 221, 255],
              "black": [0, 180, 0, 255, 0, 45],
              "grey": [0, 180, 0, 43, 46, 220]}


def match_zone(aft, bef):
    match_res = matchTemplate(aft, bef, TM_CCOEFF_NORMED)
    min_sim, max_sim, min_loc, max_loc = minMaxLoc(match_res)
    if (min_sim >= -0.6) and (max_sim <= 0.6):
        return 0
    else:
        min_sim = min_sim * -1
        if max_sim >= min_sim:
            return max_sim
        else:
            return min_sim


class Image(System):
    def screenshot(self, zone: list = "WINDOW"):
        SetCursorPos((1, 1))
        sleep(0.01)
        if zone == "WINDOW":
            shot = ImageGrab.grab(self.frame)
        elif isinstance(zone, tuple):
            (x1, y1, x2, y2) = zone
            (scx1, scy1), (scx2, scy2) = self.axis_zoom(x1, y1), self.axis_zoom(x2, y2)
            xf1, yf1, xf2, yf2 = self.frame
            shot = ImageGrab.grab((xf1 + scx1, yf1 + scy1, xf1 + scx2, yf1 + scy2))  # 截取屏幕指定区域的图像
        elif zone == "FULL":
            shot = ImageGrab.grab()
        else:
            print("error:\"zone\"需要是列表。")
            return None
        path = r"cache\%s.png" % (str(time())[-5:])
        shot.save(path)
        return path

    def scshot(self, zone="WINDOW"):
        SetCursorPos((1, 1))
        sleep(0.01)
        if zone == "WINDOW":
            shot = ImageGrab.grab(self.frame)
        elif isinstance(zone, tuple):
            (scx1, scy1, scx2, scy2) = self.zone_zoom(zone)
            xf1, yf1, xf2, yf2 = self.frame
            shot = ImageGrab.grab((xf1 + scx1, yf1 + scy1, xf1 + scx2, yf1 + scy2))  # 截取屏幕指定区域的图像
        elif zone == "FULL":
            shot = ImageGrab.grab()
        else:
            print("error:\"zone\"需要是列表。")
            return None
        return cvtColor(asarray(shot), COLOR_RGB2BGR)

    def find_pic(self, target, zone="ALL", template: str = "",
                 delete=False, method=TM_CCOEFF_NORMED):
        if isinstance(template, ndarray):
            pass
        elif template:
            if not isfile(template):
                print("error: ocr 参数 big_pic 为无效路径。")
                raise ValueError("error: ocr 参数 big_pic 为无效路径。")
            else:
                template_path = template
                template = imread(template_path)
                if delete:
                    remove(template_path)
        else:
            template = self.scshot()
        if zone == "ALL":
            (x1, y1, x2, y2) = (0, 0, 0, 0)
        else:
            (x1, y1, x2, y2) = zone
            (scx1, scy1), (scx2, scy2) = self.axis_zoom(x1, y1), self.axis_zoom(x2, y2)
            template = template[scy1:scy2, scx1:scx2]
        if isinstance(target, ndarray):
            pass
        elif target:
            if not isfile(target):
                print("error: findpic 参数 small_pic 为无效路径。")
                raise ValueError("error: findpic 参数 small_pic 为无效路径。")
            else:
                target = imread(target)
        else:
            print("error: findpic 参数 small_pic 为无效路径。")
            raise ValueError("error: findpic 参数 small_pic 为无效路径。")
        tem_h, tem_w = target.shape[0:2]
        if self.zoom == 1.0:
            pass
        else:
            search_h, search_w = template.shape[0:2]
            template = resize(template,
                              (int(search_w / self.zoom),
                               int(search_h / self.zoom)))
        match_res = matchTemplate(template, target, method)
        del template
        min_sim, max_sim, min_loc, max_loc = minMaxLoc(match_res)
        if (min_sim >= -0.6) and (max_sim <= 0.6):
            centre, sim = ((0, 0), 0)
        else:
            min_sim = min_sim * -1
            if max_sim >= min_sim:
                (rel_x, rel_y), sim = max_loc, max_sim
            else:
                (rel_x, rel_y), sim = min_loc, min_sim
            x = x1 + rel_x + int(tem_w / 2)
            y = y1 + rel_y + int(tem_h / 2)
            centre = (x, y)
        return centre, sim

    def find_color(self, target, zone="ALL", template: str = "",
                   delete=False):
        if isinstance(template, ndarray):
            pass
        elif template:
            if not isfile(template):
                print("error: ocr 参数 big_pic 为无效路径。")
                raise ValueError("error: ocr 参数 big_pic 为无效路径。")
            else:
                template_path = template
                template = imread(template_path)
                if delete:
                    remove(template_path)
        else:
            template = self.scshot()
        if zone == "ALL":
            (x1, y1, x2, y2) = (0, 0, 0, 0)
        else:
            (x1, y1, x2, y2) = zone
            (scx1, scy1), (scx2, scy2) = self.axis_zoom(x1, y1), self.axis_zoom(x2, y2)
            template = template[scy1:scy2, scx1:scx2]
        search_h, search_w, num = template.shape
        hsv = cvtColor(template, COLOR_BGR2HSV)
        del template
        for color in target.split("+"):
            if color == "red":
                [h_down_min, h_down_max], [h_up_min, h_up_max], s_min, s_max, v_min, v_max = color_zone[color]
                for rel_x in range(search_w):
                    for rel_y in range(search_h):
                        h, s, v = hsv[rel_y, rel_x]
                        # hex = ('{:02X}' * 3).format(r, g, b)
                        if h_down_min < h < h_down_max or h_up_min < h < h_up_max:
                            if s_min < s < s_max:
                                if s_min < s < s_max:
                                    rel_x = x1 + int(rel_x / self.zoom)
                                    rel_y = y1 + int(rel_y / self.zoom)
                                    return (rel_x, rel_y), True
            else:
                if color in ["orange", "yellow", "green", "cyan", "blue", "purple", "white", "black", "grey"]:
                    h_min, h_max, s_min, s_max, v_min, v_max = color_zone[color]
                else:
                    b, g, r = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
                    h, s, v = rgb_to_hsv(r, g, b)
                    if h < 0.061:
                        h += 1
                    h_min, h_max, s_min, s_max, v_min, v_max = h*180-2, h*180+2, s*255-3, s*255+3, v-3, v+3
                for rel_x in range(search_w):
                    for rel_y in range(search_h):
                        h, s, v = hsv[rel_y, rel_x]
                        # hex = ('{:02X}' * 3).format(r, g, b)
                        if h_min < h < h_max:
                            if s_min < s < s_max:
                                if s_min < s < s_max:
                                    rel_x = x1 + int(rel_x / self.zoom)
                                    rel_y = y1 + int(rel_y / self.zoom)
                                    return (rel_x, rel_y), True
        return (0, 0), False

    def ocr(self, zone="ALL", template: str = "", mode: int = 0,
            delete=False):
        if self.OCR is None:
            print("error: ocr 未启用。")
            return 0
        if isinstance(template, ndarray):
            template = template
        elif template:
            if not isfile(template):
                print("error: ocr 参数 big_pic 为无效路径。")
                raise ValueError("error: ocr 参数 big_pic 为无效路径。")
            else:
                template_path = template
                template = imread(template_path)
                if delete:
                    remove(template_path)
        else:
            template = self.scshot()
        if zone == "ALL":
            (x1, y1) = (0, 0)
        else:
            (x1, y1, x2, y2) = zone
            (scx1, scy1), (scx2, scy2) = self.axis_zoom(x1, y1), self.axis_zoom(x2, y2)
            template = template[scy1:scy2, scx1:scx2]
        _list = self.OCR.output(template)
        del template
        if mode == 0:  # 简单单行识字
            if _list:
                text, gross, weight = "", 0, 0
                for i in _list:
                    tem_text = i[1][0]
                    tem_num = len(tem_text)
                    weight = tem_num * i[1][1]
                    gross += tem_num
                    text += tem_text
                _list = text, weight / gross
            else:
                _list = "", 0
        elif mode == 1:  # 分析文本及其位置形状
            if _list:
                _l = []
                for i in _list:
                    xy1, xy2 = ([u / self.zoom for u in i[0][0]],
                                [o / self.zoom for o in i[0][2]])
                    zone = ([x + y for x, y in zip([x1, y1], xy1)] +
                            [x + y for x, y in zip([x1, y1], xy2)])
                    _l += [[i[1][0], zone, i[1][1]]]
                _list = _l
            else:
                _list = [["", None, 0]]
        elif mode == 2:  # 输出原始结果
            pass
        else:
            print("error: ocr 参数 mode 无效模式。")
        return _list

    def find_text(self, target, zone="ALL", big_pic: str = "", delete=False):
        _list = self.ocr(zone, template=big_pic, mode=1, delete=delete)
        result = str_find(target, _list)
        if result:
            return result
        else:
            return False

    def match_text(self, target, zone="ALL", big_pic: str = "", delete=False):
        _list = self.ocr(zone, template=big_pic, mode=1, delete=delete)
        result = str_find(target, _list)
        if result:
            return result
        else:
            return False

    def wait_pic(self, template_path, zone="ALL", wait_time=(1000, 10), similar=0.7):
        while 1:
            for i in range(wait_time[1]):
                p, s = self.find_pic(template_path, zone)
                if s >= similar:
                    return p
                else:
                    sleep(wait_time[0] / 1000)
            if self.soft.isforeground():
                raise RuntimeError("识别超时")
            else:
                self.soft.foreground()
                self.logger("切换顶层窗口")

    def wait_text(self, target, zone="ALL", wait_time=(1000, 10)):
        while 1:
            for i in range(wait_time[1]):
                _list = self.ocr(zone, mode=1)
                result = str_find(target, _list)
                if result:
                    return result
                else:
                    sleep(wait_time[0] / 1000)
            if self.soft.isforeground():
                raise RuntimeError("识别超时")
            else:
                self.soft.foreground()
                self.logger("切换顶层窗口")


if __name__ == '__main__':
    print()
    # env = Environment(1920, 1080)
    # result = ocr(big_pic=r"D:\Kin\Pictures\court.png")
    # print(result)
    # exe_path = r"tools\ocr\PaddleOCR-json_v.1.3.1\PaddleOCR-json.exe"
    # abs_path = os.path.join(os.getcwd(), exe_path)
    # print(abs_path)
    # print(os.path.exists(abs_path))
