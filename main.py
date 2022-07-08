
import requests
import lxml
import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime


headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/103.0.0.0 Safari/537.36'
}

result_data = list()


async def scraping(session, url):
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        cards = soup.find_all('div', class_='product-cell-container col-xs-12 col-sm-12 col-md-8 col-lg-6')

        for card in cards:
            title = card.find('div', {'class': 'product-title', 'itemprop': 'name'}).text.strip()

            try:
                image_src = card.find('span', class_='product-image').img['src']
            except:
                image_src = card.find('span', class_='product-image').div['data-image-retina-src']

            try:
                price = card.find('div', class_='product-price-top').find('span', class_='price').text.strip()
            except:
                price = card.find('div', class_='product-price-top').find('span', class_='price discount-red').text.strip()

            number = card.find('span', class_='product-image')['data-part-number']

            try:
                out_of_stock = card.find('div', class_='text-danger-lighter out-of-stock text-nowrap').text
                availability = '-'
            except:
                availability = '+'

            result_data.append({
                'title': title,
                'image_src': image_src,
                'price': price,
                'number': number,
                'availability': availability
            })

        print(f'{url} parsed')



async def get_tasks(count_of_pages, url):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page in range(1, count_of_pages+1):
            tasks.append(asyncio.create_task(scraping(session, url+f'?p={page}')))

        result = await asyncio.gather(*tasks)


def main():
    category = input('Enter category: ')
    base_url = 'https://ua.iherb.com/c/'

    pagination_html = requests.get(url=base_url+category, headers=headers)
    soup = BeautifulSoup(pagination_html.text, 'lxml')
    count_of_pages = int(soup.find_all('a', class_='pagination-link')[-1].text.strip())

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_tasks(count_of_pages, base_url+category))

    with open(f'result.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            ('Title', 'Image', 'Price', 'Number', 'Availability')
        )

    with open(f'result.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for elem in result_data:
            writer.writerow(
                (
                    elem['title'],
                    elem['image_src'],
                    elem['price'],
                    elem['number'],
                    elem['availability']
                )
            )


if __name__ == '__main__':
    main()
