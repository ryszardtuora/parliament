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
for speech in speeches:
  author, text = speech.split("\n", 1)
  try:
    party = deputies[author]
    obj = {"author": author, "party": party, "text": text}
    speech_objs.append(obj)
  except KeyError:
    # UNRECOGNIZED AUTHOR
    pass

df = pandas.DataFrame(speech_objs)

#BASIC STATISTICS
df.party.value_counts()
df.author.value_counts()
df["text"].apply(len).describe()


# COUNT VECTORIZATION
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer()
embedding = cv.fit_transform(df["text"])
freqs = numpy.array(embedding.sum(axis=0)).squeeze()
feature_names = cv.get_feature_names()
fqdict = Counter({word:freq for word, freq in zip(feature_names, freqs)})


# TFIDF VECTORIZATION
from sklearn.feature_extraction.text import TfidfTransformer
model = TfidfTransformer(sublinear_tf=True)
tfidf = model.fit_transform(embedding) 
keywords = []
for row in tfidf:
    dense_row = row.toarray().squeeze()
    srt = dense_row.argsort()
    top_5 = [feature_names[i] for i in srt[-5:]]
    keywords.append(top_5)


# VISUALIZATION
from matplotlib import pyplot as plt
from matplotlib import cm
from sklearn.decomposition import TruncatedSVD
dim_reductor = TruncatedSVD(n_components=2)
reduced = pandas.DataFrame(dim_reductor.fit_transform(tfidf), columns=["X", "Y"])
ndf = pandas.concat([df, reduced], axis=1)
fig, ax = plt.subplots()
for i, party in enumerate(ndf["party"].unique()):
    party_entries = ndf[ndf["party"]==party]
    X, Y = party_entries.X, party_entries.Y
    ax.scatter(X, Y, c=cm.Accent(i), label=party)

ax.legend()
plt.show()

explained_variance = dim_reductor.explained_variance_ratio_

# CLUSTERING
from sklearn.cluster import KMeans
NUM_CLUSTERS = 10
km = KMeans(n_clusters = NUM_CLUSTERS)
clusters = km.fit_predict(tfidf)
cluster_frequency = Counter(clusters)

cluster_keywords = []
for cluster_index in range(NUM_CLUSTERS):
    indices = [i for i, c in enumerate(clusters) if c == cluster_index]
    cluster_counter = Counter()
    for i in indices:
        cluster_counter.update(keywords[i])
    top_10 = cluster_counter.most_common(10)
    cluster_keywords.append(top_10)



# PARTY KEYWORDS 
party_keywords = {} 
keywords_df = pandas.DataFrame(keywords, columns=[f"top_{i}" for i in range(5,0,-1)])
ndf = pandas.concat([df, keywords_df], axis=1)
for party in ndf["party"].unique():
    party_entries = ndf[ndf["party"]==party]
    aggregated = pandas.concat([party_entries.loc[:,f"top_{i}"] for i in range(5,0,-1)])
    top10 = aggregated.value_counts().iloc[:10]
    party_keywords[party] = top10

