import datetime
import logging

from elasticsearch import Elasticsearch
from trello import TrelloClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./monitor.log')

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

client = TrelloClient(
    api_key='trelloapikey',
    api_secret='trelloapi_secretkey',
    token='trelloapi_token',
)


# select id from updated or created card
all_boards = client.list_boards()

#set period default 3days bofore today
since_day = (datetime.date.today() +
             datetime.timedelta(days=-3)).strftime("%Y-%m-%d")
before_day = datetime.date.today().strftime("%Y-%m-%d")


updated_list = all_boards[1].fetch_actions(
    action_filter='updateCard', since=since_day + 'T00:00:00.000Z', before=before_day + 'T00:00:00.000Z', action_limit=1000)
created_list = all_boards[1].fetch_actions(
    action_filter='createCard', since=since_day + 'T00:00:00.000Z', before=before_day + 'T00:00:00.000Z', action_limit=1000)

logger.info("updated_list length %s", len(updated_list))
logger.info("created_list length %s", len(created_list))

targetlist = []


for item in updated_list:
    targetlist.append(item['data']['card']['id'])
    

for item in created_list:
    targetlist.append(item['data']['card']['id'])
    

result_target = list(set(targetlist))

# travel each card by id and format dict


payload = {}
es = Elasticsearch("es_address:port")

for item in result_target:
    currentcard = client.get_card(item)
    payload['id'] = currentcard.id
    payload['shortUrl'] = currentcard.short_url
    payload['dateLastActivity'] = str(currentcard.dateLastActivity)[:-22]
    payload['desc'] = currentcard.description
    payload['name'] = currentcard.name

    # insert date to es
    result = es.index(index="tm_trello_card", doc_type="card",
                      id=payload['id'], body=payload)

    logger.info("updated es data %s", str(result))
