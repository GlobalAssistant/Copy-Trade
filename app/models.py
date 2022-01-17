from start import db

class SignalOrder(db.Model):
	__tablename__ = 'signal_order'
	id = db.Column(db.Integer, primary_key = True)
	orderId = db.Column(db.String(255))
	symbol = db.Column(db.String(255))
	side = db.Column(db.String(255))
	positionSide = db.Column(db.String(255))
	origQty = db.Column(db.Integer)
	avgPrice = db.Column(db.Integer)
	orderTradeTime = db.Column(db.String(255))

	# def __init__(self, orderId, symbol, side, positionSide, origQty, avgPrice, orderTradeTime):
	#	 self.orderId = orderId
	#	 self.symbol = symbol
	#	 self.side = side
	#	 self.positionSide = positionSide
	#	 self.origQty = origQty
	#	 self.avgPrice = avgPrice
	#	 self.orderTradeTime = orderTradeTime

class OpenPosition(db.Model):
	__tablename__ = 'position'
	id = db.Column(db.Integer, primary_key = True)
	signalId = db.Column(db.String(255))
	pair = db.Column(db.String(255))
	side = db.Column(db.String(255))
	quantity = db.Column(db.Integer)
	maxQuantity = db.Column(db.Integer)
	positionSize = db.Column(db.Integer)
	createDate = db.Column(db.DateTime)
	updateDate = db.Column(db.DateTime)
	lastEventTime = db.Column(db.String(255))
	isClosed = db.Column(db.Boolean, default=False)
	isCorrupted = db.Column(db.Boolean, default=False)

	# def __init__(self, orderId, symbol, side, positionSide, origQty, avgPrice, orderTradeTime):
	#	 self.orderId = orderId
	#	 self.symbol = symbol
	#	 self.side = side
	#	 self.positionSide = positionSide
	#	 self.origQty = origQty
	#	 self.avgPrice = avgPrice
	#	 self.orderTradeTime = orderTradeTime

class LastOrderEvent(db.Model):
	__tablename__ = 'last_order_event'
	id = db.Column(db.Integer, primary_key = True)
	orderKey = db.Column(db.String(255))
	lastorderevent = db.Column(db.Integer)

	# def __init__(self, orderKey, lastorderevent):
	#	 self.orderKey = orderKey
	#	 self.lastorderevent = lastorderevent

class positionString(db.Model):
	__tablename__ = 'positionString'
	id = db.Column(db.Integer, primary_key = True)
	positionKey = db.Column(db.String(255))
	positionString = db.Column(db.Text)

	# def __init__(self, positionKey, positionString):
	#	 self.positionKey = positionKey
	#	 self.positionString = positionString

class CreateSignalRequest:
	__tablename__ = 'CreateSignalRequest'
	id = db.Column(db.Integer, primary_key = True)
	key = db.Column(db.String(255))
	exchange = db.Column(db.String(255))
	exchangeAccountType = db.Column(db.String(255))
	leverage = db.Column(db.Integer)
	signalId = db.Column(db.String(255))
	pair = db.Column(db.String(255))
	otype = db.Column(db.String(255))
	side = db.Column(db.String(255))
	orderType = db.Column(db.String(255))
	positionSizePercentage = db.Column(db.Integer)
	reduceOrderType = db.Column(db.String(255))
	reduceAvailablePercentage = db.Column(db.Integer)
	limitPrice = db.Column(db.String(255))


	# def __init__(self):
	#	 # default/properties values
	#	 self.key = ''
	#	 self.exchange = ''
	#	 self.exchangeAccountType = ''
	#	 self.leverage = 0
	#	 # order values
	#	 self.signalId = ''
	#	 self.pair = ''
	#	 self.type = ''
	#	 self.side = ''
	#	 self.orderType = ''
	#	 self.positionSizePercentage = 0

	#	 self.reduceOrderType = ''
	#	 self.reduceAvailablePercentage = 0
	#	 self.limitPrice = ''
		
