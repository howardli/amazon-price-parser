#coding=utf-8
import sys, codecs, os, traceback, string, random, time, urllib2, csv, logging
from urlparse import urlparse
from Queue import Queue
from parse_data import parse_data

file_path = os.path.normpath(os.path.dirname(__file__))
data_path = os.path.join(file_path, 'data')

logger=logging.getLogger()
handler=logging.FileHandler('write_record.log')
logger.addHandler(handler)

#设置全局访问请求头
opener = urllib2.build_opener()
opener.addheaders = [('Accept', 'text/html, application/xhtml+xml, */*'),
                    ('Accept-Language', 'zh-CN'),
                    ("Connection", "Keep-Alive"),
                    ('Referer', 'http://www.amazon.com'),
                    ('Host', 'www.amazon.com'),
                    ("User-Agent", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0")]
urllib2.install_opener(opener)

#打开相应的url
def open(url, proxy):
    try:
        request = urllib2.Request(url)
        request.set_proxy(proxy, 'http')
        wp = urllib2.urlopen(request,timeout=10)
        content = wp.read()
        code = str(wp.code)
        if code=="404" or code=="503":
            return code
        return content
    except urllib2.HTTPError, e:
        code = str(e.code)
        if code == "404" or code == "503":
            return code
    except:
        logger.error(url + "".join(traceback.format_exception(*sys.exc_info())))
    finally:
        try:
            wp.close()
            del wp
        except: 
            pass

#访问url，并解析数据，保存进csv
def write_record(i, proxy, queue, min_time, max_time):
    try:
        data_file = codecs.open(os.path.join(data_path, '%s.csv'%proxy.split(':')[0]), 'ab')
        error_time = 0
        url = ""
        while True:
            print queue.qsize()
            url = ""
            #gc.collect()
            #objgraph.show_most_common_types(limit=50)
            try:
                url = queue.get(block=False)
            except:
                break
            print "proxy:%s,url:%s"%(proxy, url)
            content = open(url, proxy)
            if not content or content == "503":
                if not content:
                    error_time+=1
                    if error_time > 100:
                        break
                queue.put(url)
                time.sleep(1)
                continue
            if content == "404":
                continue
            #解析价格
            try:
                result_row = parse_data(content)
            except:
                logger.error(url + "".join(traceback.format_exception(*sys.exc_info())))
                queue.put(url)
                #如果读取出错，暂停1秒
                time.sleep(1)
                #一个线程如果错误大于5次，终止该线程
                continue
            if not result_row:
                continue
            csv.writer(data_file).writerow([url.split('/')[5]] + result_row)
            del result_row, url
            #暂停几秒
            stop_time(min_time, max_time)
    except:
        logger.error(url + "".join(traceback.format_exception(*sys.exc_info())))
    finally:
        l = locals()
        if 'data_file' in l:
            data_file.close()

#暂停的时间
def stop_time(min_time, max_time):
    random_time = random.randint(min_time, max_time)
    #print "wait time:%sms"%random_time
    time.sleep(random_time / 1000)