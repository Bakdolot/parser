from seleniumwire import webdriver  # Import from seleniumwir
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from datetime import datetime, timedelta
import time
from random import randint
import requests
from bs4 import BeautifulSoup
import uuid
import os
import click

BASE_DIR = os.getcwd()


# Квартиры
SALE_APARTMENT = ['https://lalafo.kg/kyrgyzstan/kvartiry/prodazha-kvartir?page={}', 'apartment_sale.txt', 1, 2, 280]
DAILY_RENT_APARTMENT =['https://lalafo.kg/kyrgyzstan/kvartiry/arenda-kvartir/posutochnaya-arenda-kvartir?page={}', 'apartment_daily_rent.txt', 1, 1, 260]
LONG_TERM_RENT_APARTMENT = ['https://lalafo.kg/kyrgyzstan/kvartiry/arenda-kvartir/dolgosrochnaya-arenda-kvartir?page={}', 'apartment_long_term_rent.txt', 1, 1, 240]

# Дома
SALE_HOUSE = ['https://lalafo.kg/kyrgyzstan/doma-i-dachi/prodazha-domov?page={}', 'house_sale.txt', 2, 2, 270]
DAILY_RENT_HOUSE = ['https://lalafo.kg/kyrgyzstan/doma-i-dachi/arenda-domov/posutochno-arenda-domov?page={}', 'house_daily_rent.txt', 2, 1, 4]
LONG_TERM_RENT_HOUSE = ['https://lalafo.kg/kyrgyzstan/doma-i-dachi/arenda-domov/dolgosrochno-dom?page={}', 'house_long_term_rent.txt', 2, 1, 55]

# Гаражи
SALE_GARAGE = ['https://lalafo.kg/kyrgyzstan/garaji/prodayu-garazh?page={}', 'garage_sale.txt', 6, 2, 9]
RENT_GARAGE = ['https://lalafo.kg/kyrgyzstan/garaji/sdayu-garazh?page={}', 'garage_rent.txt', 6, 1, 1]

# Земельные участки
SALE_SECTION = ['https://lalafo.kg/kyrgyzstan/zemelnye-uchastki/prodazha-zemli?page={}', 'section_sale.txt', 4, 2, 190]
RENT_SECTION = ['https://lalafo.kg/kyrgyzstan/zemelnye-uchastki/arenda-zemli?page={}', 'section_rent.txt', 4, 1, 2]

DRIVER = f'{BASE_DIR}/chromedriver_linux64/chromedriver'


checked_urls_file_name = f'{BASE_DIR}/outputs/checked_urls.txt'

DRIVER = f'{BASE_DIR}/chromedriver_linux64/chromedriver'


checked_urls_file_name = f'{BASE_DIR}/outputs/checked_urls.txt'

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-extentions')

driver = webdriver.Chrome(DRIVER, options=options, desired_capabilities=capabilities)



headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjM3MzIwOTY1LCJqdGkiOiI4MzhlMDMxODdkZGE0ODhjODRiMDRjMWQyMGViMjEyMCIsInVzZXJfaWQiOjEsInBob25lIjoiOTk2NzcwMjY2ODA0In0.OLjdsOuxCJnRHBl_Y1xliHzgZfpY3A0zFbMH1lQb1Jk"}

def driver_scrolling(url, page):
    driver.get(url.format(randint(0, page)))
    flag = 0
    time.sleep(1.5)
    timer = datetime.now() + timedelta(seconds=35)
    while timer > datetime.now():
        time.sleep(1)
        flag += 35
        driver.execute_script(f'window.scrollBy({flag-50},{flag});', '')


def get_data():
    urls = []
    images = []
    for i in driver.get_log('performance'):
        log = json.loads(i['message'])['message']
        try:
            if 'api/search/v3/feed/' in log["params"]['response']['url']:
                value = json.loads(driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": log["params"]["requestId"]})['body'])
                if 'items' in value.keys():
                    for i in value['items']:
                        urls.append('https://lalafo.kg'+i['url'])
                        img = []
                        for j in i['images']:
                            img.append(j['original_url'])
                        images.append(img)
        except KeyError:
            continue
    return urls, images


def write_file(data):
    with open(f'{BASE_DIR}/outputs/lalafo_info.txt', 'w') as file:
        file.write(str(data))

    driver.close()
    driver.quit()



def get_elements(urls: list, images: list) -> list:
    elements = []
    checked_urls = None
    non_checked_urls = {}
    with open(checked_urls_file_name, 'r') as file:
        checked_urls = eval(file.read())
    for i in range(len(urls)):
        try:
            if checked_urls.get(urls[i]):
                continue
            non_checked_urls[urls[i]] = None
            driver.get(urls[i])
            driver.find_element_by_xpath('//*[@id="__next"]/div/div[1]/div/div[3]/div[1]/div[2]/div[2]/div[2]/button').click()
            # html = requests.get(urls[i])
            bs = BeautifulSoup(driver.page_source, 'lxml')
            title = bs.find('h1', class_='Heading secondary-small').text
            description = bs.find('div', class_='description__wrap').text
            phone = bs.find('div', 'phone-number__wrap').find('div', 'phone-wrap').text
            price = ''.join(bs.find('div', 'css-13sm4s4').find('span', 'heading').text[:-3].split()) or None
            currency = bs.find('div', 'css-13sm4s4').find('span', 'currency').text or None
            element = {
                'title': title,
                'description': description,
                'images': images[i],
                'phone': phone,
                'price': int(price),
                'currency': currency
            }
            attrs = bs.find('ul', class_='details-page__params css-1a02eld').find_all('li')
            for i in range(len(attrs)):
                element.update({attrs[i].find('p').text.strip(':'): [i.text for i in attrs[i].find_all('a')] or attrs[i].find_all('p')[1].text})
            elements.append(element)
        except:
            continue
    if non_checked_urls:
        with open(checked_urls_file_name, 'w') as file:
            checked_urls.update(non_checked_urls)
            file.write(str(checked_urls))
    return elements


def get_fields(file_name):
    file = []
    with open(file_name, 'r') as f:
        data = f.read().split('\n\n')
        file.append(eval(data[0]))
        file.append(eval(data[1]))
    return file


def temporary_data(file_name):
    file = None
    with open(file_name, 'r') as f:
        file = eval(f.read())
    return file


def response_data(data, fields, base_fields, sell_type, property_type):

    fields_with_values = fields[1]
    fields = fields[0]
    for element in data:
        try:
            temporary = {
                'description': element['description'],
                'region': 5,
            }
            for fil in list(fields_with_values):
                if fil in list(element):
                    try:
                        if fil == 'Защита территории':
                            temporary[fields_with_values[fil]] = [fields[fil][val] for val in element[fil]]
                        else:
                            for val in element[fil]:
                                temporary[fields_with_values[fil]] = fields[fil][val]
                    except:
                        continue
            for fil in list(base_fields):
                if fil in list(element):
                    temporary[base_fields[fil]] = float(element[fil][0])
            if element.get('images'):
                imgs = [requests.get(image).content for image in element['images']]
                images = []
                for image in imgs:
                    images.append(('images', (str(uuid.uuid4())+'.jpeg', image, 'image/jpeg')))
                files = {
                    'images': images
                }
            if temporary.get('max_floor'):
                temporary['max_floor'] = int(temporary['max_floor'])
            if not temporary.get('district'):
                temporary['district'] = 7
            temporary['city'] = 1
            temporary['add_from'] = 1
            temporary['currency'] = 2 if element['currency'] == 'USD' else 1
            temporary['price'] = element['price']
            if not 'square' in list(temporary):
                temporary['square'] = 0
            temporary['sell_type'] = sell_type
            temporary['user'] = 1
            temporary['price_for'] = 1
            temporary['phone_numbers'] = str([int(element['phone'][2:-2])])
            temporary['property_type'] = property_type
            tem = temporary.pop('build_year') if temporary.get('build_year') else None
            tem


            response = requests.post('https://api.domket.kg/ad/create/', headers=headers, data=temporary, files=images)
            print(response.json())
            time.sleep(0.3)

        except Exception as e:
                print(e)
    return response   



@click.command()
@click.argument('category')
def main(category):   
    driver_scrolling(eval(category)[0], eval(category)[4])
    urls, images = get_data()
    print(f'urls len >> {len(urls)}')
    data = get_elements(urls, images)
    write_file(data)
    data = temporary_data(f'{BASE_DIR}/outputs/lalafo_info.txt')
    fields = get_fields(f'{BASE_DIR}/outputs/category/{eval(category)[1]}')
    base_fields = temporary_data(f'{BASE_DIR}/outputs/base_fields.txt')
    payload = response_data(data, fields, base_fields, eval(category)[3], eval(category)[2])
    print(len(data))
    # print(payload)
    


if __name__ == '__main__':
    try:
        main()

    except Exception as e:
        print(e)
