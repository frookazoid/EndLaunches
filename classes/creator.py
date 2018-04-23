import colorama, requests, random
from classes.logger import logger
from time import sleep
from faker import Faker
from bs4 import BeautifulSoup as bs
from requests_toolbelt import MultipartEncoder

class create():
    def __init__(self, x, proxies, config):
        colorama.init()
        self.s = requests.session()
        self.x = x
        self.proxies = proxies
        self.faker = Faker()
        self.config = config
        self.log = logger().log
        self.url = "https://www.endclothing.com/us/customer/account/createpost/"
        self.password = self.config['generator']['password']
        self.s.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            #'Access-Control-Allow-Credentials': 'true',
            #'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'DNT': '1',
            #'Referer': 'https://launches.endclothing.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)


    def grab(self):
        self.s.cookies.clear()
        self.proxy = random.choice(self.proxies)
        self.proxyDict = {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy
        }
        self.s.proxies.update(self.proxyDict)
        re = self.s.get("https://www.endclothing.com/us/customer/account/login/")
        self.formKey = bs(re.text, 'html.parser').find('input', {'name': 'form_key'})['value']
        self.cookies = self.s.cookies.get_dict()
        self.cookie_string = "; ".join([str(x) + "=" + str(y) for x, y in self.cookies.items()])

    def gen(self):
        self.fname = self.faker.first_name()
        self.lname = self.faker.last_name()
        self.dob = str(random.randint(10,12)) + '/' + str(random.randint(10,30)) + '/' + str(random.randint(1970,1980))

        self.s.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarycv56Q1LbZ1RQzL3f',
            #'cookie': self.cookie_string,
            'DNT': '1',
            'Referer': 'https://www.endclothing.com/us/customer/account/login/',
            'upgrade-insecure-requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)



        self.email = self.fname + self.lname + str(random.randint(1, 100)) + "@" + self.config['generator']['catchall']

        data = {
            'form_key': (None, self.formKey),
            'success_url': (None, ''),
            'error_url': (None, ''),
            'firstname': (None, self.fname),
            'lastname': (None, self.lname),
            'email': (None, self.email),
            'dob': (None, self.dob),
            'password': (None, self.password),
            'password_confirmation': (None, self.password)
        }
        m = MultipartEncoder(data, boundary='----WebKitFormBoundarycv56Q1LbZ1RQzL3f')
        re = self.s.post(self.url, data=m.to_string())
        if 'welcome' in re.text:
            self.log('[%s] Account Created | (%s)' % (self.x, self.email), "success")
            with open("./config/accounts.txt", "a") as f:
                f.write(self.email + ":" + self.password + "\n")
                f.close()
            self.s.cookies.clear()
        else:
            self.log('[%s] Error Creating  | (%s)' % (self.x, self.email), "error")
            print(re.text)
            sleep(10)
            self.grab()




    def run(self):
        for i in range(25):
            self.grab()
            self.gen()