import json
import base64
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class test:
    def __init__(self):
        self.IMAGE_URL = 'https://cdn.mos.cms.futurecdn.net/snbrHBRigvvzjxNGuUtcck.jpg'
        self.browser = webdriver.Chrome('./chromedriver')
        self.wait = WebDriverWait(self.browser, 20)
        self.cases = filter(lambda x: x.startswith('test_'), dir(self))

    def pre_process(self):
        self.browser.get('https://www.google.com.hk/imghp')
        self.browser.find_element_by_css_selector(
            '#sbtc > div > div.dRYYxd > div.ZaFQO').click()
        self.browser.find_element_by_css_selector('#Ycyxxc').send_keys(
            self.IMAGE_URL)
        self.browser.find_element_by_css_selector('#RZJ9Ub').click()

    def post_process(self):
        self.browser.quit()

    def get_search_list(self):
        e = self.browser.find_element_by_css_selector('#search')
        e_list = e.find_elements_by_class_name('g')
        assert e_list is not []
        return e_list

    def test_text_relevance(self):
        e = self.browser.find_element_by_css_selector(
            '#sbtc > div.SDkEP > div.a4bIc > input')
        assert 'moon' or '月' in e.get_property(
            'value'), "picture name doesn't have the related word moon or 月"
        e_list = self.get_search_list()
        for k, val in enumerate(e_list):
            assert 'moon' or '月' in val.text, f"the {k+1}th web page doesn't have the related word moon or 月"

    def test_img_content_relevance(self):
        import cv2
        import numpy as np
        from PIL import Image
        from io import BytesIO
        from skimage.measure import compare_ssim

        html = requests.get(self.IMAGE_URL, verify=False)
        src_img = Image.open(BytesIO(html.content))

        _src_img = cv2.resize(np.asarray(src_img), (256, 256))
        _src_img = cv2.cvtColor(_src_img, cv2.COLOR_BGR2GRAY)

        e_list = self.browser.find_elements_by_css_selector(
            '#rso > div:nth-child(3) > div.normal-header ~ div')
        for k, e in enumerate(e_list):
            target_img_base64 = e.find_element_by_tag_name('img').get_property(
                'src').split('data:image/jpeg;base64,')[1]
            target_img_raw = base64.urlsafe_b64decode(target_img_base64)
            target_img = Image.open(BytesIO(target_img_raw))
            _target_img = cv2.resize(np.asarray(target_img), (256, 256))
            _target_img = cv2.cvtColor(_target_img, cv2.COLOR_BGR2GRAY)

            (score, _) = compare_ssim(_src_img, _target_img, full=True)

            assert score <= 0.3, f'the {k+1}th image is not related'

    def test_visit_target(self):
        with open('conf.json', 'r') as fd:
            obj = json.load(fd)
            self.VISIT_RESULT = obj['VISIT_RESULT']

        e_list = self.get_search_list()
        element = e_list[self.VISIT_RESULT - 1]
        self.wait.until(
            EC.visibility_of((element.find_element_by_tag_name('a'))))
        element.find_element_by_tag_name('a').click()
        self.wait.until(EC.number_of_windows_to_be(2))
        after = self.browser.window_handles[-1]
        self.browser.switch_to.window(after)

    def run_cases(self):
        for case in self.cases:
            try:
                getattr(self, case)()
            except Exception as e:
                print(repr(e))
            else:
                print(f'{case} sucess')

        self.browser.save_screenshot(f'{self.VISIT_RESULT}.png')


if __name__ == '__main__':

    t = test()
    t.pre_process()
    t.run_cases()
    t.post_process()

    
'''
1 最大长度的输入内容，正常显示，正常提交
2 内容为空，不可提交
3 内容为最小输入长度，可以提交
3 内容只有空格 或者 回车 不可提交
4 内容是否支持emoji的输入回显与提交
5 内容是否支持其他非ascii码字符（特殊符号与中文等）的输入回显与提交
6 通过系统文件提交框与拖拽方式，传入支持上传的文件类型，可以正确上传提交
7 通过系统文件提交框与拖拽方式，传入不支持上传的文件类型，不可以正确上传提交
8 通过系统文件提交框与拖拽方式，传入支持上传的文件类型，但附件大小超过限制，不可以正确上传提交
9 通过系统文件提交框与拖拽方式，传入支持上传的文件类型，但附件大小为0，不可以正确上传提交
10 同时有内容输入和附件，可以正确提交
11 单独有article 或 单独有附件，可以正确提交
12 通过系统文件提交框与拖拽方式，传入支持上传的文件类型，附件数量超过最大限制，不可以正确上传提交
13 通过系统文件提交框与拖拽方式，传入支持上传的文件类型，附件数量等于最大限制，正确上传提交
14 防止sql注入，xss注入，输入内容有> < + - \ ][ )( . ' " & NULL None % @ =，会正确转义
15 防止csrf，提交输入时，后端有跨域校验与csrf_token校验；权限校验，未登录的用户不可提交
16 性能：通过系统文件提交框与拖拽方式，传入支持上传的文件类型，附件数量等于最大限制，正确上传提交时，上传耗时如何
17 性能：页面完全加载时间 耗时如何
18 性能：1千、5千个用户同时，上传文件提交article，服务耗时如何，cpu，mem消耗如何
19 兼容性在chrome safari firefox 以及 windows mac linux,移动设备，不同的分辨率，不同的系统locale，满足上述使用

1 The maximum length of the input content, displayed correctly, and submitted correctly
2 The content is empty and cannot be submitted
3 The content is the minimum input length and can be submitted
3 The content has only spaces or enter and cannot be submitted
4 Does the content support emoji input echo and submission?
5 Whether the content supports other non-ASCII code characters (special symbols and Chinese, etc.) input echo and submission
6 Through the system file submission box and drag-and-drop method, input the file types that support uploading, and you can upload and submit correctly
7 Through the system file submission box and drag-and-drop method, input file types that do not support uploading, and they cannot be uploaded and submitted correctly.
8 Through the system file submission box and drag-and-drop method, import the file types that support uploading, but the attachment size exceeds the limit and cannot be uploaded and submitted correctly
9 Through the system file submission box and drag-and-drop method, input the file types that support uploading, but the attachment size is 0, and it cannot be uploaded and submitted correctly.
10 There are content input and attachments at the same time, which can be submitted correctly
11 There is a separate article or a separate attachment, which can be submitted correctly
12 Through the system file submission box and drag-and-drop method, input the file types that support uploading, and the number of attachments exceeds the maximum limit, and it cannot be uploaded and submitted correctly.
13 Through the system file submission box and drag-and-drop method, input the file types that support uploading, the number of attachments is equal to the maximum limit, upload and submit correctly
14 Prevent sql injection, xss injection, input content> <+-\ ][ )(. '"& NULL None% @ =, will be escaped correctly
15 Prevent csrf. When submitting input, the backend has cross-domain verification and csrf_token verification；Permission verification, users who are not logged in cannot submit
16 Performance: Through the system file submission box and drag-and-drop method, input the file types that support uploading, and the number of attachments is equal to the maximum limit. When uploading and submitting correctly, how long does it take to upload?
17 Performance: How long does the page fully load time?
18 Performance: 1 thousand and 5 thousand users at the same time, uploading files and submitting articles, how long does the service take? What is the consumption of cpu and mem?
19 Compatibility In chrome safari firefox and windows mac linux , and mobile devices, different resolutions, different system locales, meet the above use
'''
