Скрипт позволяет обновлять IP адреса AWS ec2 инстансов за счет того, что если вы не приаттачили к инстансу выделенный Elastic IP, то stop инстанса и последующий start инстанса приведет к тому, что он получит другой IP-адрес.

Скрипт позволяет автоматизировать это через Cron. Скрипт получает список работающих инстансов по определенному тегу, по-умолчанию это тег Group, сортирует их по времени работы и те инстансы, которые уже работают дольше, чем `MIN_TTL` минут будут стопнуты и затем обратно запущены.

---
### Создание юзера
Для работы скрипта нужно создать пользователя, выбрав AWS credential type: Programmatic access и выдать ему доступ, достаточный чтобы запрашивать список инстансов, а также делать стоп и старт инстансов. 

`AmazonEC2FullAccess` точно хватит, но если у вас много лишнего времени - можете вручную наклацать более узкие права.

https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html

![6](https://user-images.githubusercontent.com/66549992/156938806-df8da283-7291-402c-9137-84b459e458cd.png)

![7](https://user-images.githubusercontent.com/66549992/156938881-171d6267-e9f5-416e-922b-ae4b732fd4ce.png)

---
### Создание инстансов

![1](https://user-images.githubusercontent.com/66549992/156938968-735d206c-c1d7-4a09-a806-0018e35aaa35.png)
![3](https://user-images.githubusercontent.com/66549992/156938972-27b225c0-1aae-43b5-b501-c0bf38bce36a.png)

**IMPORTANT - создание тега группы**
![10](https://user-images.githubusercontent.com/66549992/156938979-93da6f73-b4fe-4d7e-bc3c-0fe07e611d8c.png)


---

### Environment Variables:

`MIN_TTL` - сколько минимум отработает инстанс, прежде чем попадет под ротацию (default 30min)

`PERCENT_TO_ROTATE` - процент инстансов, которые будут стопаться за один запуск скрипта, чтобы никогда не стопать всю ферму (default 25%)

`AWS_EC2_ROTATE_REGION` - регион AWS, по которому будет работать скрипт, например, eu-north-1)

`KEY_ID` - получите когда создадите пользователя

`KEY_SECRET` - получите когда создадите пользователя

---

### Установка:

1) Устанавливаете `python3`, `python3-pip`

2) Устанавливаете зависимости через `pip3 install -r requirements.txt`

3) Создаете пользователя, как описано ниже, получаете `KEY_ID` и `KEY_SECRET`

4) Запускаете редактирование Cron через `crontab -e`, обязательно прописываете Енвы `AWS_EC2_ROTATE_REGION`, `KEY_ID` и `KEY_SECRET`, опционально прописываете `MIN_TTL` и `PERCENT_TO_ROTATE` если не устраивают значения по-умолчанию, ну и прописываете запуск самого скрипта в формате Крон, для примера, если вы проставили инстансам тег `Group` со значением `rotate_me_group`:

`*/30 * * * * /usr/bin/python3 /home/ozamodaz/aws-ec2-rotate/rotate.py rotate_me_group >> /tmp/aws-ec2-rotate.log 2>&1`
