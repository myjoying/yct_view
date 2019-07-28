from flask import Flask, render_template, request,jsonify
from flask_script import Manager
from flask_bootstrap import Bootstrap
from DBdata.dataGet import *
import pandas as pd
from models import Stock
import stocks



app = Flask(__name__)

manager = Manager(app)
bootstrap = Bootstrap(app)

stocklist = Stock.objects()

def find_stock(ticker):
  try:
    stock = Stock.objects(symbol=ticker)[0]
    return stock
  except:
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock_market')
def stock_market():
    return render_template('stock_market.html')

@app.route('/stock_item/', methods=['GET', 'POST'])
def stock_item():
    data = pd.DataFrame()
    if request.method == 'GET':
        code = request.args.get('code', None)
        start_time = request.args.get('start_time', None)
        end_time = request.args.get('end_time', None)
        freq = request.args.get('freq', None)

        if code and start_time and end_time and freq:
            data = loadDataKLine(code, start_time, end_time, freq)

    a = jsonify(data.to_json(orient='columns'))
    return jsonify(data.to_json(orient='columns'))
    #return jsonify(data.to_json(orient='columns'))




@app.route('/stock/<ticker>')
def stock(ticker):
    return render_template('stock.html', ticker=ticker, quote=stock)

@app.route('/add/<ticker>')
def add(ticker):
  print('add XF')
  try:
    stock = Stock()
    stock['name'] = ticker
    stock['symbol'] = ticker
    try:
      stock['last_price'] = float(stocks.get_quote(ticker))
    except:
      print("lookup failed for %s" % ticker)
    print('presave')
    try:
      stock.save()
    except:
      print('stock failed to save')
    print("Created %s Successfully" % stock['name'])
    return render_template('add.html', ticker=ticker)
  except:
    return render_template('uhoh.html')

@app.route('/add/',methods=['GET'])
def badd():
    return render_template('badd.html')

@app.route('/add/',methods=['POST'])
def padd():
    print("Symbol Add")
    ticker = request.form['stock']
    add(ticker)
    return render_template('add.html', ticker=ticker)

#@app.route('/remove/<ticker>')
#def remove(ticker):
#    try:
#      #user.remove({'stock':ticker})
#      stock = Stock(symbol=ticker)[0].delete()
#      return render_template('remove.html', ticker=ticker)
#    except:
#      return render_template('uhoh.html')

@app.route('/remove/<id>')
def remove(id):
    try:
      #user.remove({'stock':ticker})
      stock = Stock(id=id)
      sym = stock['symbol']
      stock.delete()
      return render_template('remove.html', ticker=sym)
    except:
      return render_template('uhoh.html')



@app.route('/remove/')
def bremove():
    return render_template('bremove.html')

@app.route('/remove/',methods=['POST'])
def premove():
    ticker = request.form['stock']
    remove(ticker)
    return render_template('remove.html', ticker=ticker)

@app.route('/view/',methods=['POST'])
def search():
    ticker = request.form['search']
    #price = stocks.get_quote(ticker)
    stock_hist = stocks.get_historic(ticker,365)
    view_symbol(ticker)
    return render_template('view_stock.html', ticker=ticker, stock_hist=stock_hist)

@app.route('/view/<symbol>',methods=['GET'])
def view_symbol(symbol):
    stock_hist = stocks.get_historic(symbol,7)
    print(stock_hist)
    return render_template('view_stock.html', ticker=symbol,stock_hist=stock_hist)

@app.route('/profile/')
def profile():
    #stocklist = user.find()
    stocklist = Stock.objects()
    return render_template('profile.html', stocklist=stocklist, stocks=stocks)

if __name__ == '__main__':
#    manager.run()
    app.run(host="0.0.0.0",port=3001, debug=True)
