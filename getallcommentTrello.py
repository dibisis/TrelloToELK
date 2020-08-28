import json



def get_commentinfo_fromjson(filename):
    json_files = json.loads(open(filename, encoding='UTF8').read())

    result = {}
    tempresult = ''
    for item in json_files:
        tmpname = item['data']['card']['name']
        tmptext = item['data']['text']
        tmpfullname = item['memberCreator']['fullName']
        tmpid = item['id']

        tmpdict = {"id": tmpid, "name": tmpname,
                   "text": tmptext, "fullName": tmpfullname}

        print(json.dumps(tmpdict, ensure_ascii=False))

    # print(result)
    return result


get_commentinfo_fromjson('response_comment_11.json')

