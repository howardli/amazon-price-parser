#coding=utf-8
import sys, codecs, os, threading, csv
from Queue import Queue
from write_record import write_record

file_path = os.path.normpath(os.path.dirname(__file__))
config_path = os.path.join(file_path, 'config')
data_path = os.path.join(file_path, 'data')

#主程序
def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
    #读取程序参数
    param_file = codecs.open(os.path.join(config_path, 'param.txt'), 'r', 'utf-8')
    params = param_file.readlines()
    param_file.close()
    #读取url
    url_file = codecs.open(os.path.join(config_path, 'url.txt'), 'r', 'utf-8')
    urls = url_file.readlines()
    url_file.close()
    #读取代理服务器
    proxy_file = codecs.open(os.path.join(config_path, 'proxy.txt'), 'r', 'utf-8')
    proxys = proxy_file.readlines()
    proxy_file.close()  
    #执行程序参数
    for param in params:
        exec param
    #把需要读取的url放到队列中
    queue = Queue(len(urls));
    for url in urls:
        url = url.strip('\r\n')
        if url == '':
            continue;
        queue.put(url)
    #开启多线程进行访问
    threads=[]
    nloops=range(len(proxys))
    for i in nloops:
        t=threading.Thread(target=write_record, args=(i, proxys[i].strip('\r\n'), queue, min_time, max_time))
        threads.append(t)
    for i in nloops:
        threads[i].start()
    for i in nloops:
        print "stop"
        threads[i].join()
    files = os.listdir(data_path)
    data_file = codecs.open(os.path.join(file_path, 'data.csv'), 'a')
    for file in files:
        csv_file = codecs.open(os.path.join(data_path, file), 'r')
        reader = csv.reader(csv_file)
        try:
            for row in reader:
                csv.writer(data_file).writerow(row)
        except:
            pass
        csv_file.close()  
    data_file.close()

if __name__ == '__main__':
    main()