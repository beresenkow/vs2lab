import Splitter as sp
import Mapper as mp
import Reducer as rd

import constPipe as const

splitter = sp.Splitter()

mappers = {
    mp.Mapper(),
    mp.Mapper(),
    mp.Mapper()
}

reducers = {
    rd.Reducer(const.PORT1),
    rd.Reducer(const.PORT2)
}

with open("wordcount.txt") as txt:
    text = txt.read()

splitter.initWordCount(text)

splitter.start()

for mapper in mappers:
    mapper.start()

for reducer in reducers:
    reducer.start()
