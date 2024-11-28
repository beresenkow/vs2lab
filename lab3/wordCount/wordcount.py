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