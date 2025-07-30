import requests
from threading import Semaphore
import colorama
from termcolor import *
import time
import random
from utility import *
from classes.logger import logger

log = logger().log

screen_lock = Semaphore(value=1)
colorama.init()



class SMS:
    def __init__(self,refferal,session,proxies, user, server, task):
        self.proxies = proxies
        if len(proxies) != 0:
            self.usingProxies = True
        else:
            self.usingProxies = False
        self.task = task
        self.session = session
        self.refferal = refferal
        self.user = user
        self.server = server
        config = Data().loadJson('config.json')
        self.country_code = config['5simCountry']
        self.headers = {
            'Authorization': 'Bearer ' + config['5simAPI'],
            'Accept': 'application/json',
        }
        self.slug = f'[SMS CONFIRMER] [{server}] [{user}] [{task}]: '
        #self.countries = [{"code":"IN","5sim":"indonesia"}, {"code":"CA","5sim":"canada"}, {"code":"MY","5sim":"malaysia"}, {"code":"VT","5sim":"vietnam"}, {"code":"US","5sim":"usa"}]
        self.countries = [{"code":"US","5sim":"usa"}]
        #, {"code":"PH","5sim":"phillipines"}

        

    def start_task(self):
        if(self.getNumber()):
            time.sleep(10)
            if(self.sendSMS()):
                time.sleep(10)
                return self.retrieveSMS()
            else:
                return False

    def sendSMS(self):
        count = 0
        headers = {
                'authority': 'snkrdunk.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'referer': 'https://snkrdunk.com/en/signup',
                'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        }
        while True:
            if count == 10:
                self.cancelPhone()
                return False
            log(self.slug+'Sending SMS...')
            try:
                if self.usingProxies:
                    response = self.session.post('https://snkrdunk.com/en/v1/account/sms-verification',headers=headers,json={"countryCode":self.phoneCountry['code'],"phoneNumber":self.phoneNumber},proxies=random.choice(self.proxies))
                else:
                    response = self.session.post('https://snkrdunk.com/en/v1/account/sms-verification',headers=headers,json={"countryCode":self.phoneCountry['code'],"phoneNumber":self.phoneNumber})

            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SNKRDUNK')
                time.sleep(10)
                continue
            

            if response.status_code == 200:
                log(self.slug+"SMS sent")
                return True
            elif 'already' in str(response.content) and response.status_code == 409:
                log(self.slug+"Phone number already used")
                self.cancelPhone()
                self.getNumber()
                time.sleep(5)
                continue
            elif response.status_code == 403:
                log(self.slug+'Bad phone number, getting new one')
                self.cancelPhone()
                self.getNumber()
                time.sleep(5)
            else:
                print(response.text)
                count += 1
                log(self.slug+"Bad Response Status "+str(response.status_code))
                if 'Too many failed verification attempts. Please try again tomorrow' in response.text:
                    return False
                time.sleep(15)
                continue



    def cancelPhone(self):
        
        while True:
            log(self.slug+'Cancelling phone number...')
            try:
                url = f'https://5sim.net/v1/user/cancel/{self.orderID}'
                if self.usingProxies:
                    response = requests.get(url,headers=self.headers)
                else:
                    response = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SMSPVA')
                time.sleep(15)
                continue

            if response.status_code == 200:
                log(self.slug+'Number cancelled successfully')
                return True
            else:
                print(response.text)
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(15)
                continue

    def retrieveSMS(self):
        count = 0 
        while True:
            count += 1
            if count == 6:
                if self.sendSMS() == False:
                    return False

            if count == 12:
                self.cancelPhone()
                self.getNumber()
                if self.sendSMS() == False:
                    return False
                count = 0

                
            log(self.slug+"Retrieving SMS ("+str(count)+')...')
            url = f'https://5sim.net/v1/user/check/{self.orderID}'
            try:
                if self.usingProxies:
                    response = requests.get(url,headers=self.headers)
                else:
                    response = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SMSPVA')
                time.sleep(10)
                continue

            if response.status_code == 200:
                try:
                    response = response.json()
                    sms = response['sms'][0]['code']
                    return sms
                except:
                    log(self.slug+'Waiting for sms...')
                    time.sleep(15)
                    continue
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(15)
                continue



    def getNumber(self):
        no_number_count = 0
        
        while True:
            self.phoneCountry = random.choice(self.countries)
            log(self.slug+f'Requesting number from {self.phoneCountry["5sim"]}...')
            url = f"https://5sim.net/v1/user/buy/activation/{self.phoneCountry['5sim']}/any/snkrdunk?maxPrice=25"
            try:
                if self.usingProxies:
                    response = requests.get(url,headers=self.headers)
                else:
                    response = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SMSPVA')
                time.sleep(10)
                continue


            if response.status_code == 200:
                try:
                    response = response.json()
                except:
                    log(self.slug+'Error loading response')
                    time.sleep(15)
                    continue
                try:
                    data = response
                    self.orderID = str(data['id'])
                    self.phoneNumber = str(data['phone'])
                    self.slug = f'[SMS CONFIRMER] [{self.server}] [{self.user}] [{self.phoneNumber}] [{self.task}]: '
                    log(self.slug+"Got number")
                    return True
                except:
                    log(self.slug+"Error while getting whole number")
                    no_number_count += 1
                    print(response)
                    time.sleep(15)
                    continue

            elif response.status_code == 403:
                log(self.slug+"Unauthorized Access [403]")
                time.sleep(20)
                continue
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(15)
                continue


