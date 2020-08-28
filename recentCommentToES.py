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


# select comment info from created comment recent 5days
all_boards = client.list_boards()

# set period default 3days bofore today
since_day = (datetime.date.today() +
             datetime.timedelta(days=-5)).strftime("%Y-%m-%d")
before_day = datetime.date.today().strftime("%Y-%m-%d")


comment_list = all_boards[1].fetch_actions(
    action_filter='commentCard', since=since_day + 'T00:00:00.000Z', before=before_day + 'T00:00:00.000Z', action_limit=1000)

logger.info("comment_list length %s", len(comment_list))


payload = {}
es = Elasticsearch("es_address:port")

for item in comment_list:

    payload['id'] = item['id']
    payload['fullName'] = item['memberCreator']['fullName']
    payload['text'] = item['data']['text']
    payload['name'] = item['data']['card']['name']
    payload['shortLink'] = "https://trello.com/c/" + \
        item['data']['card']['shortLink'] + "/#comment-" + item['id']

    # # insert data to es
    result = es.index(index="tm_trello_comment",
                      doc_type="comment", id=payload['id'], body=payload)

    logger.info("updated es data %s", str(result))
