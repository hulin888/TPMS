from paddleocr import PaddleOCR


def initialize():
    global ocrmodel
    ocrmodel = PaddleOCR(use_angle_cls=True, lang='en', use_gpu = False, show_log = False)
    print("Paddle OCR Model Initialized")
# if __name__ == "__main__":
initialize()