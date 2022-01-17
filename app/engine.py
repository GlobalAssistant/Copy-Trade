# from entity.OpenPosition import OpenPosition
import requests
import time
from datetime import datetime, timezone
from binance_f import RequestClient
from binance_f import SubscriptionClient
from binance_f.constant.test import *
from binance_f.model import *
from binance_f.exception.binanceapiexception import BinanceApiException
from binance_f.base.printobject import *
import json

from models import *
from start import app, db
  
# Opening JSON file
with open('config.json', 'r') as openfile:
	json_object = json.load(openfile)

keys = json_object["master"]
zignaly_keys = json_object["slave"]
binance_futures_leverage = json_object["leverage"]

def resolvePositionKey(order):
	return order

def sendPost(request, zignaly_keys):

	# r = requests.post(zignaly_keys["url"], 
	#			 data={
	#				 "pair": request.getPair(),
	#				 "signalId": request.getSignalId(),
	#				 "type": request.getOtype(),
	#				 "exchange": request.getExchange(),
	#				 "exchangeAccountType": request.getExchangeAccountType(),
	#				 "side": getSide(),
	#				 "orderType":  request.getOrderType(),
	#				 "leverage": "10",
	#				 "positionSizePercentage": getPositionSizePercentage(),
	#				 "key": request.getKey(),
	#				 "stopLossFollowsTakeProfit":True
	#			 }
	#	 )

	r = requests.post(zignaly_keys["url"], 
				data={
					"pair": request.getPair(),
					"signalId": "long1id",
					"type": "entry",
					"exchange": "zignaly",
					"exchangeAccountType": "futures",
					"side": "long",
					"orderType": "market",
					"leverage": "10",
					"positionSizePercentage": "1",
					"key": zignaly_keys["api_key"],
					"stopLossFollowsTakeProfit":True
				}
		)

def savePosition(order, position):
	position.updateDate = datetime.now(timezone.utc)
	position_json = json.dumps(position.__dict__)
	position_str = str(position_json)
	q = positionString(positionKey=resolvePositionKey(order), positionString=position_str)
	db.session.add(q)
	db.session.commit()

def createSignal(position, side, otype, positionSizePercentage):
	request = CreateSignalRequest()
	request.setLeverage(binance_futures_leverage)
	request.setSignalId(position.getSignalId())
	request.setPair(position.getPair())
	reduce1 = "World" in otype
	request.setOtype("update" if reduce1 else otype)
	request.setSide(side);
	request.setOrderType("MARKET")
	print("=========App works========12=====")

	if reduce1:
		request.setReduceOrderType("MARKET");
		request.setReduceAvailablePercentage(positionSizePercentage)
	elif positionSizePercentage != None:
		request.setPositionSizePercentage(positionSizePercentage)

	# zignalyService.createSignal(request)
	request.setKey(zignaly_keys["api_key"])
	request.setExchange("binance")
	request.setExchangeAccountType("futures")

	db.session.add(request)
	db.session.commit()
	print("=========App works========13=====")


	sendPost(request, zignaly_keys)

def resolvePositionKey(order):
	return order.positionSide + "-" + order.symbol;

def processOrderUpdate(order):
	if order.orderStatus != "FILLED":
		print("Order is not FILLED")
		return False

	positionKey = resolvePositionKey(order)
	# check eventTime to prevent double processing
	orderKey = "ORDER-" + positionKey
	orderKey_lastOrderEvent = LastOrderEvent.query.filter_by(orderKey=orderKey).first()
	print("=========lastOrderEvent========03=====", orderKey_lastOrderEvent, type(orderKey_lastOrderEvent))
	

	if orderKey_lastOrderEvent != None:
		lastOrderEvent = orderKey_lastOrderEvent.lastOrderEvent
		print("=========App works========003=====")
		print("=========lastOrderEvent========0003=====", lastOrderEvent, type(lastOrderEvent))
		# todo UPD: check if no concurrent issues for orders processing
		if lastOrderEvent >= order.orderTradeTime:
			print("This order already processed for position", positionKey)
			return False
		else:
			# Instead of Redis
			q = LastOrderEvent(orderKey=orderKey, lastorderevent=order.orderTradeTime)
			db.session.add(q)
			db.session.commit()
			print("=========App works========4=====")

	else:
		print("=========App works========04=====")
		q = LastOrderEvent(orderKey=orderKey, lastorderevent=order.orderTradeTime)
		db.session.add(q)
		db.session.commit()
	
	positionSizePercentage = None
	positionSize = round(order.origQty * order.avgPrice / binance_futures_leverage, 2)
	print("=========App works========5=====")

	# Check whether it is a new postion or exsited position
	positionKey_positionString = PositionString.query.filter_by(positionKey=positionKey).first()

	if positionKey_positionString == None:
		side = "LONG" if order.side == "BUY" else "SELL"
		# q = OpenPosition(signalId=unique_random_id, pair=order.symbol, side=side, quantity=order.origQty, maxQuantity=order.origQty, positionSize=positionSize, createDate=createDate, updateDate=datetime.now(timezone.utc), lastEventTime=datetime.now(timezone.utc))
		position = OpenPosition()
		position.signalId=unique_random_id
		position.pair=order.symbol
		position.quantity=order.origQty
		position.maxQuantity=order.origQty
		position.positionSize=positionSize
		position.createDate=createDate
		position.updateDate=datetime.now(timezone.utc)
		position.lastEventTime=datetime.now(timezone.utc)

		otype = "entry"
		positionSizePercentage = round(positionSize * 100 / walletBalance, 2)
		print("=========App works========6=====")

	else:
		positionString = positionKey_positionString.positionString
		position = OpenPosition()
		position_json = json.loads(positionString)
		if position_json["isCorrupted"] == True:
			print("Open position is corrupted, order unable to open new position")
			# todo: check zignaly order if still open
			return true

		if position_json["side"] != order.side:
			print("Stored position side does not match to order side")
			return True

		increase = order.side == "BUY" if position_json["side"] == "LONG" else order.side == "SELL"
		print("=========App works========7=====")

		if increase :
			# todo: if position was not reduced yet - recreate take profit
			position.position_json["quantity"] = position_json["quantity"] + order.origQty
			position.quantity = position.position_json["quantity"]
			if position.position_json["quantity"] > position_json["maxQuantity"]:
				position_json["maxQuantity"] = position_json["maxQuantity"] + order.origQty
				position.maxQuantity = position_json["maxQuantity"]

			otype = "update"
			positionSizePercentage = round(positionSize * 100 / walletBalance, 2)
			position_json["positionSize"] = position_json["positionSize"] + positionSize
			position.positionSize = position_json["positionSize"]
			print("=========App works========8=====")

		else:
			if position_json["quantity"] == position_json["maxQuantity"]:
				# todo: if first reduce order - create stop loss order
				print("Quantity equals with maxQuantity.")
			result = position_json["quantity"] - order.origQty
			if double(result) < 0:
				print(position_json["side"] + " position " + position_json["pair"] + " quantity is negative.")
				position_json["isCorrupted"] = True
				position.isCorrupted = position_json["isCorrupted"]

				position.signalId=position_json["signalId"]
				position.pair=position_json["pair"]
				position.quantity=position_json["quantity"]
				position.maxQuantity=position_json["maxQuantity"]
				position.positionSize=position_json["positionSize"]
				position.createDate=position_json["createDate"]
				position.updateDate=position_json["updateDate"]
				position.lastEventTime=position_json["lastEventTime"]

				savePosition(order, position)
				print("=========App works========9=====")

				return True
			else:
				print("=========App works========10=====")

				otype = "update_reduce"
				positionSizePercentage = round(positionSize * 100 / walletBalance, 2)
				position_json["positionSize"] = position_json["positionSize"] - positionSize
				position.positionSize = position_json["positionSize"]

			# walletBalance = walletBalance = order.realizedProfit()
			position_json["quantity"] = result
			position.quantity = position_json["quantity"]
			print("=========App works========11=====")

	createSignal(position, position.getSide(), order.type, positionSizePercentage)
	# update position with order
	if position.isClosed == True:
		print("Closing postion " + position.pair)
		db.session.add(position)
		db.session.commit()

		# Instead of Redis
		positionString.query.filter_by(positionKey=positionKey).delete()
		db.session.commit()
	else:
		savePosition(order, position)
	return True


def callback(data_type: 'SubscribeMessageType', event: 'any'):
	if data_type == SubscribeMessageType.RESPONSE:
		print("Event ID: ", event)
	elif  data_type == SubscribeMessageType.PAYLOAD:
		if(event.eventType == "ORDER_TRADE_UPDATE"):
			### store filled order to db
			print("Event Type: ", event.eventType, type(event.eventType))
			print("Event time: ", event.eventTime, type(event.eventTime))
			print("Transaction Time: ", event.transactionTime, type(event.transactionTime))
			print("Symbol: ", event.symbol, type(event.symbol))
			print("Client Order Id: ", event.clientOrderId, type(event.clientOrderId))
			print("Side: ", event.side, type(event.side))
			print("Order Type: ", event.type, type(event.type))
			print("Time in Force: ", event.timeInForce, type(event.timeInForce))
			print("Original Quantity: ", event.origQty, type(event.origQty))
			print("Position Side: ", event.positionSide, type(event.positionSide))
			print("Price: ", event.price, type(event.price))
			print("Average Price: ", event.avgPrice, type(event.avgPrice))
			print("Stop Price: ", event.stopPrice, type(event.stopPrice))
			print("Execution Type: ", event.executionType, type(event.executionType))
			print("Order Status: ", event.orderStatus, type(event.orderStatus))
			print("Order Id: ", event.orderId, type(event.orderId))
			print("Order Last Filled Quantity: ", event.lastFilledQty, type(event.lastFilledQty))
			print("Order Filled Accumulated Quantity: ", event.cumulativeFilledQty, type(event.cumulativeFilledQty))
			print("Last Filled Price: ", event.lastFilledPrice, type(event.lastFilledPrice))
			print("Commission Asset: ", event.commissionAsset, type(event.commissionAsset))
			print("Commissions: ", event.commissionAmount, type(event.commissionAmount))
			print("Order Trade Time: ", event.orderTradeTime, type(event.orderTradeTime))
			print("Trade Id: ", event.tradeID, type(event.tradeID))
			print("Bids Notional: ", event.bidsNotional, type(event.bidsNotional))
			print("Ask Notional: ", event.asksNotional, type(event.asksNotional))
			print("Is this trade the maker side?: ", event.isMarkerSide, type(event.isMarkerSide))
			print("Is this reduce only: ", event.isReduceOnly, type(event.isReduceOnly))
			print("stop price working type: ", event.workingType, type(event.workingType))
			print("Is this Close-All: ", event.isClosePosition, type(event.isClosePosition))
			print("=========App works========1=====")
			if not event.activationPrice is None:
				print("Activation Price for Trailing Stop: ", event.activationPrice)
			if not event.callbackRate is None:
				print("Callback Rate for Trailing Stop: ", event.callbackRate)

			order = OrderUpdate
			order = event
			if order != None:
				if processOrderUpdate(order):
					# store filled order to db
					print("=========App works========2=====")

					q = SignalOrder(orderId=event.orderId, symbol=event.symbol, side=event.side, positionSide=event.positionSide, origQty=int(event.origQty), avgPrice=int(event.avgPrice), orderTradeTime=event.orderTradeTime)
					db.session.add(q)
					db.session.commit()
					flash("Order added")

		elif(event.eventType == "listenKeyExpired"):
			print("Event: ", event.eventType)
			print("Event time: ", event.eventTime)
			print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
			print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
			print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
	else:
		print("Unknown Data:")
	print()

def error(e: 'BinanceApiException'):
	print(e.error_code + e.error_message)

def run():

	# Start user data stream
	request_client = RequestClient(api_key=keys["api_key"], secret_key=keys["secret_key"])
	listen_key = request_client.start_user_data_stream()

	accountInformation = request_client.get_account_information_v2()
	assets = accountInformation.assets
	for asset in assets:
		if asset.asset == "USDT":
			global walletBalance
			walletBalance = asset.walletBalance
			print("==walletBalance: ", asset.walletBalance)
			if walletBalance == 0:
				print("Wallet balance is 0")

	# Keep user data stream
	result = request_client.keep_user_data_stream()
	# print("Result: ", result)
	client = SubscriptionClient(api_key=keys["api_key"], secret_key=keys["secret_key"])
	client.subscribe_user_data_event(listen_key, callback, error)