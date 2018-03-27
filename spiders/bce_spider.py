#!/usr/bin/python

import requests
from adapters.bce_adapters import *
from dao.lingxu_connectors import *
import datetime
import logging
import sys


class BceSpider(object):
    """docstring for BceSpider"""

    def __init__(self, bce_conf, lingxu_db_conf, result_file):
        super(BceSpider, self).__init__()
        self.bce_conf = bce_conf
        self.lingxu_db_conf = lingxu_db_conf
        self.result_file = result_file
        self.logger = logging.getLogger('root')

    def crawl(self, start_time=None, end_time=None):
        session = requests.session()
        bce_login_adpater = BceLoginAdapter(
            url=self.bce_conf['bce_login_url'],
            user_name=self.bce_conf['user_name'],
            password=self.bce_conf['password'],
            account_id=self.bce_conf['account_id'],
            retry_count=self.bce_conf['retry_count']
        )
        csrf_token = bce_login_adpater.execute(session, None, None)
        if(not csrf_token):
            self.logger.error('can not get the correct csrf token')
            return

        bce_list_bill_adapter = BceListBillsAdapter(
            self.bce_conf['bce_list_bill_url'], self.bce_conf['retry_count'])
        if(not end_time):
            end_time = datetime.datetime.utcnow()
        if(not start_time):
            start_time = end_time - datetime.timedelta(days=7)
        end_time_str = datetime.datetime.strftime(
            end_time, '%Y-%m-%dT%H:%M:%SZ')
        start_time_str = datetime.datetime.strftime(
            start_time, '%Y-%m-%dT%H:%M:%SZ')
        self.logger.info('Crawl the bce payment info from %s to %s ' %
                         (start_time_str, end_time_str))
        list_bill_param = {}
        list_bill_param['csrf_token'] = csrf_token
        list_bill_param['start_time'] = start_time_str
        list_bill_param['end_time'] = end_time_str
        self.logger.info('Get the bill list from %s to %s' %
                         (start_time_str, end_time_str))
        list_bill_result = bce_list_bill_adapter.execute(
            session, list_bill_param, None)

        if(not list_bill_result):
            self.logger.info('No new bills from %s to %s' %
                             (start_time_str, end_time_str))
            return
        bill_time = list_bill_result['bill_time']
        bill_list = list_bill_result['bill_list']

        bce_bill_details_adapter = BceBillDetailsAdapter(
            self.bce_conf['bce_bill_details_url'], self.bce_conf['retry_count'])
        lingxu_connector = LingxuConnector(**self.lingxu_db_conf)
        for bill in bill_list:
            bill_id = bill['billingId']
            bill_details_param = {}
            bill_details_param['bill_id'] = bill_id
            bill_details_param['csrf_token'] = csrf_token
            bill_details_param['bill_time'] = bill_time
            instance_payment_list = bce_bill_details_adapter.execute(
                session, bill_details_param, None)
            success_list = self.persist_instance_payment_list(
                lingxu_connector, instance_payment_list)
            self.record_success_list(self.result_file, success_list)

    def persist_instance_payment_list(self, db_connector, instance_payment_list):
        if(not instance_payment_list):
            return
        db_connector.insert_instance_payment_list(instance_payment_list)

    def record_success_list(self, result_file, success_list):
        if(not success_list):
            return
        for instance_payment in success_list:
            result_file.write(','.join(map(str,instance_payment)) + '\n')
