# -*- coding: utf-8 -*-
from requests.packages.urllib3.exceptions import ReadTimeoutError

__author__ = 'pankajs'

from TwitterAPI import TwitterAPI
from TwitterAPI.TwitterError import TwitterRequestError, TwitterError
from TwitterAPI.TwitterError import TwitterConnectionError
from data_cleaner import *
import rethinkdb as rethinkdb
import re

cleaner = DataCleaner()
rethinkdb.connect("127.0.0.1", 28015).repl()

TRACK_TERM = '@HDFC_Bank, hdfc, HSBC,  @Barclays, #Barclays, ' \
             'AxisBank, suncorpbank, @nab, #nab, CreditSuisse, bankofengland, ' \
             '@Citi, #Citi, WellsFargo, DeutscheBank, kotakmahindrabk, @UBS, #UBS, bank_sc, StanChart, Westpac'

TERMS = ['wellsfargo', 'hsbc', 'hdfc', 'axis', 'barclays', 'suncorpbank', 'nab','westpac', 'citi','kotakmahindrabk', 'stanchart', 'sc', 'deutschebank', 'ubs', 'creditsuisse', 'bankofengland']

CONSUMER_KEY = 'mCMgMI0abcahLh7HQLY9dB2jq'
CONSUMER_SECRET = 'VsrMtE3YISaHOOwvMqpcE7mCYqK4ILBg9vMIRvUmLMlJsbe9Xk'
ACCESS_TOKEN_KEY = '1460773141-9BRBAXVONLitVqCyS51bGAChqOEi3ZgqYbQkEuT'
ACCESS_TOKEN_SECRET = 'MbZtO16etDHfstNDskAhT9nrvw5LbUzdQCOn1spO61tbx'

api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

request = api.request('statuses/filter', {'track': TRACK_TERM, 'language': 'en'})


http_pattern = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', re.DOTALL)


def authors(contributors):
    if contributors is None:
        return None
    return ','.join(map(lambda author: author['screen_name'], contributors))


def filter_term(text):
    text = text.lower()
    for term in TERMS:
        if term.lower() in text:
            return term.lower()
    return None

while True:
    try:
        iterator = request.get_iterator()
        for item in iterator:
            if 'text' in item:
                text = re.sub(http_pattern, '', item['text'].encode('utf-8').replace('\n', ' ')).encode('utf-8')
                print(text)
                rethinkdb.db("sentiment").table("messages")\
                    .insert({"text": text,
                             "coordinates": item['coordinates'],
                             "source": "twitter",
                             "author": authors(item['contributors']),
                             "tokens": cleaner.execute(text),
                             "filter_term": filter_term(text),
                             "created_on": rethinkdb.now()}).run()
            elif 'disconnect' in item:
                event = item['disconnect']
                if event['code'] in [2, 5, 6, 7]:
                    print('Disconnect message want by twitter')
                    raise Exception(event['reason'])
                else:
                    print("temporary disconnect retry request")
                    break
    except TwitterRequestError as e:
        if e.status_code < 500:
            # something needs to be fixed before re-connecting
            raise
        else:
            pass
    except TwitterConnectionError:
        pass
    except TwitterError:
        pass
    except UnicodeDecodeError:
        pass
    except ReadTimeoutError:
        pass
