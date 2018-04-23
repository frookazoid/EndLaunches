import colorama, requests, random, datetime, base64
from classes.logger import logger
from bs4 import BeautifulSoup as bs
from time import sleep
from datetime import datetime


class launch():
    def __init__(self, x, proxies, config, accounts, profiles):
        colorama.init()
        self.s = requests.session()
        self.x = x
        self.proxies = proxies
        self.accounts = accounts
        self.proxy = random.choice(self.proxies)
        self.proxyDict = {
            'http':  'http://' + self.proxy,
            'https': 'https://' + self.proxy
        }
        self.s.proxies.update(self.proxyDict)
        self.config = config
        self.log = logger().log
        self.productURL = self.config['bot']['link']
        self.email = self.accounts.split(':')[0]
        self.password = self.accounts.split(':')[1]
        self.profiles = profiles

    def login(self): #logging in
        self.s.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'DNT': '1',
            'Referer': 'https://launches.endclothing.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)
        data = {
            'login[email]': self.email,
            'login[password]': self.password
        }
        login_URL = "https://launches-api.endclothing.com/api/account/login"
        re = self.s.post(login_URL, data=data)
        if re.status_code == 200:
            self.log('[%s] Logged in!       | ' % self.x + '(%s)' % self.email, "success")
            json = re.json()
            self.cID = json['id']
            self.grab() #Call function to grab necessary info for setting info
        else:
            self.log('[%s] Error while logging in |  ' % self.x + '(%s)' % self.email, "error")
            quit()

    def ship(self): #Setting Shipping
        self.s.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'DNT': '1',
            'Referer': 'https://launches.endclothing.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)
        data = {
            'customerId': self.cID,
            'address[city]': self.profiles['city'],
            'address[company]': '',
            'address[countryId]': '6',
            'address[firstName]': self.profiles['first'],
            'address[lastName]': self.profiles['last'],
            'address[postCode]': self.profiles['zip'],
            'address[regionId]': '54',
            'address[regionName]': '',
            'address[street1]': self.profiles['address'],
            'address[street2]': self.profiles['address2'],
            'address[telephone]': self.profiles['phone'],
            'address[defaultBilling]': 'false',
            'address[defaultShipping]': 'true'
        }
        addressURL = "https://launches-api.endclothing.com/api/account/addresses"
        re = self.s.post(addressURL, data=data)
        if self.profiles['first'] in re.text:
            self.log("[%s] Shipping set!    | (%s)" % (self.x, self.email), "success")
            json = re.json()
            self.BID = json['default_shipping']
            self.cc()
        else:
            self.log("[%s] Error Setting shipping info... Retrying: %s " % (self.x, str(re.status_code)), "error")
            self.log('[%s] %s' % (self.x, re.text), "error")
            sleep(30)
            quit()



    def cc(self): #Set CC info
        data = {
            "{}": ''
        }
        re = self.s.post("https://launches-api.endclothing.com/braintree/payment-method/token", data=data)
        if "value" in re.text:
            json = re.json()
            key = json['value']
            decode = base64.b64decode(key)
            idk = decode
            utf = idk.decode("utf-8")
            data = utf.replace('\\u0026', '&')
            fml = data.split(',')[1]
            fml2 = fml.split(':"')[1]
            self.fml3 = fml2.replace('"', '')



        data = {
            "_meta": {
                "merchantAppId": "launches.endclothing.com",
                "platform": "web",
                "sdkVersion": "3.11.0",
                "source": "hosted-fields",
                "integration": "custom",
                "integrationType": "custom",
                "sessionId": "59ccded6-807f-40cf-846e-2179c93e6e4b"

            },
            "creditCard": {
                "number": self.profiles['ccNum'],
                "cvv": self.profiles['cvv'],
                "expiration_month": self.profiles['month'],
                "expiration_year": self.profiles['year'],
                "options": {
                    "validate": 'false'
                }
            },
            "braintreeLibraryVersion": "braintree/web/3.11.0",
            "authorizationFingerprint": self.fml3
        }

        self.s.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Referer': 'ttps://assets.braintreegateway.com/web/3.11.0/html/hosted-fields-frame.min.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)

        re = self.s.post("https://api.braintreegateway.com/merchants/s3qf7btpbbghkdyp/client_api/v1/payment_methods/credit_cards", json=data)
        if re.status_code == 202:
            json = re.json()
            self.nonce = json['creditCards'][0]['nonce']
        else:
            self.log("[%s] Error on stage 1 of CC" % self.x, "error")
            sleep(5)
            self.cc()

        data = {
            'payment_method[customer_id]': self.cID,
            'payment_method[website_id]': '2',
            'payment_method[product_id]': self.pid,
            'payment_method[payment_method][id]': '',
            'payment_method[payment_method][token]': '',
            'payment_method[payment_method][type]': 'launches',
            'payment_method[payment_method][default]': '',
            'payment_method[payment_method_nonce]': self.nonce,
            'payment_method[device_data]': '{"device_session_id": "a26750cd9cfaf884159665d2a3885cf6","fraud_merchant_id": "600810"}',
            'payment_method[billing_address][id]': self.BID,
            'payment_method[billing_address][firstName]': '',
            'payment_method[billing_address][lastName]': '',
            'payment_method[billing_address][telephone]': self.profiles['phone'],
            'payment_method[billing_address][company]': '',
            'payment_method[billing_address][street1]': '',
            'payment_method[billing_address][street2]': '',
            'payment_method[billing_address][city]': self.profiles['city'],
            'payment_method[billing_address][regionName]': '',
            'payment_method[billing_address][regionId]': '',
            'payment_method[billing_address][postCode]':'',
            'payment_method[billing_address][countryId]':'6',
            'payment_method[billing_address][braintreeAddressId]': '',
            'payment_method[billing_address][type]': '',
            'payment_method[default_payment]': 'true'
        }
        self.s.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cookie_string,
            'DNT': '1',
            'Referer': self.productURL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)
        re = self.s.post("https://launches-api.endclothing.com/api/account/payment-methods", data=data)
        if re.status_code == 201:
            self.log('[%s] Credit card set! | (%s)' % (self.x, self.email), "success")
            json = re.json()
            self.paymentID = json['id']
            self.enter()
        else:
            self.log('[%s] Error with setting credit card... retrying:  %s' % (self.x, str(re.status_code)), "error")
            sleep(5)
            self.cc()


    def grab(self): #Grab Product ID & Product Size ID
        self.s.headers.update({
            'host': 'launches.endclothing.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36',
            'upgrade-insecure-requests': 'true',
            'dnt': '1',
            'accept-language': 'en-US,en;q=0.9'
        })
        re = self.s.get(self.productURL)
        self.cookies = self.s.cookies.get_dict()
        self.cookie_string = "; ".join([str(x) + "=" + str(y) for x, y in self.cookies.items()])

        self.s.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json',
            'Cookie': self.cookie_string,
            'DNT': '1',
            'Referer': self.productURL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)

        pp = self.s.get(self.productURL).json()
        self.pid = pp['id']
        sid = pp['productSizes']
        self.sizeDict = []
        for items in sid:
            if self.profiles['size'] == items['sizeDescription']:
                self.size = items['id']
                self.ship() #Grabbed necessary info, Call function to set the info
            elif self.profiles['size'] == "random":
                print(items['id'])
                quit()
                self.size = random.choice(self.sizeDict)
                self.log('[%s] Random size: %s  | (%s)' % (self.size, self.x, self.email), "info")
                self.ship()  # Grabbed necessary info, Call function to set the info

    def enter(self):
        data = {
            'subscription[customer_id]': self.cID,
            'subscription[product_size_id]': self.size,
            'subscription[shipping_address_id]': self.BID,
            'subscription[shipping_address_type]': 'magento',
            'subscription[billing_address_id]': self.BID,
            'subscription[billing_address_type]': 'magento',
            'subscription[payment_method_id]': self.paymentID,
            'subscription[payment_method_type]': 'magento',
            'subscription[shipping_method_id]': '7',
            'subscription[website_id]': '2',
            'subscription[postcode]':  self.profiles['zip'],
            'subscription[street]': self.profiles['address']
        }
        self.s.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': self.cookie_string,
            'DNT': '1',
            'Referer': self.productURL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        }
        self.s.headers.update(self.s.headers)
        re = self.s.post("https://launches-api.endclothing.com/api/account/subscriptions", data=data)
        if re.status_code == 201:
            self.log('[%s] Entered Raffle!  | (%s)' % (self.x, self.email), "success")
        else:
            JSON = re.json()
            self.log('[%s] %s' % (self.x, JSON['message']), "success")


    def run(self):
        self.login()


