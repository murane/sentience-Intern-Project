import urllib
import datetime
from sqlalchemy import *
from sqlalchemy.sql import text,select
from bs4 import BeautifulSoup
from flask import Flask,render_template,request		
app = Flask(__name__)	
@app.route("/")			#default page	
def main():
	
	return render_template('home.html')

@app.route("/inputAction",methods=['POST','GET'])					#input button action
def inputAction():
	if request.form['stockItemCode']=="":							#if no input
		msg="Please enter profer stockItemCode"						#give a message
		return render_template('home.html',result=msg)
	else:															#else search stock item
		url="http://google.com/finance?q="+request.form['stockItemCode']	
		html=urllib.urlopen(url)									#use urllib query to google finance
		soup=BeautifulSoup(html,'html.parser')						#and parse it by soup
		
		code=request.form['stockItemCode']							#get code by input value

		parse=soup.findAll('span',{'class':'pr'})
		price=parse[0].find('span').text
		price=str(price).replace(',','')
		
		parse=soup.findAll('div',{'class':'id-price-change'})
		price_change=parse[0].find('span').contents[0].text
		price_change=str(price_change).replace(',','')				#parse price, price_change



		parsed ="price of "+code+" is "+price+" price change is "+price_change
																	#parsed text will be rendered		
		engine = create_engine('mysql://root:1234@localhost/test')	
		conn= engine.connect()										#create mysql engine and conn object
		conn.execute(text(											#if table doesn't exist create it
						'''CREATE TABLE IF NOT EXISTS stock(		
						stockItemCode VARCHAR(30),
						price VARCHAR(30),
						price_change VARCHAR(30),
						time TIMESTAMP,
						PRIMARY KEY(stockItemCode, time));
						'''))
		
		query="INSERT INTO stock (price, price_change, stockItemCode) VALUES("+price+","+price_change+",\'"+code+"\')"
		conn.execute(text(query))									#use parsed data make query string to insert
		return render_template('home.html',result=parsed)			#data is inserted and rendering html

@app.route("/data")													#if we see result
def querydata():
	
	engine=create_engine('mysql://root:1234@localhost/test')		#first make mysql engine and conn obj
	conn=engine.connect()
	a="stockItemCode\tprice\tprice_change\ttime\n"					#string for data
	res=conn.execute("SELECT * FROM stock")							#make query
	for data in res:												#by select query iterate it 
		a+=(data['stockItemCode']+" \t"+data['price']+"\t"+data['price_change']+"\t"+str(data['time'])+"\n")
		
	return render_template('data.html',result=a)

if __name__=='__main__':	#run app
	app.debug = True 		#debug option
	app.run()
