import Splitter as sp

splitter = sp.Splitter()

with open("wordcount.txt") as txt:
    text = txt.read()

splitter.initWordCount(text)

splitter.start()
