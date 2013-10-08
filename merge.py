#coding=utf-8
import sys, codecs, os,csv

file_path = os.path.normpath(os.path.dirname(__file__))
data_path = os.path.join(file_path, 'data')

#主程序
def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
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