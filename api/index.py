import os
from typing import Final
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
                      InputTextMessageContent, InlineQueryResultsButton, WebAppInfo)
from telegram import User
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler,
                          CallbackContext, InlineQueryHandler, ChosenInlineResultHandler)
from telegram.constants import ParseMode
import random
import datetime
from uuid import uuid4
import threading
import asyncio
import websockets
from multiprocessing import Process
import json

PORT = int(os.environ.get('PORT', 8443))

TOKEN = "8089314049:AAGfgf61zq0TnBuWhBGpVvIH-3LNIOIeg-A"

data = {'canvas':None, 'players':[]}


async def yes(update: Update, context: CallbackContext):
    print('1111111111111')
    group_id = update.message.chat.id
    await context.bot.sendMessage(chat_id=group_id, text='text')


async def ws_handler(websocket):
    async for message in websocket:
        message = eval(message)
        if message['tag'] == 'connected':
            data['players'].append(websocket)
            print(data['players'])
            await websocket.send(json.dumps({'tag':'start', 'data':data['canvas']}))
        elif message['tag'] == 'save':
            print('Save')
            data['canvas'] = message['data']
        elif message['tag'] == 'load':
            if data['canvas']:
                print('Load')                                      
                await websocket.send(json.dumps({'tag':'canvas', 'data':data['canvas']}))
            else:
                print('空')
        elif message['tag'] == 'drawn':
            data['canvas'] = message['data']
            for ws in data['players']:
                try:
                    print('drawn')
                    await ws.send(json.dumps({'tag':'canvas', 'data':data['canvas']}))
                except websockets.exceptions.ConnectionClosed:
                    print('Closed')
                    print(len(data['players']))
                    data['players'] = [p for p in data['players'] if p is not ws]
                    print(len(data['players']),data['players'])
        elif message['tag'] == 'clear':
            data['canvas'] = '{\"version\":\"6.6.6\",\"objects\":[]}'
            for ws in [p for p in data['players'] if p is not websocket]:
                try:
                    print('clear')
                    await ws.send(json.dumps({'tag':'canvas', 'data':'{\"version\":\"6.6.6\",\"objects\":[]}'}))
                except websockets.exceptions.ConnectionClosed:
                    print('Closed')
                    print(len(data['players']))
                    data['players'] = [p for p in data['players'] if p is not ws]
                    print(len(data['players']),data['players'])
            

def run_a():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('yes', yes))
    app.run_polling(poll_interval=0.0)


async def run_b():
    print('b')
    async with websockets.serve(ws_handler, '192.168.0.162', 8080):
        await asyncio.Future()


def bridge():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_b())


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    print('fff')
    # Commands
    #app.add_handler(CommandHandler('yes', yes))

    # InlineQuery
    #app.add_handler(InlineQueryHandler(inline_query))
    #app.add_handler(ChosenInlineResultHandler(chosen_inline))

    # Polls the bot
    print('Polling1...')
    #loopA = asyncio.new_event_loop()
    #loopB = asyncio.new_event_loop()
    threading.Thread(target=run_a).start()
    threading.Thread(target=bridge).start()
    print('Polling26798797...')
    
    
