#coding=utf-8
import re

re_producttitle = re.compile(r"<h1 class=\"producttitle\">(.*?)<\/h1>")
re_result = re.compile(r"result\">([\s\S]*?)<\/tbody")
re_sellerInformation = re.compile(r"class=\"sellerInformation\">([\s\S]*?)<\/ul>")
re_seller_name1 = re.compile(r"title=\"(.*?)\"")
re_seller_name2 = re.compile(r"<b>(.*?)<\/b>")
re_cols = re.compile(r"<td>(.*?)<\/td>")
re_price = re.compile(r"class=\"price\">(.*?)<\/span>")
re_olpSecondaryPrice = re.compile(r"class=\"olpSecondaryPrice\">(.*?)<\/span>")
re_price_shipping = re.compile(r"class=\"price_shipping\">(.*?)<\/span>")
re_fulfillment=re.compile(r"Fulfillment by Amazon")
#解析数据
def parse_data(content):
    #0title 1hhibugbox 2hhifba 3hhishipping 4price 5topname 6num 7flag 8bugbox 9shipping 10price 11name 12flag 13bugbox 14shiiping 15price
    data = ["N/A","N/A",0,"N/A","N/A","N/A",0,0,"N/A","N/A","N/A","N/A",0,"N/A","N/A","N/A"]
    data[0] = re.findall(re_producttitle, content)[0]
    results= re.findall(re_result,content)
    loop_count = 1
    low_price = ""
    for result in results:
        sellerInformation = re.findall(re_sellerInformation, result)[0]
        sellers= re.findall(re_seller_name1,sellerInformation)
        if len(sellers)==0:
            seller = re.findall(re_seller_name2,sellerInformation)[0]
        else:
            seller = sellers[0]
        price, shipping, buybox_price = parse_price(result)
        if loop_count == 1:
            low_price = buybox_price
        if loop_count < 3:
            #记录第一二位是否是fullfillment
            if len(re.findall(re_fulfillment,sellerInformation)) > 0:
                data[loop_count*5+2] = 1
            #记录第一二位的名字
            data[6*loop_count-1] = seller
            #记录第一二位的价格
            data[loop_count*5+5], data[loop_count*5+4], data[loop_count*5+3] = price, shipping, buybox_price
        if seller == "HandHelditems":
            if data[2]==1:
                data[2] = 0
                data[4] , data[3], data[1] = price, shipping, buybox_price
            if data[1]=="N/A":
                if len(re.findall(re_fulfillment,sellerInformation)) > 0:
                    data[2] = 1
                data[4] , data[3], data[1] = price, shipping, buybox_price
        #print low_price, buybox_price
        if low_price!="N/A" and buybox_price!="N/A":
            exec "equal ="+str(low_price)+"=="+str(buybox_price)
            if equal:
                data[6]+=1
        loop_count += 1
    return data

    
#解析一个产品的3类价格
def parse_price(row):
    cols = re.findall(re_cols,row)
    if len(cols)==6:#返回有3个价格的格式，先解析price和buybox_price
        price = re.findall(re_price,row)[0].replace("$","")
        buybox_price = re.findall(re_olpSecondaryPrice,row)[0].replace("$","")
        exec "shipping = " + buybox_price + "-" + price
        if shipping < 0:#有可能出现两个价格相反的情况
            exec "price, buybox_price = " + buybox_price + "," + price
            shipping = 0 - shipping
    else:#只有price和shipping，需要自己计算buybox_price
        prices = re.findall(re_price,row)
        if len(prices)>0:
            price = prices[0].replace("$","")
        else:
            price = "N/A"
        shippings = re.findall(re_price_shipping,row)
        if len(shippings)>0:
            shipping = shippings[0].replace("$","")
        else:#兼容shipping为0的情况
            shipping = "0"
        if price !="N/A":
            exec "buybox_price = " + price + shipping
        else:
            buybox_price = "N/A"
        shipping = shipping.replace("+","")
    del cols
    return price, shipping, buybox_price