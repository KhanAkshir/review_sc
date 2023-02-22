from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
app = Flask(__name__)

@cross_origin()
@app.route("/")
def homepage():
    return render_template("index.html")

@cross_origin()
@app.route("/review", methods =["POST","GET"])
def index():
    if request.method=='POST':
        try:
            my_str=request.form['content'].replace(" ","")
            flipkart_url="https://www.flipkart.com/search?q="+ my_str
            urCLient=uReq(flipkart_url)
            flipkart_page=urCLient.read()
            urCLient.close()
            flipkart_html=bs(flipkart_page,"html.parser")
            bigbox=flipkart_html.findAll("div",{"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            pro_num=request.form["prodnum"]
            box=bigbox[int(pro_num)]
            product_link= "https://www.flipkart.com" + box.div.div.div.a['href']
            Prodreq=requests.get(product_link)
            product_html=bs(Prodreq.text,'html.parser')
            comment_box=product_html.find_all("div",{"class":"_16PBlm"})

            filename=my_str+".csv"
            fw= open(filename,"w")
            headers="Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]

            for i in comment_box:
                try:
                    name= i.div.div.find("p",{"class":"_2sc7ZR _2V5EHH"}).text
                except:
                    logging.info("Akshir")
                
                try:
                    rating = i.div.div.div.div.text
                except:
                    rating = 'No Rating'
                    logging.info("rating")
                
                try:
                    commenthead=i.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                
                try:
                    comtag = i.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": my_str, "Name": name, "Rating": rating, "CommentHead": commenthead,"Comment": custComment}

                reviews.append(mydict)
            logging.info(f"log my final result {reviews}")

            fw.write(headers)
            client = pymongo.MongoClient("mongodb+srv://Akshir:<password>@cluster0.yinu3eg.mongodb.net/?retryWrites=true&w=majority")
            db = client['review_scrap']
            review_coll=db["review_scrap_data"]



            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return "Something gone wrong"
    else:
        return render_template('index.html')


   

if __name__=="__main__":
    app.run(host="0.0.0.0")
