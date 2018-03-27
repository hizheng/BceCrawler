#!/usr/bin/python
import json
from datetime import datetime
import pytz
from base_adapter import BaseAdapter


class BceLoginAdapter(BaseAdapter):
    """docstring for BceLoginAdapter"""

    def __init__(self, **kwargs):
        super(BceLoginAdapter, self).__init__(kwargs['url'], kwargs['retry_count'])
        self.user_name = kwargs['user_name']
        self.password = kwargs['password']
        self.account_id = kwargs['account_id']

    def execute(self, session, data, headers):
        login_form_data = {
            'username': self.user_name,
            'password': self.password,
            'accountId': self.account_id,
            'redirect': 'http://console.bce.baidu.com'
        }
        response = super(BceLoginAdapter, self).execute(
            session, login_form_data, headers)
        csrf_token = None
        if response is not None:
            csrf_token = session.cookies.get_dict()['bce-user-info']
            csrf_token = csrf_token.strip('"')
        return csrf_token


class BceListBillsAdapter(BaseAdapter):
    """docstring for BceListBillsAdapter"""

    def __init__(self, url, retry_count):
        super(BceListBillsAdapter, self).__init__(url, retry_count)

    def execute(self, session, data, headers):
        bill_headers = {
            'Content-Type': 'application/json',
            'csrftoken': data['csrf_token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        }

        page_size = 10000
        if('page_size' in data):
            page_size = data['page_size']
        bill_list_data = {
            'productType': 'prepay',
            'ignoreNoPayment': False,
            'startTime': data['start_time'],
            'endTime': data['end_time'],
            'isPaid': True,
            'miniMode': '-1',
            'order': 'desc',
            'orderBy': 'startTime',
            'pageNo': 1,
            'pageSize': 10000,
            'serviceType': None,
            'paymentStatus': None
        }
        bill_list_data = json.dumps(bill_list_data)
        response = super(BceListBillsAdapter, self).execute(
            session, bill_list_data, bill_headers)
        return self.parse_response(data, response)

    def parse_response(self, data, response):
        result = {}
        if(not response):
            return result
        bill_list_response_json = json.loads(response.text)
        bill_list = bill_list_response_json['page']
        bill_list = bill_list['result']
        return bill_list


class BceBillDetailsAdapter(BaseAdapter):
    """docstring for BceBillDetailsAdapter"""

    def __init__(self, url, retry_count):
        super(BceBillDetailsAdapter, self).__init__(url, retry_count)

    def execute(self, session, data, headers):
        bill_headers = {
            'Content-Type': 'application/json',
            'csrftoken': data['csrf_token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
        }
        bill_details_data = {'uuid': data['bill_id']}
        bill_details_data = json.dumps(bill_details_data)
        response = super(BceBillDetailsAdapter, self).execute(
            session, bill_details_data, bill_headers)
        return self.parse_response(data, response)

    def parse_response(self, data, response):
        instance_payment_list = []
        if(not response):
            return instance_payment_list
        bill_details_response_json = json.loads(response.text)
        api_success = bill_details_response_json['success']
        if(api_success):
            result = bill_details_response_json['result']
            items = result['items']
            for item in items:
                service_type = item['serviceType']  # BCC ord CDS
                if(service_type == 'BBC'):
                    item_type = 'PM'
                    self.parse_bbc_item(
                        data, item, item_type, instance_payment_list)
                if(service_type == 'BCC'):
                    item_type = 'VM'
                    self.parse_bcc_cds_item(
                        data, item, item_type, instance_payment_list)
                if(service_type == 'CDS'):
                    item_type = 'DISK'
                    self.parse_bcc_cds_item(
                        data, item, item_type, instance_payment_list)
        return instance_payment_list

    def parse_bbc_item(self, data, item, item_type, instance_payment_list):
        pass

    def parse_bcc_cds_item(self, data, item, item_type, instance_payment_list):
        bill_time_local_str = data['bill_time']
        product_type = item['productType']  # prepay
        payment_type = ''
        if(product_type == 'prepay'):
            payment_type = 'PRE-PAY'
        else:
            payment_type = 'POST-PAY'
        payment_period = item['time']
        payment_sub_type = item['timeUnit']
        resource_short_ids = item['shortIds']
        for resource_short_id in resource_short_ids:
            instance_payment_hist = (
                resource_short_id,
                item_type,
                payment_type,
                payment_sub_type,
                bill_time_local_str,
                payment_period
            )
            instance_payment_list.append(instance_payment_hist)
