import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

search_keyword = input('location name (example : restaurant) : ')
location_keyword = input('city (example : ohio) : ')
url = 'https://www.yellowpages.com'
additional_search_url = '/search?'
requests_header = {
    'accept': 'ext/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9 ',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en,id;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 '
                  'Safari/537.36 '
}
query_param = f'search_terms={search_keyword}&geo_location_terms={location_keyword}'

while True:
    response = requests.get(url=f'{url}{additional_search_url}{query_param}', headers=requests_header)
    soup = BeautifulSoup(response.content, 'lxml')
    result = soup.find('div', {'class': 'search-results organic'})
    contents = result.find_all('a', {'class': 'business-name'})
    data = []

    # get all location url
    for idx, content in enumerate(contents):
        location_url = content['href']

        # get detail each location
        new_url = f'{url}{location_url}'
        new_response = requests.get(new_url, requests_header)
        new_soup = BeautifulSoup(new_response.content, 'lxml')
        container = new_soup.find('main', {'id': 'bpp'})
        main_contact = container.find('div', {'class': 'contact'})
        main_article = container.find('article', {'id': 'main-article'})
        main_info = container.find('section', {'id': 'business-info'})
        categories = container.find('p', {'class': 'cats'}).find_all('a')
        section_rating = container.find('section', {'class': 'ratings'})
        time_info = container.find('div', {'class': 'time-info'})
        gallery = main_article.find('section', {'id': 'gallery'})
        photo_container = None if gallery is None else gallery.find('div', {
            'class': 'collage-item full'})
        photos = None if photo_container is None else photo_container.find_all('img')
        business_name = container.find('h1').text.strip()
        business_phone = main_contact.find('p', {'class': 'phone'}).text.strip()
        business_address = main_contact.find('h2', {'class': 'address'}).text.strip()
        business_rating = None if section_rating is None else section_rating.select_one('div')['class'][1]
        business_slogan = None if main_info.find('h2', {'class': 'slogan'}) is None else main_info.find('h2', {
            'class': 'slogan'}).text.strip()
        business_website = main_info.find('a')['href']
        business_general_info = None if main_info.find('dd', {'class': 'general-info'}) is None else main_info.find(
            'dd', {'class': 'general-info'}).text.strip()

        # empty variable
        list_business_photo_product = []
        list_business_categories = []

        # logic process for save result to empty variable
        # save categories
        for category in categories:
            list_business_categories.append(category.text.strip())

        # validation tag is not None
        # save photo url
        if photos is not None:
            for photo in photos:
                list_business_photo_product.append(photo['src'])
        else:
            list_business_photo_product.append(None)

        # save business schedule and status
        # validation tag is not None
        if time_info is not None:
            # validation out of range
            if len(time_info.find_all('div')) >= 3:
                business_status = time_info.find_all('div')[0].text.strip()
                business_open_schedule_today = time_info.find_all('div')[1].text.strip()
                business_open_schedule_tomorrow = time_info.find_all('div')[2].text.strip()
            else:
                business_status = time_info.find_all('div')[0].text.strip()
                business_open_schedule_today = time_info.find_all('div')[1].text.strip()
                business_open_schedule_tomorrow = None
        else:
            business_status = None
            business_open_schedule_today = None
            business_open_schedule_tomorrow = None

        # format data to json format
        json_data = {
            'business_name': business_name,
            'business_categories': list_business_categories,
            'business_url': new_url,
            'business_phone': business_phone,
            'business_address': business_address,
            'business_rating': business_rating,
            'business_status': business_status,
            'business_open_schedule_today': business_open_schedule_today,
            'business_open_schedule_tomorrow': business_open_schedule_tomorrow,
            'business_photo_product': list_business_photo_product,
            'business_slogan': business_slogan,
            'business_website': business_website,
            'business_general_info': business_general_info,
        }

        data.append(json_data)

        print(f'downloaded {idx + 1} of {len(contents)} at {datetime.now()}')

    # create json file
    with open('data.json', 'w') as file:
        json.dump(data, file)

    # get pagination
    pagination_container = soup.find('div', {'class': 'pagination'})
    pagination_next_page = pagination_container.find('a', {'class': 'next ajax-page'})['href']
    if pagination_next_page:
        query_param = pagination_next_page.replace(f'{additional_search_url}', '')
        print(query_param)
    else:
        break

print('---------------->')
