import urllib.parse
import scrapy

class BwMainCollectorSpider(scrapy.Spider):
    name = "bw"
    base_url = 'https://www.bwcon.de'
    load_items_params = ''
    click_count = 0
    item_count = 0

    def __init__(self, min_items=10, **kwargs):
        self.min_items = int(min_items)
        super().__init__(**kwargs)

    def start_requests(self):
        """
        Starts the collection routine
        :return:
        """
        urls = [
            ('%s/aus-dem-netzwerk/meldungen' % self.base_url),
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.init_collection)

        pass

    def parse(self, response, **kwargs):
        """
        Callback function to parse
        :param response:
        :param kwargs:
        :return:
        """
        pass


    def init_collection(self, response):
        """
        First response collects the params for the post load method and collects the initial items found in page
        :param response:
        :return:
        """
        try:
            item_link_xpath = './/div[@id="resultList"]//div[@class="bwc-panel-content"]'

            self.load_items_params = response.xpath('.//form[@id="formLoadMore"]/@action').get()
            panels = response.xpath(item_link_xpath)

            for index, item in enumerate(panels):
                link = item.xpath('.//div[@class="visible-xs"]//h3/a[@class="eventheading"]/@href').get()
                self.item_count += 1
                yield response.follow(link, callback=self.parse_items)


        except Exception as e:
            exit(e)

    def collect_additional_items(self, response):
        """
        collects the additional post loaded data
        :param response:
        :return:
        """
        try:

            item_link_xpath = './/div[@class="bwc-panel-content"]'
            panels = response.xpath(item_link_xpath)
            self.item_count += len(panels)
            for index, item in enumerate(panels):
                link = item.xpath('.//h3//a[@class="eventheading"]/@href').get()
                self.item_count += 1
                yield response.follow(link, callback=self.parse_items)
        except Exception as e:
            exit(e)



    def parse_items(self, response):
        """
        Parses items and yields back item to scrapy engine
        :param response:
        :return:
        """
        publication = response.xpath('.//div[@class="bwc-panel-content"]//div[@class="bwc-meldungen-detail"]')

        item = {}
        for data in publication:
            item['url'] = response.url
            item['description'] = data.xpath('./div//p/text()').get()
            item['title'] = data.xpath('.//h3/text()').get().encode('utf-8').decode('utf-8').strip()
            item['publication_date'] = data.xpath('.//div[@class="date"]/text()').get().encode('utf-8').decode('utf-8').strip()
            item['body'] = ''.join(data.xpath('.//article/p/text()').getall()).encode('utf-8').decode('utf-8').strip()

            yield item

        if self.item_count < self.min_items:
            yield self.request_new_items()

    def request_new_items(self):
        """
        Sends out a request for new items to be loaded based on the current click count
        Copied request from webpage as cURL and converted it to python request
        :return:
        """

        self.click_count += 1

        hs = {
            # 'authority': 'www.bwcon.de',
            # 'accept': '*/*',
            # 'accept-language': 'en-DE,en;q=0.9,de-DE;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # Requests sorts cookies= alphabetically
            # 'cookie': '_ga=GA1.2.650818926.1650723570; _gid=GA1.2.1163422051.1650723570; cntb_set_1=,required,cookiebox,statistik,googleAnalytics,komfort,youtube,googleMaps,; _gat=1',
            'origin': 'https://www.bwcon.de',
            'referer': 'https://www.bwcon.de/aus-dem-netzwerk/meldungen',
            # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"Windows"',
            # 'sec-fetch-dest': 'empty',
            # 'sec-fetch-mode': 'cors',
            # 'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        frmdata = {
            'tx_bwconlist_bwcon[__referrer][@extension]': 'BwconList',
            'tx_bwconlist_bwcon[__referrer][@vendor]': 'SchommerMedia',
            'tx_bwconlist_bwcon[__referrer][@controller]': 'BwconList',
            'tx_bwconlist_bwcon[__referrer][@action]': 'list',
            'tx_bwconlist_bwcon[__referrer][arguments]': 'YTowOnt97325a919d3e793c2f79a9c8507b7bd31660a6094',
            'tx_bwconlist_bwcon[__referrer][@request]': 'a:4:{s:10:"@extension";s:9:"BwconList";s:11:"@controller";s:9:"BwconList";s:7:"@action";s:4:"list";s:7:"@vendor";s:13:"SchommerMedia";}e829a25e2da01682dce23ce2037409740fd8b2e9',
            'tx_bwconlist_bwcon[__trustedProperties]': 'a:2:{s:12:"clickCounter";i:1;s:9:"recordUid";i:1;}ce13c4552f4462265822d5ccb2cc929313165a94',
            'tx_bwconlist_bwcon[clickCounter]': str(self.click_count),
            'tx_bwconlist_bwcon[recordUid]': '268,200,160',
        }

        path = '%s?%s' % (hs['referer'] ,self.load_items_params)
        url = urllib.parse.urljoin(self.base_url, path)
        form_data = urllib.parse.urlencode(frmdata)

        return scrapy.Request(url, method='POST', body=form_data, headers=hs, callback=self.collect_additional_items)