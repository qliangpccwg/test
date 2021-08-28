import requests
import ast


def parametrize(param_list):
    def wapper(func):
        def caller(*args, **kwargs):
            for v in param_list:
                func(args[0], v)
        return caller
    return wapper


class Test_Server:
    def __init__(self, ip='127.0.0.1', port='5000'):
        self.ip = '127.0.0.1'
        self.port = '5000'
        self.dst = 'http://' + self.ip + ':' + self.port
        self.enum = ['E2E', 'Headless Chrome', 'Jest', 'Selenium']
        self.cases = filter(lambda k: k.startswith(
            'test_'), Test_Server.__dict__)

    def test_option_api(self, path='/toolbox/options'):
        self.url = self.dst + path
        resp = requests.get(self.url)
        assert resp.status_code == 200
        for k, v in enumerate(ast.literal_eval(resp.text)):
            assert self.enum[k] == v

    def test_toolbox_query_empty(self, path='/toolbox'):
        self.url = self.dst + path
        resp = requests.get(self.url)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content['message'] == 'success'
        assert resp_content['data'] == []
        assert resp.status_code == 200

    def test_toolbox_create_method_error(self, path='/toolbox/create'):
        self.url = self.dst + path
        resp = requests.post(self.url)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content.get('error', None) != None
        assert resp.status_code == 400

    @parametrize([{'name': 'key1'}, {'tools': 'val1'},{'tools': 'val1','n': 'key1'}])
    def test_toolbox_create_param_error(self, data, path='/toolbox/create'):
        resp = requests.post(self.url, json=data)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content.get('error', None) != None
        assert resp.status_code == 400

    @parametrize([{'name': 'key1', 'tools': 'val1'}, {'name': 'key2', 'tools': 'val2'}])
    def test_toolbox_create_success(self, data, path='/toolbox/create'):
        resp = requests.post(self.url, json=data)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content['message'] == 'success'
        assert resp.status_code == 200

    @parametrize([{'name': 'key1', 'tools': 'val1'}, {'name': 'key2', 'tools': 'val2'}])
    def test_toolbox_create_idempotency(self, data, path='/toolbox/create'):
        resp = requests.post(self.url, json=data)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content.get(
            'error', None) == 'SQLITE_CONSTRAINT: UNIQUE constraint failed: toolbox_prefs.name'
        assert resp.status_code == 400

    @parametrize([[{'name': 'key1', 'tools': 'val1'}, {'name': 'key2', 'tools': 'val2'}]])
    def test_toolbox_query_nonempty(self, data, path='/toolbox'):
        self.url = self.dst + path
        resp = requests.get(self.url)
        resp_content = ast.literal_eval(resp.text)
        assert resp_content['message'] == 'success'
        assert resp_content['data'] != []
        assert resp.status_code == 200
        tmp = resp_content['data']
        tmp.sort(key=lambda x: x['id'])
        for k, v in enumerate(tmp):
            v.pop('id')
            assert v == data[k]

    def test_pitfall(self):
        print('''
        Mind pointing out some potential flaws or pitfalls?
        1 sql 注入没有预防
        2 create接口没有数据类型校验
        3 插入数据量没有上限
        ''')

    def run_cases(self):
        for case in self.cases:
            try:
                getattr(self, case)()
            except Exception as e:
                print(f'{case} fail', repr(e))
            else:
                print(f'{case} sucess')


if __name__ == '__main__':

    t = Test_Server()
    t.run_cases()
