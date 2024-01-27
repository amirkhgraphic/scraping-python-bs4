from bs4 import BeautifulSoup, Tag
from models import db, Estate
from config import *
import argparse
import requests
import logging


# Create and Config logger
logging.basicConfig(
    format='%(levelname)s - (%(asctime)s) - %(message)s - (Line: %(lineno)d) - [%(filename)s]',
    datefmt='%H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, database, ad_type, city, min_room=None, max_room=None, min_price=None, max_price=None):
        self.__page = 1
        self.__num = 1
        self.city = city
        self.type = ad_type
        self.db = database
        self._break = False
        self.result = list()
        self.__min_param, self.__max_param = price_params[ad_type]
        self.url = BASE_URL.format(
            type=ad_type, city=city, min_rooms=(min_room or ''), max_rooms=(max_room or ''),
            min_price_param=self.__min_param, min_price=(min_price or ''),
            max_price_param=self.__max_param, max_price=(max_price or '')
        )

    def crawl(self):
        while True:
            self.__scrape_page(self.__page)
            if self._break:
                break
            self.__page += 1

        logger.info('Scraping done!')

    def __scrape_page(self, page=1):
        response = requests.get(self.url + f'&ep={page}')

        if response.status_code == 200:
            logger.info(f'Scraping page {"-"*10} {self.__page}')
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.select('.HgListingCard_card_QGuXn')

            if len(items) != 20:
                self._break = True

            if not items:
                return

            for item in items:
                self.__scrape_detail(item)

        elif response.status_code == 403:
            print("You've been BLOCKED !!!")
            self._break = True

        else:
            self._break = True

    def __scrape_detail(self, element: Tag):
        logger.info(f'scraping data {self.__num}')
        self.__num += 1

        currency, price, *_ = (element.select_one('.HgListingCard_price_JoPAs')
                               .text.strip().split())
        price = int("".join(price[:-2].split(',')))

        room_space = [txt.text.strip() for txt in element.select(
            '.HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq span strong'
        )]
        rooms, space = None, None

        for item in room_space:
            if item.endswith("m²"):
                space = int(item[:-2])
            else:
                rooms = item

        address = element.select_one('.HgListingCard_address_JGiFv address').string

        Estate.create(type=self.type, city=self.city, price=price, currency=currency,
                      rooms=rooms, space=space, address=address).save()


if __name__ == '__main__':
    logger.info('Configuring argument parser...')
    parser = argparse.ArgumentParser(
        prog='real-estate-crawler',
        description='A web crawler for extracting real estate\'s data about the given city'
    )
    parser.add_argument('type', type=str, help='type of the advertisement', choices=['buy', 'rent'])
    parser.add_argument('city', type=str, help='name of the city')
    parser.add_argument('-r', '--min-rooms', type=int, help='minimum number of the rooms')
    parser.add_argument('-R', '--max-rooms', type=int, help='maximum number of the rooms')
    parser.add_argument('-p', '--min-price', type=int, help='minimum price')
    parser.add_argument('-P', '--max-price', type=int, help='maximum price')

    logger.info('parsing arguments...')
    args = parser.parse_args()

    logger.info('Creating table: "estate"')
    db.create_tables([Estate])

    crawler = Crawler(db, args.type, args.city, args.min_rooms, args.max_rooms, args.min_price, args.max_price)
    crawler.crawl()

    logger.info('Closing connection...')
    db.close()

    logger.info('Done!')
