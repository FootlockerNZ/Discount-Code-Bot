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
        self.session = session
        self.refferal = refferal
        self.task = task
        self.user = user
        self.server = server
        config = Data().loadJson('config.json')
        self.country_code = config['pvaCountry']
        self.api_key = config['pvaAPI']
        self.slug = f'[SMS CONFIRMER] [{server}] [{user}] [{task}]: '

        

    def start_task(self):
        if(self.getNumber()):
            time.sleep(3)
            if(self.sendSMS()):
                time.sleep(3)
                return self.retrieveSMS()

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
                    response = self.session.post('https://snkrdunk.com/en/v1/account/sms-verification',headers=headers,json={"countryCode":self.country_code,"phoneNumber":self.phoneNumber},proxies=random.choice(self.proxies))
                else:
                    response = self.session.post('https://snkrdunk.com/en/v1/account/sms-verification',headers=headers,json={"countryCode":self.country_code,"phoneNumber":self.phoneNumber})

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
            else:
                print(response.text)
                count += 1
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(20)
                continue



    def cancelPhone(self):
        
        while True:
            log(self.slug+'Cancelling phone number...')
            try:
                if self.usingProxies:
                    response = requests.get(f'https://smspva.com/priemnik.php?metod=ban&country={self.country_code}&service=opt190&id='+str(self.phoneNumber_id)+'&apikey='+self.api_key,proxies=random.choice(self.proxies))
                else:
                    response = requests.get(f'https://smspva.com/priemnik.php?metod=ban&country={self.country_code}&service=opt190&id='+str(self.phoneNumber_id)+'&apikey='+self.api_key)

            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SMSPVA')
                time.sleep(1)
                continue

            if response.status_code == 200:
                log(self.slug+'Number cancelled successfully')
                return True
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue

    def retrieveSMS(self):
        count = 0 
        while True:
            count += 1
            if count == 6:
                self.sendSMS()

            if count == 12:
                self.cancelPhone()
                self.getNumber()
                self.sendSMS()
                count = 0

            log(self.slug+"Retrieving SMS ("+str(count)+')...')
            url = f'https://smspva.com/priemnik.php?metod=get_sms&country={self.country_code}&service=opt190&id='+str(self.phoneNumber_id)+'&apikey='+self.api_key

            try:
                if self.usingProxies:
                    response = requests.get(url,proxies=random.choice(self.proxies))
                else:
                    response = requests.get(url)
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
                    time.sleep(10)
                    continue
                
                if response['response'] != '1' or response['response'] == 'ok':
                    log(self.slug+"Waiting for SMS ("+str(count)+')...')
                    time.sleep(20)
                    continue
                else:
                    log(self.slug+"Got SMS")
                    return response['text'].split(':')[1].strip()

            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(10)
                continue

    def getNumber(self):
        no_number_count = 0
        while True:
            log(self.slug+'Requesting number...')
            url = f'https://smspva.com/priemnik.php?metod=get_number&country={self.country_code}&service=opt190&apikey='+self.api_key
            #https://smspva.com/reg-sms.api.php?type=get_number&country_id=ID&operator=Total_ID&service=opt190&id=1&redirectphone=0
            try:
                if self.usingProxies:
                    response = requests.get(url,proxies=random.choice(self.proxies))
                else:
                    response = requests.get(url)
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
                    time.sleep(10)
                    continue

                if(response['response'] == '1' or response['response'] == 'ok'):
                    self.phoneNumber = str(response['number'])
                    
                    self.slug = f'[SMS CONFIRMER] [{self.server}] [{self.user}] [{self.phoneNumber}] [{self.task}]: '
                    self.phoneNumber_id = str(response['id'])
                    log(self.slug+"Got number")
                    return True
                else:
                    log(self.slug+"Error while getting whole number")
                    no_number_count += 1
                    print(response)
                    time.sleep(10)
                    continue

            elif response.status_code == 403:
                log(self.slug+"Unauthorized Access [403]")
                time.sleep(20)
                continue
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(20)
                continue


