import requests
from bs4 import BeautifulSoup

URL = 'https://ppstrq.nat.gov.tw/pps/pubQuery/PropertyQuery/propertyQuery.do'
debtor_name = '統一'

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
  'struts.token.name': 'struts.token',
  'struts.token': '9BJIP8NRCRJMTJT7O6ZDALD2IZZPR5TB',
  'monthCount': 546800,
  'totalCount': 34857941
}

req = requests.post(URL, data=param)

soup = BeautifulSoup(req.content)
print(soup.prettify())