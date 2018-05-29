import requests
import re
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


responses = []

base_req = requests.get(BASE_URL, param)

base_soup = BeautifulSoup(base_req.content, 'lxml')

reg_unit_codes = []
certificate_words = []

# Get all reg unit codes and certificate words for getting detail data
# TODO: Just get single page here, fetch all pages by urself =) (Feature)
for tr in base_soup.tbody.find_all('tr'):
    detail_info = tr[DETAIL_SYMBOL][9:-1].replace("'", '').split(',')
    reg_unit_codes.append(detail_info[0])
    certificate_words.append(detail_info[1])

# print(reg_unit_codes)
# print(certificate_words)

# Get detail data
for code, word in zip(reg_unit_codes, certificate_words):
    basic_response = {
        '債務人(買受人、受託人)名稱': '',
        '契約啟始日期': '',
        '契約終止日期': '',
        '抵押權人(出賣人、信託人)名稱': '',
        '擔保債權金額': '',
        '案件類別': '',
        '標的物種類': '',
    }

    print(word)
    param['regUnitCode'] = code
    param['certificateAppNoWord'] = word

    detail_req = requests.get(DETAIL_URL, param)
    detail_soup = BeautifulSoup(detail_req.content, 'lxml')
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

    responses.append(basic_response)


print(responses)
