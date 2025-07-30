import requests
import hashlib
import random
from time import sleep
from classes.logger import logger
log = logger().log

class emailAPI:
    def __init__(self, email, apiheaders, proxies, user, server):
        self.email = email
        self.apiheaders = apiheaders
        self.proxies = proxies
        self.slug = '[EMAIL CONFIRMER] [{}] [{}] [{}] : '.format(server, user, self.email)
        

    def check_inbox(self):
        url = 'https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{}/'.format(str(hashlib.md5(bytes(self.email, encoding='utf-8')).hexdigest()))

        while True:
            log(self.slug+"Checking inbox...")

            try:
                r = requests.get(url, headers=self.apiheaders, timeout=10)
            except:
                log(self.slug+'Failed to connect to email api')
                sleep(5)
                continue
            
            if r.status_code == 200:
                try:
                    self.link = r.json()[0]['mail_text_only'].split('<a href="')[1].split('"')[0].replace("&amp;", "&")
                    log(self.slug+'Found message in inbox')
                    return self.link
                except:
                    if 'There are no emails yet' in r.text:
                        log(self.slug+'Inbox is empty')
                    else:
                        log(self.slug+'Error checking inbox')
                        print(r.text)
            else:
                log(self.slug+'Error checking inbox. [Status Code: {}]'.format(str(r.status_code)))
                print(r.text)

            sleep(5)
    
    
    def check_email(self):
            url = 'https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{}/'.format(str(hashlib.md5(bytes(self.email, encoding='utf-8')).hexdigest()))

            log(self.slug+"Checking inbox...")

            try:
                r = requests.get(url, headers=self.apiheaders, timeout=2)
            except Exception as e:
                log(self.slug+'Failed to connect to email api')
                return False, 'Request failed'
            
            if r.status_code == 200:
                try:
                    codes = []
                    for i in r.json():
                        try:
                            codes.append(i['mail_text_only'].split('Your verification code is:')[1].split('font-size:30px;line-height:44px;font-weight:bold;">')[1].split('<')[0])
                        except:
                            pass
                    if len(codes) != 0:
                        log(self.slug+'Found code(s) in inbox: '+', '.join(codes))
                        return True, codes
                    else:
                        log(self.slug+'Found no verification codes in inbox')
                        return False, 'Found no verification codes in inbox'
                except:
                    if 'There are no emails yet' in r.text:
                        log(self.slug+'Inbox is empty')
                        return False, 'Inbox is empty'
                    else:
                        log(self.slug+'Error checking inbox')
                        print(r.text)
                        return False, 'Exception occured'
            else:
                log(self.slug+'Error checking inbox. [Status Code: {}]'.format(str(r.status_code)))
                print(r.text)
                return False, 'Request failed'


    