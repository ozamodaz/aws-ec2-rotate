import os
import sys
import boto3
from botocore.client import Config
from datetime import datetime
import pytz
import graypy
import logging
import json
from concurrent.futures import ThreadPoolExecutor

group = sys.argv[1].split(',')
logging.warning('will look for instances with tag "Group" and values: %s' % group)

state = 'running'
min_ttl = 30  # minutes
percent_to_rotate = 25  # max number of rotated instances per iteration

# graylog_host = 'graylog.yourdomain.com'
# graylog_port = 12399
# graylog_facility = 'aws-ec2-rotate'

session = boto3.Session(
    region_name='us-east-1',
    aws_access_key_id=os.environ['KEY_ID'],
    aws_secret_access_key=os.environ['KEY_SECRET'],
)
ec2 = session.resource('ec2', config=Config(max_pool_connections=50))


def rotate(instance):
    instance.stop()
    instance.wait_until_stopped()
    instance.start()
    instance.wait_until_running()
    logging.warning('ok: %s' % instance.id)


def instances_by_uptime(instances):
    by_uptime = []
    for instance in instances:
        now = datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        uptime = now - instance.launch_time
        by_uptime.append((instance, round(uptime.seconds/60)))
    by_uptime = sorted(by_uptime, key=lambda x: x[1], reverse=True)
    return by_uptime


def main():
    instances = ec2.instances.filter(Filters=[
            {'Name': 'tag:Group', 'Values': group},
            {'Name': 'instance-state-name', 'Values': [state]}])
    instances = list(instances.all())
    logging.warning(instances)

    by_uptime = instances_by_uptime(instances)
    count = int(len(instances)/100*percent_to_rotate)
    queue = [i for i in by_uptime if i[1] > min_ttl]
    msg = {
            'config': {
                       'min_ttl': min_ttl,
                       'percent_to_rotate': percent_to_rotate,
                       'instances': count
                      },
            'running_instances': len(instances),
            'max_crawler_uptime': by_uptime[0][1],
            'min_crawler_uptime': by_uptime[-1][1],
            'old_instances': len(queue)
           }
    if queue:
        msg['action'] = 'rotate %s instances' % len(queue[:count])
        logging.warning(json.dumps(msg, indent=4))
        with ThreadPoolExecutor(max_workers=30) as executor:
            for i in queue[:count]:
                instance = i[0]
                executor.submit(rotate, instance)
        instances = ec2.instances.filter(Filters=[
                {'Name': 'tag:Group', 'Values': group},
                {'Name': 'instance-state-name', 'Values': [state]}])
        instances = list(instances.all())
        by_uptime = instances_by_uptime(instances)
        if by_uptime[0][1] > (1.5 * min_ttl):
            res = {
                    'new_max_uptime': by_uptime[0][1],
                    'action': 'rotate_again'
                  }
            logging.warning(json.dumps(res, indent=4))
            main()
        else:
            res = {
                    'new_max_uptime': by_uptime[0][1],
                    'action': 'done'
                  }
            logging.warning(json.dumps(res, indent=4))
    else:
        msg['action'] = 'pass'
        logging.warning(json.dumps(msg, indent=4))


if __name__ == '__main__':
    # graylog_handler = graypy.GELFTcpHandler(graylog_host,
    #                                         graylog_port,
    #                                         facility=graylog_facility)
    logging.basicConfig(level=logging.WARNING)
    # logging.getLogger().addHandler(graylog_handler)
    main()
