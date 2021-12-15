#! python3

from lcu_driver import Connector
import random 

NAME_FILE_PATH = "D:/Projects/StreamInvite/names.txt"
NUM_INVITES = 4

connector = Connector()

async def inviteSummoners(connection, ids):
    data = [{"toSummonerId" : str(id)} for id in ids]
    res = await connection.request('post', '/lol-lobby/v2/lobby/invitations', data=data)
    print(ids)
    if res.status == 404:
        print("Are you in a lobby?")
    elif res.status == 200:
        print(f"Invited {len(ids)} people.")
    else:
        print(res)
        print(await res.json())


async def getSummonerIds(connection, names):
    with open(NAME_FILE_PATH, "r") as nameFile:
        names = [line.strip() for line in nameFile]
        print(f"Interested people: {', '.join(names)}")
        res = await connection.request('post', '/lol-summoner/v2/summoners/names', data=names)
        summoners = await res.json()
        summonerIds = set()
        for summoner in summoners:
            summonerIds.add(summoner["summonerId"])
        print(f"Got {len(summonerIds)}/{len(names)} valid names.")
        return summonerIds


# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')

    # check if the user is already logged into his account
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    if summoner.status != 200:
        print('Please login into your account.')
    else:
        ids = await getSummonerIds(connection, None)
        toInvite = set(random.choices(list(ids), k=NUM_INVITES))
        await inviteSummoners(connection, toInvite)


# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    print('The client have been closed!')

# starts the connector
connector.start()
