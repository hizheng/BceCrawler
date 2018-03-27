#!/usr/bin/python
import MySQLdb
import logging


class LingxuConnector(object):
    """docstring for LingxuConnector"""

    def __init__(self, **kwargs):
        super(LingxuConnector, self).__init__()
        self.host = kwargs['host']
        self.port = int(kwargs['port'])
        self.user_name = kwargs['user_name']
        self.password = kwargs['password']
        self.db_name = kwargs['db_name']
        self.logger = logging.getLogger('root')

    def get_connection(self):
        conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user_name,
                               passwd=self.password, db=self.db_name)
        return conn

    def insert_instance_payment_list(self, instance_payment_list, success_list):
        if(instance_payment_list):
            conn = self.get_connection()
            cursor = conn.cursor()
            for instance_payment in instance_payment_list:
                if(not instance_payment):
                    continue
                if(self.check_instance_payment(instance_payment)):
                    self.logger.info(
                        'Payment record already exists:' + 'instance_id=%s type=%s payment_time=%s' % (instance_payment[0], instance_payment[1], instance_payment[4]))
                    continue
                try:
                    sql = "insert into audit_instance_payment_hist(instance_id, type, payment_type, payment_sub_type, payment_time, payment_period, create_time, update_time) values('%s', '%s', '%s', '%s', '%s', '%f', NOW(), NOW())" % instance_payment
                    # sql = "insert into tmp_test(instance_id, type, payment_type, payment_sub_type, payment_time, payment_period, create_time, update_time) values('%s', '%s', '%s', '%s', '%s', '%f', NOW(), NOW())" % instance_payment
                    cursor.execute(sql)
                    conn.commit()
                    success_list.append(instance_payment)
                    self.logger.info(
                        'Success insert payment record:' + 'instance_id=%s type=%s payment_time=%s' % (instance_payment[0], instance_payment[1], instance_payment[4]))
                except Exception as e:
                    logging.exception(
                        'Exception occurs when insert payment record:' +
                        'instance_id=%s type=%s payment_time=%s'
                        % (instance_payment[0], instance_payment[1], instance_payment[4]))
                    conn.rollback()
            conn.close()

    def check_instance_payment(self, instance_payment):
        conn = self.get_connection()
        cursor = conn.cursor()
        instance_id = instance_payment[0]
        payment_time = instance_payment[4]
        instance_type = instance_payment[1]
        sql = "select count(*) from audit_instance_payment_hist where instance_id = '%s' and type = '%s' and payment_time = '%s'" % (
        # sql = "select count(*) from tmp_test where instance_id = '%s' and type = '%s' and payment_time = '%s'" % (
            instance_id, instance_type, payment_time)
        is_exist = True
        try:
            cursor.execute(sql)
            row = cursor.fetchone()
            if(row[0] == 0):
                is_exist = False
        except Exception as e:
            logging.exception(
                'Exception occurs when check instance payment:' + 'instance_id=%s type=%s payment_time=%s' % (instance_id, instance_type, payment_time))
        conn.close()
        return is_exist
