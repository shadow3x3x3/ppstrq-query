import requests
import re
import pprint
import aiohttp
import asyncio

from bs4 import BeautifulSoup

BASE_URL = 'https://ppstrq.nat.gov.tw/pps/pubQuery/PropertyQuery/propertyQuery.do'
DETAIL_URL = 'https://ppstrq.nat.gov.tw/pps/pubQuery/PropertyQuery/propertyDetail.do'

DETAIL_SYMBOL = 'onclick'
debtor_name = '大同'

# TODO: Make all strings of key to Constant, just like URL (Performance)
param = {
  'method': 'query',
  'regUnitCode': '',
  'certificateAppNoWord': '',
  'currentPage': 2,
  'totalPage': '',
  'debtorType': 1,
  'creditorType': 1,
  'scrollTop': 0,
  'debtorTypeRadio': 1,
  'queryDebtorName': debtor_name,
  'queryDebtorNo': '',
  'creditorTypeRadio': 1,
  'queryCreditorName': '',
  'queryCreditorNo': '',
}

async def fetch_detail(session, code, word):
    basic_response = {
        '債務人(買受人、受託人)名稱': '',
        '契約啟始日期': '',
        '契約終止日期': '',
        '抵押權人(出賣人、信託人)名稱': '',
        '擔保債權金額': '',
        '案件類別': '',
        '標的物種類': '',
    }

    param['regUnitCode'] = code
    param['certificateAppNoWord'] = word

    detail_req = await session.get(DETAIL_URL, params=param)
    # print(await detail_req.text())

    detail_soup = BeautifulSoup(await detail_req.text(), 'lxml')

    main_div = detail_soup.find('div', {
        'id': 'formInput'
    })

    name_divs = main_div.find_all('div', {
        'class': 'well pubDetailWellHalf center-block'
    })
    basic_response['債務人(買受人、受託人)名稱'] = name_divs[0].find('div', {
        'class': 'row'
    }).text[4:].strip()

    basic_response['抵押權人(出賣人、信託人)名稱'] = name_divs[1].find('div', {
        'class': 'row'
    }).text[4:].strip()

    main_divs = main_div.find_all('div', {
        'class': 'well pubDetailWell center-block'
    })

    basic_info_div = main_divs[0]
    basic_response['案件類別'] = basic_info_div.find('div', {
        'class': 'row pubDetailRow'
    }).find_all('div', {
        'class': 'col-sm-3 pubDetailValue'
     })[1].text

    trade_info_div = main_divs[-1]
    trade_info_divs = trade_info_div.find_all('div', {
        'class': 'row pubDetailRow'
    })
    date_divs = trade_info_divs[0]
    dates = date_divs.find_all('div', {'class': 'col-sm-3 pubDetailValue'})
    # print(dates)
    basic_response['契約啟始日期'] = dates[0].text
    basic_response['契約終止日期'] = dates[1].text
    money = trade_info_divs[1].find_all('div', {
        'class': 'col-sm-3 pubDetailValue'
    })[1].text
    basic_response['擔保債權金額'] = re.sub('\r|\n|\t', '', money)

    kind = trade_info_divs[-1].find('div', {
        'class': 'col-sm-9 pubDetailValue'
    }).text
    basic_response['標的物種類'] = kind

    return basic_response

async def main(loop):
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Get all reg unit codes and certificate words for getting detail data
        # TODO: Just get single page here, fetch all pages by urself =) (Feature)
        base_req = requests.get(BASE_URL, param)
        base_soup = BeautifulSoup(base_req.content, 'lxml')

        for tr in base_soup.tbody.find_all('tr'):
            detail_info = tr[DETAIL_SYMBOL][9:-1].replace("'", '').split(',')
            tasks.append(loop.create_task(
                fetch_detail(session, detail_info[0], detail_info[1])
                )
            )

        finished, unfinished = await asyncio.wait(tasks)
        all_response = [r.result() for r in finished]
        pprint.pprint(all_response)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
