import requests
import colorama
import hashlib
import string
from time import sleep
from termcolor import *
import ctypes
import time
from utility import *
from bs4 import *
import random
#from smspva import *
from sim import *
from EMAILHandler import *
colorama.init()
from classes.logger import logger
log = logger().log


    
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}

ACTIVE_TASKS = 0
FAILED_TASKS = 0
SUCESSFUL_TASKS = 0
GETTING_CSRF = 0
CREATING_ACCOUNT = 0
WAITING_FOR_EMAIL = 0
GETTING_PHONE = 0
WAITING_FOR_SMS = 0
FINALISING = 0

def addAccount(email, password):
    with open('Codes/snkrdunkaccounts.txt', 'a') as k:
        k.write(email+":"+password+"\n")


class SNKRDUNK:
    def __init__(self, referral, domains, apiheaders, user, server, task):
        global ACTIVE_TASKS
        ACTIVE_TASKS += 1
        self.updateStatus()
        self.task = task
        self.domains = domains
        self.referral = referral
        self.user = user
        self.server = server
        self.slug = f'[GENERATOR] [{server}] [{user}] [{str(task)}] : '
        self.config = Data().loadJson('config.json')
        self.proxies = Data().loadProxies('proxies.txt')
        self.apiheaders = apiheaders
        self.session = requests.Session()
        self.headers = {
            'authority': 'snkrdunk.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
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
        log(self.slug+'Starting Task')
        self.start_task()
    
    def generate_password(self):
        capital_letter = random.choice(string.ascii_uppercase)
        middle_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        special_char = '!'
        password = capital_letter + middle_part + special_char
        return password

    def start_task(self):
        global SUCESSFUL_TASKS
        global FINALISING
        global ACTIVE_TASKS
        sleep(random.randint(1, 30))
        if (self.setCookie()):
            if(self.getCSRF('https://snkrdunk.com/en/signup')):
                if(self.create_acount()):
                    if(self.getEmailVerification()):
                        if(self.verifyEmail()):
                            if(self.sendPhoneVerification()):
                                if(self.getCSRF('https://snkrdunk.com/en/account/address?slide=right')):
                                    if(self.verifyAddress()):
                                        if(self.applyreferral()):
                                            #if(self.applyOtherReferral()):
                                                SUCESSFUL_TASKS += 1
                                                FINALISING -= 1
                                                ACTIVE_TASKS -= 1
                                                self.updateStatus()
                                                return True
                            





        global FAILED_TASKS
        FAILED_TASKS += 1
        self.updateStatus()
        log(self.slug+'Task Failed')
        self.session = requests.Session()
        return self.start_task()
    
    def capsolver(self):
        api_key = self.config['capsolverAPI']
        site_url = "https://snkrdunk.com/en/signup" 
        payload = {
            "clientKey": api_key,
            "task": {
                "type": 'AntiAwsWafTaskProxyLess',
                "websiteURL": site_url
            }
        }
        res = requests.post("https://api.capsolver.com/createTask", json=payload)
        resp = res.json()
        task_id = resp.get("taskId")
        if not task_id:
            log(self.slug+"Failed to create task:", res.text)
            return
        log(self.slug+f"Got taskId: {task_id} / Getting result...")
 
        while True:
            time.sleep(1)  
            payload = {"clientKey": api_key, "taskId": task_id}
            res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
            resp = res.json()
            status = resp.get("status")
            if status == "ready":
                return resp.get("solution", {}).get('cookie')
            if status == "failed" or resp.get("errorId"):
                log(self.slug+"Solve failed! response:", res.text)
                return None
    
    def setCookie(self):
        x = 0
        while True:
            log(self.slug+'Setting aws waf cookie...')
            token = self.capsolver()
            if token is not None:
                cookie_name = 'aws-waf-token'
                log(self.slug+'Successfully set cookie')
                self.session.cookies.set(cookie_name, token)
                return True
            else:
                x +=1
                if x == 3:
                    return False
                sleep(3)

 

    def applyreferral(self):
        while True:
            log(self.slug+'Applying referral {}...'.format(self.referral))
            try:
                self.headers['referer'] = 'https://snkrdunk.com/en/signup'

                response = self.session.post('https://snkrdunk.com/en/v1/invitation',headers=self.headers,json={'code':self.referral})
            except:
                log(self.slug+'Failed to connect to SNKRDUNK')
                time.sleep(1)
                continue

            if response.status_code == 200:
                log(self.slug+"Referral succcessfully applied")
                addAccount(self.email, self.password)
                return True
            elif response.status_code == 404:
                log(self.slug+"Referral code is incorrect.")
                return True
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue



    def applyOtheReferral(self):
        while True:
            log(self.slug+'Applying promotion {}...'.format('HARRISON'))
            try:
                self.headers['referer'] = 'https://snkrdunk.com/en/account/coupons?slide=right'

                data = {
                    'classCode': 'YHPE',
                    'eventCode': 'HARRISON',
                }
                response = self.session.post('https://snkrdunk.com/en/v1/promotional-events/participate?classCode=YHPE&eventCode=HARRISON',headers=self.headers,data=data)
            except:
                log(self.slug+'Failed to connect to SNKRDUNK')
                time.sleep(1)
                continue

            if response.status_code == 200:
                log(self.slug+"Referral succcessfully applied")
                addAccount(self.email)
                return True
            elif response.status_code == 404:
                log(self.slug+"Referral code is incorrect.")
                return True
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue

    def verifyAddress(self):
        global FINALISING
        FINALISING += 1
        self.updateStatus()
        self.headers['referer'] = 'https://snkrdunk.com/en/signup'

        while True:
            log(self.slug+'Verifying address...')
            try:
                response = self.session.post('https://snkrdunk.com/en/account/address?slide=right',headers=self.headers,data={'firstName': 'ZZZ','lastName': 'ZZZ','phoneNumber':444000444,'country': 'AU','streetAddress': '300 Murray St','aptSuite': 'A','city': 'Perth','region': 'WA','postCode':6000,'csrf_token':self.csrf_token},proxies=random.choice(self.proxies))
            except:
                log(self.slug+"Failed to connect to SNKRDUNK")
                time.sleep(1)
                continue

            if response.status_code == 200:
                log(self.slug+'Address successfully verified')
                return True
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue

        
    def updateStatus(self):
        return
        #ctypes.windll.kernel32.SetConsoleTitleW(f"SNKRDUNK GEN | AT: {str(ACTIVE_TASKS)} | FT: {str(FAILED_TASKS)} | ST: {str(SUCESSFUL_TASKS)} | GCSRF: {str(GETTING_CSRF)} | ACC: {str(CREATING_ACCOUNT)} | EMAIL: {str(WAITING_FOR_EMAIL)} | PHONE: {str(GETTING_PHONE)} | SMS: {str(WAITING_FOR_SMS)} | FINAL: {str(FINALISING)}")


    def sendPhoneVerification(self):
        global GETTING_PHONE
        GETTING_PHONE += 1
        self.updateStatus()
        self.headers['referer'] = 'https://snkrdunk.com/en/signup'

        while True:
            log(self.slug+'Verifying phone...')
            k = SMS(self.referral,self.session,self.proxies, self.user, self.server, self.task).start_task()
            if not k:
                log(self.slug+"Error while verifying phone")   
                return False
            try:
                response = self.session.patch('https://snkrdunk.com/en/v1/account/sms-verification',headers=self.headers,json={'pinCode':k},proxies=random.choice(self.proxies))
            except Exception as e:
                print(e)
                log(self.slug+'Failed to connect to SNKRDUNK')
                time.sleep(1)
                continue
            
            if response.status_code == 200:
                log(self.slug+"Phone successfully verified")
                GETTING_PHONE -= 1
                self.updateStatus()
                return True
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue




    def create_acount(self):
        global CREATING_ACCOUNT
        CREATING_ACCOUNT += 1
        self.updateStatus()
        

        while True:
            log(self.slug+"Creating account...")
            self.username = 'swine'+str(random.randint(0,99999))+'codes'+str(random.randint(0,99999))
            self.email = self.username + random.choice(self.domains)
            self.slug = f'[GENERATOR] [{self.server}] [{self.user}] [{self.email}] [{str(self.task)}] : '
            self.password = self.generate_password()
            self.headers['referer'] = 'https://snkrdunk.com/en/signup'
            data = {
                'username': self.username,
                'email': self.email,
                'password': self.password,
                'agreement': 'on',
                'csrf_token': self.csrf_token,
                'tzDatabaseName': 'Australia/Adelaide'
            }

            try:
                response = self.session.post('https://snkrdunk.com/en/signup',data=data,proxies=random.choice(self.proxies),headers=self.headers)
            except:
                log(self.slug+'Failed to connect to SNKRDUNK')
                time.sleep(1)
                continue

            if response.status_code == 200:
                CREATING_ACCOUNT -= 1
                self.updateStatus()
                log(self.slug+'Account successfully created')
                return True

            elif response.status_code == 403:
                log(self.slug+'Unauthorized Access [403]')
                time.sleep(1)
                continue
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue

    def verifyEmail(self):
        global WAITING_FOR_EMAIL
        WAITING_FOR_EMAIL += 1
        self.updateStatus()
        while True:
            log(self.slug+"Verifying email...")
            try:
                response = self.session.get(self.activation_link,headers=self.headers,proxies=random.choice(self.proxies))
            except:
                log(self.slug+"Failed to connect to SNKRDUNK")
                time.sleep(1)
                continue

            if response.status_code == 200:
                log(self.slug+'Email successfully verified')
                WAITING_FOR_EMAIL -= 1
                self.updateStatus()
                return True
            elif response.status_code == 403:
                log(self.slug+"Unauthorized Access [403]")
                time.sleep(1)
                continue
            else:
                log(self.slug+"Bad Response Status "+str(response.status_code))
                time.sleep(1)
                continue


    
    def getEmailVerification(self):
        log(self.slug+"Getting email verification...")
        global WAITING_FOR_EMAIL
        WAITING_FOR_EMAIL += 1
        self.updateStatus()


        self.activation_link = emailAPI(self.email, self.apiheaders, self.proxies, self.user, self.server).check_inbox() 
        if(self.activation_link == False):
            log(self.slug+'Email verification not found')
            return False

        WAITING_FOR_EMAIL -= 1
        self.updateStatus()
        log(self.slug+'Found verification link')
        return True


    def getCSRF(self,url):
        global GETTING_CSRF
        GETTING_CSRF += 1
        self.updateStatus()
        while True:
            log(self.slug+'Getting CSRF token...')
            try:
                response = self.session.get(url,proxies=random.choice(self.proxies),headers=self.headers)
            except Exception as e:
                print(e)
                log(self.slug+"Failed to connect to SNKRDUNK")
                time.sleep(1)
                continue

            if response.status_code == 200:
                soup = BeautifulSoup(response.content,'html.parser')
                try:
                    csrf_token = soup.find("input",attrs={'name':'csrf_token'})['value']
                except:
                    log(self.slug+'Error finding CSRF token')
                    time.sleep(1)
                    continue

                self.csrf_token = csrf_token
                GETTING_CSRF -= 1
                self.updateStatus()
                log(self.slug+'Got CSRF')
                return True

            elif response.status_code == 403:
                log(self.slug+'Unauthorized Access [403]')
                time.sleep(1)
                continue
            else:
                
                log(self.slug+'Bad response status '+str(response.status_code))
                print(response.text)
                time.sleep(1)
                continue








