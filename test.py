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
