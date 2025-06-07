import pymongo
from info import DATABASE_URI, DATABASE_NAME
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]

async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    mycol = mydb[str(gfilters)]
    
    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }

    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except:
        logger.exception('Some error occurred in add_gfilter!', exc_info=True)

async def find_gfilter(gfilters, name):
    mycol = mydb[str(gfilters)]
    query = mycol.find({"text": name})
    
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            alert = file.get('alert', None)
            return reply_text, btn, alert, fileid
    except:
        return None, None, None, None

async def get_gfilters(gfilters):
    mycol = mydb[str(gfilters)]
    texts = []

    try:
        for file in mycol.find():
            texts.append(file['text'])
    except:
        pass

    return texts

async def delete_gfilter(message, text, gfilters):
    mycol = mydb[str(gfilters)]
    myquery = {'text': text}
    query = mycol.count_documents(myquery)

    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`' deleted. I'll not respond to that gfilter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that gfilter!", quote=True)

async def del_allg(message, gfilters):
    if str(gfilters) not in mydb.list_collection_names():
        await message.edit_text("Nothing to remove!")
        return

    try:
        mydb[str(gfilters)].drop()
        await message.edit_text("All gfilters have been removed!")
    except:
        await message.edit_text("Couldn't remove all gfilters!")

async def count_gfilters(gfilters):
    mycol = mydb[str(gfilters)]
    try:
        count = mycol.count_documents({})
        return False if count == 0 else count
    except:
        return False

async def gfilter_stats():
    collections = mydb.list_collection_names()
    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        try:
            count = mydb[collection].count_documents({})
            totalcount += count
        except:
            continue

    totalcollections = len(collections)
    return totalcollections, totalcount
