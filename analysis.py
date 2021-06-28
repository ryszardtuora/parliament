import json
import numpy
import pandas

SEED = 42
numpy.random.seed(SEED)

# LOADING DATA
with open("deputies.json") as f:
  deputies = json.load(f)

with open("speeches.txt") as f:
  txt = f.read()
  
# CONSTRUCTING THE DF
speeches = txt.split("\n\n")
speech_objs = []
authors = []
for speech in speeches:
  author, text = speech.split("\n", 1)
  authors.append(author)
  try:
    party = deputies[author]
    obj = {"author": author, "party": party, "text": text}
    speech_objs.append(obj)
  except KeyError:
    # UNRECOGNIZED AUTHOR
    pass

df = pandas.DataFrame(speech_objs)

#ŁĄĆZYĆ PRZERWANE WYSTĄPIENIA
# CZASEM ZDARZA SIĘ TRASH df[100]
# BASIC STATISTICS
df.party.value_counts()
df.author.value_counts()
df["text"].apply(len).describe()


# COUNT VECTORIZATION
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer()
embedding = cv.fit_transform(df["text"])
dense = embedding.toarray()
freqs = dense.sum(axis=0)
feature_names = cv.get_feature_names()
fqdict = Counter({word:freq for word, freq in zip(feature_names, freqs)})


# TFIDF VECTORIZATION
from sklearn.feature_extraction.text import TfidfTransformer
model = TfidfTransformer(sublinear_tf=True)
tfidf = model.fit_transform(embedding) 
tfidf_dense = tfidf.toarray()
srt = tfidf_dense.argsort()
keywords = [[feature_names[i] for i in row[-5:]] for row in srt]

# VISUALIZATION
from matplotlib import pyplot as plt
from sklearn.decomposition import TruncatedSVD
dim_reductor = TruncatedSVD(n_components=2)
reduced = dim_reductor.fit_transform(tfidf)
transposed = reduced.T
party_list = list(set(df["party"]))
scatterplot = plt.scatter(*transposed, [party_list.index(p) for p in df["party"]])
plt.show()

# CLUSTERING
from sklearn.cluster import KMeans

parties = list(set([s["party"] for s in speech_objs]))
party_labels = [parties.index(s["party"]) for s in speech_objs]

km = KMeans(n_clusters = 5)
clusters = km.fit_predict(tfidf)

from sklearn.metrics import confusion_matrix
conf_matr = confusion_matrix(clusters, party_labels)

# wyszukiwarka Okapi BM25
# LSA
# stopwords z flisty
# lemmatize by morfeusz
# najblizsi sasiedzi po odleglosci
from sklearn.decomposition import TruncatedSVD

n_topics = 100
svd = TruncatedSVD(n_components=n_topics, random_state = SEED)
reduced = svd.fit_transform(tfidf)
explained_variance = svd.explained_variance_ratio_.sum()# czy na pewno ratio

srt = sorted([(reduced[i][0], i) for i in range(reduced.shape[0])], reverse=True)

#po klastrach counter albo sumować
#po partiach counter albo sumować
#klastry warto jednak narysować na wykresie
# dataframe
 df,group_by("party").sum()
ddf = DataFrame(array, columns=feature_names)

#PARTY KEYWORDS
top_labels = [f"top_{i}" for i in range(5,0,-1)]
ndf = pandas.concat([df, DataFrame(srt[:,-5:], columns=top_labels)], axis=1)
grouped = ndf.groupby("party")
aggregator = {
        f"top_{i}": Counter for i in range(5,0,-1)
}
aggred = grouped.agg(aggregator)
joined = {}
for party, entries in aggred.iterrows():
  joined[party] = Counter()
  for entry in entries:
    joined[party].update(entry)
  top_kws = [feature_names[i] for i, f in joined[party].most_common(5)]
  joined[party] = top_kws


