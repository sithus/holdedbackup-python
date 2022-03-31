#!/opt/homebrew/bin/python3
import asyncio
import json
import aiohttp
import motor.motor_asyncio
import sys

URL_root = "https://api.holded.com/api/invoicing/v1/"

URLs = [
    {"coleccion": "contacts", "url": URL_root + "contacts", "pagination": True, "pag_index": 1},
    {"coleccion": "invoices", "url": URL_root + "documents/invoice", "pagination": False, "pag_index": 1},
    {"coleccion": "purchases", "url": URL_root + "documents/purchase", "pagination": False, "pag_index": 1},
    {"coleccion": "estimates", "url": URL_root + "documents/estimate", "pagination": False, "pag_index": 1},
    {"coleccion": "products", "url": URL_root + "products", "pagination": False, "pag_index": 1},
    {"coleccion": "services", "url": URL_root + "services", "pagination": False, "pag_index": 1},
    {"coleccion": "waybills", "url": URL_root + "documents/waybill", "pagination": False, "pag_index": 1},
    {"coleccion": "payments", "url": URL_root+"payments", "pagination": True, "pag_index": 1},
    {"coleccion": "treasury", "url": URL_root + "treasury", "pagination": False, "pag_index": 1}
]


async def respuesta(url, session):
    headers = {
        "key": USER_KEY
    }
    params = {
        'starttmp': 978307200,
        'endtmp': 2540997503
    }
    # print(url)
    async with session.get(url, headers=headers, params=params) as response:
        elementos = json.loads(await response.text())
        return elementos


async def getURL(URL, session, db):
    if URL['pag_index'] == 1:
        borrados = await deleteDataMongo(URL['coleccion'], db)
        print("Elementos borrados localmente de la coleccion " +
              URL['coleccion']+": "+str(borrados))
    elementos = await respuesta(URL['url'], session)
    guardados = await saveDataMongo(URL['coleccion'], elementos, db)
    print(" Elementos almacenados localmente de la coleccion %(coleccion)s: %(cantidad)d" % ({"coleccion": URL['coleccion'], "cantidad": guardados}))
    if len(elementos) > 0:
        if (len(elementos) >= 500) and (URL['pagination'] == True):
            URL['pag_index'] = URL['pag_index'] + 1
            # Elimino el parámetro "page" anterior en la recursividad
            URL['url'] = URL['url'].split('?')[0]+"?page=" + str(URL['pag_index'])
            print('Solicitando página ' + str(URL['pag_index'])+' de la colección '+URL['coleccion'])
            await getURL(URL, session, db)


async def deleteDataMongo(coleccion, db):
    result = await db[coleccion].delete_many({})
    return result.deleted_count


async def saveDataMongo(coleccion, data, db):
    try:
        result = await db[coleccion].insert_many(data)
        return len(result.inserted_ids)
    except:
        print(' ERROR: al almacenar la colección: '+coleccion)
        return 0


async def conectaDbMongo(loop):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        'mongodb://127.0.0.1:27017')
    db = client[str(sys.argv[1])]
    return db


async def backup(loop):
    db = await conectaDbMongo(loop)
    print("BD conectada.")
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = [getURL(url, session, db) for url in URLs]
        await asyncio.gather(*tasks)
        print('BD cerrada.')

if len(sys.argv) == 3:
    USER_KEY = str(sys.argv[2])
    print("Backing up " + str(sys.argv[1]))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(backup(loop))
else:
    print(len(sys.argv))
    print ("No enough params. Use: backupMongo <mongodbname> <userkey>")
