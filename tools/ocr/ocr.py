from .PPOCR_api import GetOcrApi
from PIL import Image
from io import BytesIO
from cpufeature import CPUFeature
from os.path import exists, join, abspath
from sys import exit as sysexit


class OCR:
    def __init__(self, logger, workdir):
        self.logger = logger
        self.workdir = workdir
        self.cpu_feature = CPUFeature["AVX2"]
        if self.cpu_feature:
            self.exe_name = "PaddleOCR-json_v.1.3.1(simplify)"
            self.load_url = ("https://github.moeyy.xyz/"
                             "https://github.com/Kin-L/SucroseGameAssistant/releases/download/ocr/"
                             "PaddleOCR-json_v.1.3.1.simplify.zip")
            self.exe_path = r"3rd_package\PaddleOCR-json_v.1.3.1(simplify)\PaddleOCR-json.exe"
            self.logger.debug("CPU 支持 AVX2 指令集，使用 PaddleOCR-json")
        else:
            self.exe_name = "RapidOCR-json_v0.2.0(simplify)"
            self.load_url = ("https://github.moeyy.xyz/"
                             "https://github.com/Kin-L/SucroseGameAssistant/releases/download/ocr/"
                             "RapidOCR-json_v0.2.0.simplify.zip")
            self.exe_path = r"3rd_package\RapidOCR-json_v0.2.0(simplify)\RapidOCR-json.exe"
            self.logger.debug("CPU 不支持 AVX2 指令集，使用 RapidOCR-json")
        self.running = None

    def check(self):
        abs_path = join(self.workdir, self.exe_path)
        if exists(abs_path):
            return True
        else:
            return False

    def enable(self):
        if self.running is None:
            try:
                self.logger.debug("开始初始化OCR...")
                self.running = GetOcrApi(self.exe_path)
                self.logger.debug("初始化OCR完成")
            except Exception as e:
                self.logger.error(f"初始化OCR失败:{e}")
                self.running = None
                self.logger.info("请尝试重新下载或解压")
                self.logger.info("若 Win7 报错计算机中丢失 VCOMP140.DLL,请安装 VC运行库")
                self.logger.info("https://aka.ms/vs/17/release/vc_redist.x64.exe")
                sysexit(1)
        else:
            self.logger.debug("OCR早已启用")

    def disable(self):
        if self.running is None:
            self.logger.debug("OCR早已关闭")
        else:
            self.running.exit()
            self.running = None
            self.logger.debug("OCR关闭")

    @staticmethod
    def convert_format(result):
        if result['code'] != 100:
            return False
        converted_result = []

        for item in result['data']:
            box = item['box']
            text = item['text']
            score = item['score']

            converted_item = [
                [box[0], box[1], box[2], box[3]],
                (text, score)
            ]

            converted_result.append(converted_item)

        return converted_result

    def run(self, image):
        # self.instance_ocr()
        try:
            if isinstance(image, Image.Image):
                pass
            elif isinstance(image, str):
                return self.running.run(abspath(image))
            else:  # 默认为 np.ndarray，避免需要import numpy
                image = Image.fromarray(image)
            image_stream = BytesIO()
            image.save(image_stream, format="PNG")
            image_bytes = image_stream.getvalue()
            return self.running.runBytes(image_bytes)
        except Exception as e:
            self.logger.error(e)
            return r"{}"

    def recognize_single_line(self, image, blacklist=None):
        results = self.convert_format(self.run(image))
        if results:
            for i in range(len(results)):
                line_text = results[i][1][0] if results and len(results[i]) > 0 else ""
                if blacklist and any(char == line_text for char in blacklist):
                    continue
                else:
                    return line_text, results[i][1][1]
        return None

    def output(self, image):
        if isinstance(image, Image.Image):
            pass
        elif isinstance(image, str):
            return self.running.run(abspath(image))
        else:  # 默认为 np.ndarray，避免需要import numpy
            image = Image.fromarray(image)
        image_stream = BytesIO()
        image.save(image_stream, format="PNG")
        image_bytes = image_stream.getvalue()
        result = self.running.runBytes(image_bytes)
        if result['code'] == 101:
            return None
        elif result['code'] != 100:
            self.logger.debug(result)
            return False
        converted_result = []
        for item in result['data']:
            box = item['box']
            text = item['text']
            score = item['score']
            converted_item = [[box[0], box[1], box[2], box[3]], (text, score)]
            converted_result.append(converted_item)
        return converted_result
