Скрипт позволяет обновлять IP адреса AWS ec2 инстансов за счет того, что если вы не приаттачили к инстансу выделенный Elastic IP, то stop инстанса и последующий start инстанса приведет к тому, что он получит другой IP-адрес.

Скрипт позволяет автоматизировать это через Cron. Скрипт получает список работающих инстансов по определенному тегу, по-умолчанию это тег Group, сортирует их по времени работы и те инстансы, которые уже работают дольше, чем MIN_TTL минут будут стопнуты и затем обратно запущены.

Для работы скрипта нужно создать пользователя, выбрав AWS credential type: Programmatic access и выдать ему доступ, достаточный чтобы запрашивать список инстансов, а также делать стоп и старт инстансов. `AmazonEC2FullAccess` точно хватит, но если у вас много лишнего времени - можете вручную наклацать более узкие права.

Environment Variables:

`MIN_TTL` - сколько минимум отработает инстанс, прежде чем попадет под ротацию (default 30min)

`PERCENT_TO_ROTATE` - процент инстансов, которые будут стопаться за один запуск скрипта, чтобы никогда не стопать всю ферму (default 25%)

`AWS_EC2_ROTATE_REGION` - регион AWS, по которому будет работать скрипт, например, eu-north-1)

`KEY_ID` - получите когда создадите пользователя

`KEY_SECRET` - получите когда создадите пользователя

Установка:

1) Устанавливаете `python3`, `python3-pip`

2) Устанавливаете зависимости через `pip3 install -r requirements.txt`

3) Создаете пользователя, как описано ниже, получаете `KEY_ID` и `KEY_SECRET`

4) Запускаете редактирование Cron через `crontab -e`, обязательно прописываете Енвы `AWS_EC2_ROTATE_REGION`, `KEY_ID` и `KEY_SECRET`, опционально прописываете `MIN_TTL` и `PERCENT_TO_ROTATE` если не устраивают значения по-умолчанию, ну и прописываете запуск самого скрипта в формате Крон, для примера, если вы проставили инстансам тег `Group` со значением `rotate_me`:

`*/30 * * * * /usr/bin/python3 /home/ozamodaz/aws-ec2-rotate/rotate.py rotate_me >> /tmp/aws-ec2-rotate.log 2>&1`
