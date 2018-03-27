#/bin/bash

env='dev'
if [[ ! -z $1 ]];then
    env=$1
fi

to=
smtpserver=
smtpport=
user=
password=

cd /opt/cronjobs/$env/bce-crawler && python run.py $env && echo "Successfully execute the BCE crawler" | mailx -s "BCE crawler result" -a './result/result.csv' -r "ma-noreply@qiyi.com" -S smtp="smtp://${smtpserver}:${smtpport}" -S smtp-auth=login -S smtp-auth-user=$user -S smtp-auth-password=$password $to
