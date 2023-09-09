import re
import pymongo as mg
from lxml import etree
from pprint import pprint as pp

MONGONDB = "mongodb://admin:admin123@localhost:27017/"
BASE_FILE = "./08-20/messages"
TOTAL_PAGES = 169 # 总页数
flag = 0 # 种子大小错误指示

# 连接数据库并返回==>表对象
def connect_db(db_name,collection_name):
    myclient = mg.MongoClient(MONGONDB)
    mydb = myclient[db_name]
    mycollection = mydb[collection_name]
    
    return mycollection

# 获得某一页匹配出来的texts列表
def get_texts(page):
    if page == 1:
        file_path = f'{BASE_FILE}.html'
    else:
        file_path = f'{BASE_FILE}{page}.html'
        
    html = etree.parse(file_path,etree.HTMLParser())
    texts = html.xpath('//div[@class="text"]')
    
    return texts

# 匹配并写入数据库
def regex(text,number,collection):
    global flag
    # 单个
    id_regex = re.compile("番号.*?:\s(.*?)<")
    name_regex = re.compile("片名.*?\d+\s(.*?)<")
    length_regex = re.compile("时长.*?\s(.*?)<")
    # 多个
    # size_regex = re.compile("文件大小.*?\s(.*?)\s")
    size_regex = re.compile("(\d+\.\d+GB|\d+\.\d+MB|\d+\.\d+|\d+GB|\d+MB)") #数据太脏了
    date_regex = re.compile("更新日期.*?\s(.*?)<")
    link_regex = re.compile("<code>(.*?)<")

    # 结果
    idd = re.search(id_regex, text).group(1).strip() if re.search(id_regex, text) else None
    name = re.search(name_regex, text).group(1).strip() if re.search(name_regex, text) else None
    length = re.search(length_regex, text).group(1).strip() if re.search(length_regex, text) else None

    sizes = re.findall(size_regex, text) if re.findall(size_regex, text) else []
    dates = re.findall(date_regex, text) if re.findall(date_regex, text) else []
    links = re.findall(link_regex, text) if re.findall(link_regex, text) else []
    sum_number = len(links)
    # print(number,idd,sizes,dates,links)
    if flag == 1:
        pass
        # print("===错误发生在第" + str(number) + "项======")
    flag = 0
    for j in range(sum_number):
        # 文件大小的数据太乱了，没法兼顾所有情况
        if len(sizes) < sum_number:
            shit_size = 0
        else:
            shit_size = sizes[j]
        if shit_size == 0:
            flag = 1
        context = {"番号":idd,
                   "片名":name,
                   "时长":length,
                   "磁力":{ "大小":shit_size,
                            "更新日期":dates[j],
                            "磁力链接":links[j]}}
        
        collection.insert_one(context)


def main():
    collection = connect_db("test","Jav")
    for page in range(1,TOTAL_PAGES):
        texts = get_texts(page)
        for number in range(len(texts)):
            text = etree.tostring(texts[number],encoding='utf-8').decode('utf-8')
            regex(text,number,collection)
        print("第"+str(page)+"页已完成...")
            
main()