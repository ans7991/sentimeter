import string
import re
from pyspark import SparkContext, SparkConf
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.feature import IDF
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import NaiveBayes
import rethinkdb as rdb
from nltk.corpus import stopwords

rdb.connect("10.12.20.23", 28015).repl()
feed = rdb.db("sentiment").table("messages").changes().run()

conf = SparkConf().setAppName("Sentimeter").setMaster("local")
sc = SparkContext(conf=conf)

stop = set(stopwords.words('english'))
stop = sc.broadcast(stop)

sentiments = {'1.0': "Positive", '0.0': "Negative"}

tweets = sc.textFile("/Users/anshulrastogi/Downloads/nlp/twits.txt")
tweets = tweets.map(lambda x: re.sub(r"(@|#)(\w+)", '', x))
tweets = tweets.map(lambda x: x.split(','))
plain_txt = tweets.map(lambda x: (x[0], x[1].encode('utf-8').translate(string.maketrans("", ""), string.punctuation)))
plain = plain_txt.map(lambda x: (x[0], x[1].translate(string.maketrans("", ""), '0123456789').lower()))
labels = plain.map(lambda x: float(x[0])).collect()
tokens = plain.map(lambda x: x[1].split())

hashingTF = HashingTF()
tf = hashingTF.transform(tokens)
tf.cache()
idf = IDF().fit(tf)
tfidf = idf.transform(tf)
labeledData = tfidf.zipWithIndex().map(lambda (x, y): LabeledPoint(labels[y], x))

model = NaiveBayes.train(labeledData)

for tweet in feed:
    tweet_text = tweet['new_val']['text']
    message = re.sub(r"(@|#)(\w+)", '', tweet_text)
    message = message.encode('utf-8').translate(string.maketrans("", ""), string.punctuation)
    message = message.translate(string.maketrans("", ""), '0123456789').lower()

    tf_new = hashingTF.transform(message.split(" "))
    tweet['new_val']['sentiment'] = model.predict(idf.transform(tf_new))
    rdb.db("sentiment").table("classified_messages").insert(tweet).run()
    print sentiments[str(model.predict(idf.transform(tf_new)))] + " - " + tweet_text