import requests
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

base_req = requests.post(BASE_URL, data=param)

base_soup = BeautifulSoup(base_req.content, 'lxml')

reg_unit_codes = []
certificate_words = []

# Get all reg unit codes and certificate words for getting detail data
# TODO: Just get single page here, fetch all pages by urself =) (Feature)
for tr in base_soup.tbody.find_all('tr')[:1]:
    detail_info = tr[DETAIL_SYMBOL][9:-1].replace("'", '').split(',')
    reg_unit_codes.append(int(detail_info[0]))
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

    detail_req = requests.post(DETAIL_URL, data=param)
    detail_soup = BeautifulSoup(detail_req.content, 'lxml')

    target_divs = detail_soup.find_all('div', {
        'class': 'well pubDetailWellHalf center-block'})
    basic_response['債務人(買受人、受託人)名稱'] = target_divs[0].find('div', {'class': 'row'}).text[4:].strip()
    basic_response['抵押權人(出賣人、信託人)名稱'] = target_divs[1].find('div', {'class': 'row'}).text[4:].strip()
    responses.append(basic_response)


print(responses)
