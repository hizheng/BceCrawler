#!/usr/bin/python
import sys
import ConfigParser
from spiders.bce_spider import BceSpider
import logging
import logging.config
from datetime import datetime
import pytz


def run():
    config = ConfigParser.ConfigParser()
    conf_dir = sys.path[0] + "/config"
    life_cycle = 'dev'
    start_time_str = None
    end_time_str = None
    if(len(sys.argv) == 2):
        if(sys.argv[1] == 'help' or sys.argv[1] == '-h'):
            print(
                'Usage: python run.py [life_cycle] [start_time] [end_time]\nExample python run.py dev "2018-02-28 00:00:00" "2018-03-20 00:00:00')
            return
        life_cycle = sys.argv[1]
    elif(len(sys.argv) == 3):
        start_time_str = sys.argv[2]
    elif(len(sys.argv) == 4):
        start_time_str = sys.argv[2]
        end_time_str = sys.argv[3]
    elif(len(sys.argv) == 1):
        life_cycle = 'dev'
    else:
        print(
            'Usage: python run.py [life_cycle] [start_time] [end_time]\nExample python run.py dev "2018-02-28 00:00:00" "2018-03-20 00:00:00')
        return

    log_conf_file = conf_dir + '/' + life_cycle + '_logging.properties'
    logging.config.fileConfig(log_conf_file)
    logger = logging.getLogger('root')
    conf_file = conf_dir + "/" + life_cycle + "_conf.ini"
    config.read(conf_file)
    bce_login_url = config.get('bce-profile', 'bce_login_url')
    bce_list_bill_url = config.get('bce-profile', 'bce_list_bill_url')
    bce_bill_details_url = config.get('bce-profile', 'bce_bill_details_url')
    bce_user_id = config.get('bce-profile', 'bce_user_id')
    bce_password = config.get('bce-profile', 'bce_password')
    bce_account_id = config.get('bce-profile', 'bce_account_id')
    retry_count = config.get('bce-profile', 'retry_count')
    bce_conf = {}
    bce_conf['bce_login_url'] = bce_login_url
    bce_conf['bce_list_bill_url'] = bce_list_bill_url
    bce_conf['bce_bill_details_url'] = bce_bill_details_url
    bce_conf['user_name'] = bce_user_id
    bce_conf['password'] = bce_password
    bce_conf['account_id'] = bce_account_id
    bce_conf['retry_count'] = retry_count

    lingxu_db_host = config.get('lingxu-db', 'host')
    lingxu_db_port = config.get('lingxu-db', 'port')
    lingxu_db_user_name = config.get('lingxu-db', 'user_name')
    lingxu_db_password = config.get('lingxu-db', 'password')
    lingxu_db_name = config.get('lingxu-db', 'db_name')
    lingxu_db_conf = {}
    lingxu_db_conf['host'] = lingxu_db_host
    lingxu_db_conf['port'] = lingxu_db_port
    lingxu_db_conf['user_name'] = lingxu_db_user_name
    lingxu_db_conf['password'] = lingxu_db_password
    lingxu_db_conf['db_name'] = lingxu_db_name

    start_time = None
    end_time = None
    tz_local = pytz.timezone('Asia/Shanghai')
    GMT = pytz.timezone('GMT')
    if start_time_str:
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        start_time = start_time.replace(tzinfo=tz_local).astimezone(GMT)
    if end_time_str:
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = end_time.replace(tzinfo=tz_local).astimezone(GMT)

    result_file = open(sys.path[0] + '/result/result.csv', 'w')

    bce_spider = BceSpider(bce_conf, lingxu_db_conf, result_file)
    bce_spider.crawl(start_time, end_time)

    result_file.close()


if __name__ == '__main__':
    run()
