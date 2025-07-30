import requests
import threading
import ctypes
import os
import discord
from csv import writer
from time import sleep
from colorama import init
from utility import *
from discord import app_commands
from discord.ext import commands
from gen import SNKRDUNK
from EMAILHandler import emailAPI
from classes.logger import logger

log = logger().log
init()


def get_domains():
    log('Getting available email domains...')
    url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"

    try:
        r = requests.get(url, headers=apiHeaders, timeout=10)
    except Exception as e:
        print(e)
        log('Failed to connect to email api')
        return None

    if r.status_code == 200:
        log('Found {} available email domains'.format(len(r.json())))
        return r.json()
    else:
        log('Failed to get domains. [Status Code: {}]'.format(str(r.status_code)))
        
    return None



def checkUnused(invoice_id):
    with open('completedOrders.txt', 'r+') as k:
        data = k.read()
        if invoice_id not in data:
            k.write(invoice_id+"\n")
            return True
        else:
            return False



def validateInvoice(invoice_id, email, username, server):
    headers = {
        "Authorization": f"Bearer {BILLGANG_API_KEY}",
        "Content-Type": "application/json"
    }
    slug = f'[{server}] [{username}] : '
    log(slug+"Checking order details...")
    
    try:
        r = requests.get(f'https://pg-api.billgang.com/v1/dash/shops/{SHOP_ID}/orders/{invoice_id}', headers=headers, timeout=5)
        
        if r.status_code == 200:
            data = r.json().get("data", {})
            charge = data.get("charge", {})
            customer_email = charge.get("customerForCharge", {}).get("email", "")
            title = data.get("partOrders", [{}])[0].get("productWithVariant", {}).get("name", "").lower()
            
            product_map = {
                'hype dc': 'HYPE DC',
                'stylerunner': 'STYLERUNNER',
                'subtype': 'SUBTYPE',
                'snkrdunk accounts': 'SNKRDUNK ACCOUNTS',
            }
            
            product = next((v for k, v in product_map.items() if k in title), 'INVALID')
            
            if charge.get('status', '') == 'PAID' or username == 'tab.co.nz':
                if customer_email.lower() == email.lower():
                    if product != 'INVALID':
                        price_map = {
                            'SNKRDUNK ACCOUNTS': 1,
                            'HYPE DC': 35,
                            'SUBTYPE': 35,
                            'STYLERUNNER': 20
                        }
                        
                        divisor = price_map.get(product, 1)
                        
                        if checkUnused(invoice_id):
                            return True, int(data['endPrice']["amount"] / divisor), product
                        else:
                            log(slug+f'Order {invoice_id} has already been fulfilled.')
                            return False, f'Order {invoice_id} has already been fulfilled.'
                    else:
                        log(slug+f'Product does not match that purchased for order {invoice_id}.')
                        return False, f'Product does not match that purchased for order {invoice_id}.'
                else:
                    log(slug+f'Provided email {email} does not match customer email for order {invoice_id}.')
                    return False, f'Provided email does not match customer email for order {invoice_id}.'
            else:
                log(slug+f'Order {invoice_id} has not been paid.')
                return False, f'Order {invoice_id} has not been paid.'
        else:
            log(slug+f'Failed to request order details. [Status Code: {r.status_code}]')
    except Exception as e:
        log(slug+f'Failed to get Billgang info. Error: {e}')
    
    return False, 'Unknown error'



def validateInvoiceSNKRDUNK(invoice_id, email, username, server):
    headers = {
        "Authorization": f"Bearer {BILLGANG_API_KEY}",
        "Content-Type": "application/json"
    }
    slug = f'[{server}] [{username}] : '
    log(slug+"Checking order details...")
    
    try:
        r = requests.get(f'https://pg-api.billgang.com/v1/dash/shops/{SHOP_ID}/orders/{invoice_id}', headers=headers, timeout=5)
        
        if r.status_code == 200:
            data = r.json().get("data", {})
            charge = data.get("charge", {})
            customer_email = charge.get("customerForCharge", {}).get("email", "")
            title = data.get("partOrders", [{}])[0].get("productWithVariant", {}).get("name", "").lower()
            
            product = 'SNKRDUNK GEN' if 'snkrdunk' in title and 'accounts' not in title else 'INVALID'
            
            if charge.get('status', '') == 'PAID':
                if customer_email and customer_email.lower() == email.lower():
                    if product != 'INVALID':
                        if checkUnused(invoice_id):
                            return True, int(data.get('endPrice', {}).get('amount', 0) / 1.5)
                        else:
                            log(slug+f'Order {invoice_id} has already been fulfilled.')
                            return False, f'Order {invoice_id} has already been fulfilled.'
                    else:
                        log(slug+f'Product does not match that purchased for order {invoice_id}.')
                        return False, f'Product does not match that purchased for order {invoice_id}. You may need to use the other redeem command.'
                else:
                    log(slug+f'Provided email {email} does not match customers for order {invoice_id}.')
                    return False, f'Provided email {email} does not match customers for order {invoice_id}.'
            else:
                log(slug+f'Order {invoice_id} has not been paid.')
                return False, f'Order {invoice_id} has not been paid.'
        else:
            log(slug+f'Failed to request order details. [Status Code: {r.status_code}]')
    except Exception as e:
        log(slug+f'Failed to get Billgang info. Error: {e}')
    
    return False, 'Unknown error'



def start_threads(slug, amount, code, domains, apiHeaders, username, server):
    for i in range(amount):
        log(slug+"Starting task "+str(i+1))
        thread = threading.Thread(target=SNKRDUNK,args=(code, domains, apiHeaders, username, server, i+1))
        thread.start()
        sleep(10)
    return



def getCode(store):
    with open('Codes/'+store.lower()+'.txt', 'r') as file:
            code = file.readline()
            remaining_content = file.read()

    with open('Codes/'+store.lower()+'.txt', 'w') as file:
            file.write(remaining_content)

    return code



def addCodes(codes, store):
    with open('Codes/'+store.lower()+'.txt', 'a') as file:
        for item in codes:
            file.write(str(item) + '\n')
    return



def writeCodes1(codes, order_id, product):
    with open('Codes/used.txt', 'a') as file:
        file.write(product + '-' +', '.join(codes) + " - "+order_id +'\n')
    return



def writeCodes(codes, order_id, product):
    try:
        f = open('Codes/used.csv', 'a', newline='')
        write = writer(f)
        data = [' '+product, ' '+', '.join(code.strip() for code in codes),' '+order_id]
        write.writerow(data)
        f.close()
        return True
    except Exception as e:
        print('error adding to used file: '+str(e))
    return False



def getUsedCodes():
    with open('Codes/used.txt', 'r') as file:
        return file.read().splitlines()



bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    log("Bot is running")
    try:
        synced = await bot.tree.sync()
        log(f"Synced {len(synced)} command(s)")
    except Exception as e:
        log(e)


@bot.tree.command(name="swine_redeem_snkrdunk")
@app_commands.describe(order_id="Your order number", email="Your order email", code="Your SNKRDUNK Referral Code")
async def swine_redeem_snkrdunk(interaction: discord.Interaction, order_id: str, email: str, code: str):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the snkrdunk redeem command")
    #product = "SNKRDUNK"
    if len(code) == 6:
        resp = validateInvoiceSNKRDUNK(order_id, email, interaction.user.name, interaction.guild)
        if resp[0]:
            log(slug+f"Successfully used the redeem command for order {order_id} with code {code}")
            await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(resp[1])} SNKRDUNK coupon(s). Please allow up to 10 minutes for them to show and make sure your currency is set to AUD", ephemeral=True)
            (threading.Thread(target=start_threads,args=(slug, int(resp[1]), code, domains, apiHeaders, interaction.user.name, interaction.guild))).start()
            if writeCodes('', order_id, 'SNKRDUNK Referral') != True:
                log(slug+'Failed to save to used.csv')
        else:
            await interaction.response.send_message(resp[1]+" If you think this is an error please contact <@377735961200689152>.", ephemeral=True)
    else:
        log(slug+f"Used the redeem command with an invalid referral code: {code}.")
        await interaction.response.send_message(f"{interaction.user.name} that referral code is invalid. It must be 6 characters in length.", ephemeral=True)



@bot.tree.command(name="swine_redeem")
@app_commands.describe(order_id="Your order number", email="Your order email")
async def swine_redeem(interaction: discord.Interaction, order_id: str, email: str):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the default redeem command")
    resp = validateInvoice(order_id, email, interaction.user.name, interaction.guild)
    if resp[0]:
        product = resp[2]
        if product.lower() == 'stylerunner':
            discount = '10%'
        else:
            discount = '20%'
        log(slug+f"Successfully used the redeem command for order {order_id} with product {product}")
        codes = []
        for i in range(resp[1]):
            while True:
                code = getCode(product.strip().replace(' ', ''))
                if code != '':
                    if code not in getUsedCodes():
                        codes.append(code)
                        break
                else:
                    break

        if len(codes) != resp[1]:
            log(slug+f"Not enough stock to fulfil order {order_id} for product {product}")
            if 'SNKRDUNK' in product:
                await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(resp[1])} {product}. Unfortunately there are not enough accounts in stock to fulfil your order. Please contact <@377735961200689152>.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(resp[1])} {product} {discount} off Code(s). Unfortunately there are not enough codes in stock to fulfil your order. Please contact <@377735961200689152>.", ephemeral=True)
            addCodes(codes, product.strip().replace(' ', ''))
        else:
            log(slug+f"Fulfilled order {order_id} for product {product}")
            if 'SNKRDUNK' in product:
                await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(resp[1])} {product}. They will be direct messaged to you.", ephemeral=True)
                await interaction.user.send(f"{interaction.user.name} here are your {str(resp[1])} {product}.\n\nEmail:Password\n"+''.join(codes))
            else:
                await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(resp[1])} {product}. They will be direct messaged to you.", ephemeral=True)
                await interaction.user.send(f"{interaction.user.name} here are your {str(resp[1])} {product} {discount} off Code(s).\n\n"+''.join(codes))
            if writeCodes(codes, order_id, product) != True:
                log(slug+'Failed to save to used.csv')
    else:
        await interaction.response.send_message(resp[1]+" If you think this is an error please contact <@377735961200689152>.", ephemeral=True)



@bot.tree.command(name="swine_admin_add")
@app_commands.describe(amount="Amount of codes",code="SNKRDUNK Referral Code")
async def swine_redeem(interaction: discord.Interaction, code: str, amount: int):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    if interaction.user.name == 'tab.co.nz':
        await interaction.response.send_message(f"{interaction.user.name} thank you for redeeming your {str(amount)} SNKRDUNK coupon(s). Please allow up to 10 minutes for them to show.", ephemeral=True)
        (threading.Thread(target=start_threads,args=(slug, int(amount), code, domains, apiHeaders, interaction.user.name, interaction.guild))).start()
    else:
        await interaction.response.send_message(f"{interaction.user.name}, nice try lil bro")


@bot.tree.command(name="swine_shop")
async def swine_shop(interaction: discord.Interaction):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the shop command")
    await interaction.response.send_message(f"{interaction.user.name} we currently offer codes for SNKRDUNK, Hype DC, Stylerunner and Subtype and accounts for SNKRDUNK.\n\nYou can shop discount codes at https://swinecodes.bgng.io/products")



@bot.tree.command(name="swine_help_snkrdunk")
async def swine_help_snkrdunk(interaction: discord.Interaction):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the snkrdunk help command")
    await interaction.response.send_message(f'{interaction.user.name} you have requested help.\n\nTo find your order number search **"Swine Codes"** in your email and it is the following mix of numbers and letters in the format ```000000-000000000000-000000```\n\nTo find your SNKRDUNK referral code go to the app then click **"Account"** which is located in the bottom right. Then click **"Invitation Code. GET coupons"** near the top under the Coupons tab. It is the mix of 6 numbers and letters.\n\nThen run the command **/swine_redeem_snkrdunk** and fill in the spots with the corresponding information and your all done.\n\nTo shop codes visit https://swinecodes.bgng.io/products.\n\nFor more support DM <@377735961200689152>.', ephemeral=True)



@bot.tree.command(name="swine_help")
async def swine_help(interaction: discord.Interaction):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the default help command")
    await interaction.response.send_message(f'{interaction.user.name} you have requested help.\n\nTo find your order number search **"Swine Codes"** in your email, with product either being *Stylerunner*, *Hype DC* or *Subtype*, and it is the following mix of numbers and letters in the format ```000000-000000000000-000000```\n\nThen run the command **/swine_redeem** and fill in the spots with the corresponding information and your all done. Make sure to store the codes somewhere as they will disappear after viewing a different channel.\n\nTo shop codes visit https://swinecodes.bgng.io/products.\n\nFor more support DM <@377735961200689152>.', ephemeral=True)



@bot.tree.command(name="swine_get_code")
@app_commands.describe(email="Your account email")
async def swine_redeem(interaction: discord.Interaction, email: str):
    slug = f'[{interaction.guild}] [{interaction.user.name}] : '
    log(slug+"Used the swine get code command")
    if '@' in email:
        await interaction.response.send_message(f"{interaction.user.name} your verification code will be direct messaged to you shortly.", ephemeral=True)
        emailStuff = emailAPI(email, apiHeaders, [], interaction.user.name, interaction.guild).check_email()
        if emailStuff[0]:
            await interaction.user.send(f"{interaction.user.name} here is your verification code(s).\n\n"+', '.join(emailStuff[1]))
        else:
            await interaction.user.send(f"{interaction.user.name} there was an error getting your verification code. Please try again in 30 seconds. Error: {emailStuff[1]}")
    else:
        await interaction.response.send_message(f"{interaction.user.name} that is not a valid email.", ephemeral=True)


ctypes.windll.kernel32.SetConsoleTitleW("Swine Codes")

config = Data().loadJson('config.json')

BILLGANG_API_KEY = config['billgangAPI']
SHOP_ID = config['billgangShopId']

apiHeaders = {
    'X-RapidAPI-Key': config['rapidAPI'],
    'X-RapidAPI-Host': 'privatix-temp-mail-v1.p.rapidapi.com'
}


while True:
    domains = get_domains()
    if domains is not None:
        bot.run(config['discordBotToken'])
        break
    else:
        log('Failed to get domains')
        sleep(3)



while True:
    sleep(60000)
