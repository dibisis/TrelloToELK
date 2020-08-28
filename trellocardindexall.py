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
currentboard= all_boards[1]

all_card_list=currentboard.all_cards()


payload = {}
es = Elasticsearch("es_address:port")

for item in all_card_list:
    payload['id'] = item.id
    payload['directlink'] = item.short_url
    payload['dateLastActivity'] = str(item.dateLastActivity)[:-22]
    payload['description'] = item.description
    payload['title'] = item.name

    # insert date to es
    result = es.index(index="tm_trello_card_new", doc_type="card",
                      id=payload['id'], body=payload)

    logger.info("updated es data %s", str(result))
