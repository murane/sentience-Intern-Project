import urllib
import datetime
from sqlalchemy import *
from sqlalchemy.sql import text,select
from bs4 import BeautifulSoup
from flask import Flask,render_template,request		
							#import Flask and rendering module
app = Flask(__name__)		#take file's name and make Flask app
@app.route("/")		#default route
def main():
	
	return render_template('home.html')

@app.route("/inputAction",methods=['POST','GET'])	#input stockItemCode
def inputAction():
	if request.form['stockItemCode']=="":					#if stockItemCode is empty
		msg="Please enter profer stockItemCode"				#give a message under the text form
		return render_template('home.html',result=msg)
	else:
		url="http://google.com/finance?q="+request.form['stockItemCode']	#use orl of google finance and query data
		html=urllib.urlopen(url)													
		soup=BeautifulSoup(html,'html.parser')								#make soup using html.parser
		
		code=request.form['stockItemCode']

		parse=soup.findAll('span',{'class':'pr'})
		price=parse[0].find('span').text
		price=str(price).replace(',','')
		
		parse=soup.findAll('div',{'class':'id-price-change'})
		price_change=parse[0].find('span').contents[0].text
		price_change=str(price_change).replace(',','')

		#time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")			#parse price,change,itemname
																			#and make timestamp
		parsed ="price of "+code+" is "+price+" price change is "+price_change	#and make string

		engine = create_engine('mysql://root:1234@localhost/test')			#to store data create sqlalchemy engine
		conn= engine.connect()
		conn.execute(text(
						'''CREATE TABLE IF NOT EXISTS stock(
						stockItemCode VARCHAR(30),
						price VARCHAR(30),
						price_change VARCHAR(30),
						time TIMESTAMP,
						PRIMARY KEY(stockItemCode, time));
						'''))
		
		query="INSERT INTO stock (price, price_change, stockItemCode) VALUES("+price+","+price_change+",\'"+code+"\')"
		conn.execute(text(query))
		return render_template('home.html',result=parsed)

@app.route("/data")
def querydata():
	
	engine=create_engine('mysql://root:1234@localhost/test')
	conn=engine.connect()
	a="stockItemCode\tprice\tprice_change\ttime\n"
	res=conn.execute("SELECT * FROM stock")
	for data in res:
		a+=(data['stockItemCode']+" \t"+data['price']+"\t"+data['price_change']+"\t"+str(data['time'])+"\n")
		
	return render_template('data.html',result=a)

if __name__=='__main__':	#run app
	app.debug = True 		#debug option
	app.run()
