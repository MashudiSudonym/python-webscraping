import requests
import json
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
query_param = {
    'search_terms': search_keyword,
    'geo_location_terms': location_keyword,
}
response = requests.get(url=f'{url}{additional_search_url}', params=query_param, headers=requests_header)
soup = BeautifulSoup(response.content, 'lxml')
result = soup.find('div', {'class': 'search-results organic'})
contents = result.find_all('a', {'class': 'business-name'})
data = []

# get all location url
for content in contents:
    location_url = content['href']

    # get detail each location
    new_url = f'{url}{location_url}'
    new_response = requests.get(new_url, requests_header)
    new_soup = BeautifulSoup(new_response.content, 'lxml')
    container = new_soup.find('main', {'class': 'container claimed'})
    main_info = container.find('article', {'class': 'business-card clearfix paid-listing'})
    categories = main_info.find('p', {'class': 'cats'}).find_all('a')
    section_rating = main_info.find('section', {'class': 'ratings'})
    time_info = main_info.find('div', {'class': 'time-info'})
    business_name = container.find('h1').text.strip()
    business_phone = main_info.find('p', {'class': 'phone'}).text.strip()
    business_address = main_info.find('h2', {'class': 'address'}).text.strip()
    list_business_categories = []

    # validation tag is not None
    if section_rating is not None:
        business_rating = section_rating.select_one('div')['class'][1]
    else:
        business_rating = None

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

    for category in categories:
        list_business_categories.append(category.text.strip())

    # check with print
    print(business_name)
    print(list_business_categories)
    print(new_url)
    print(business_phone)
    print(business_address)
    print(business_rating)
    print(business_status)
    print(business_open_schedule_today)
    print(business_open_schedule_tomorrow)

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
    }

    data.append(json_data)

# create json file
with open('data.json', 'w') as file:
    json.dump(data, file)
print('---------------->')
