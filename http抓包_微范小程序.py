import json
import os
import string
import re
import os.path, time
#python version>=3.6
bookName=r"城市道路交叉口设计规程 CJJ 152-2010"
directory_str=r'c:\Users\Administrator\SynologyDrive\zhuabao'
pat1 = re.compile('Body:')  # 从最原始的txt数据提取Json的pattern
pattern1=re.compile(r'>\W*(\d+|[A-Z])\.\s*(\d+)')    #提取每个小txt中的序号来排序章节，已把附录字母包含进来
pattern2 = re.compile('\d+.\d+.\d+')
pattern3 = re.compile('p>')
output_fn=bookName+'.html'

def split_body(fp):
    '''
    处理抓包后的响应文件：sslCaptureData_0.txt
    将response按json格式输入到Python中
    '''
    with open(fp, encoding='utf8') as f:
        txt = f.read()
    lst = pat1.split(txt)
    try:
        dt = json.loads(lst[-1],encoding='utf8',strict=False)
        return dt['data']['detail']['list']
    except:
        return None

def parse_content(dts):
    '''
    dts:return of split_body,字典
    将规范正文提取出
    并抽出条文序号用于多文件排序
    '''
    ots = ''
    for dt in dts:
        ots = ots + dt['content'] + '\n'
    m=re.search(pattern1,ots)
    #有的规范带有附录如C.0.1，帮直接正则返回会报错
    try:
        if not m.group(1) in string.ascii_uppercase:
            return [m.group(1),m.group(2),ots]
        else:
            return [ord(m.group(1)),m.group(2),ots]
    except:
        return None

def parse_explain(dts):
    '''
    提取规范若有条文说明
    '''
    expns = ''
    for i in dts:
        if i['explain'] and i['explain'] not in expns:
            expns = expns + i['explain'] + '\n'
    return expns

def parse_explain2dt(dts):
    '''
    提取规范若有条文说明，并去重
    '''
    expns_dt = {}
    for i in dts:
        explain = i['explain'] if not i['explain'] == None else None
        if explain and explain not in expns_dt:
            key = re.findall(pattern2, explain)[0]
            expns_dt[key] = re.sub(pattern3, 'i>', explain)
    return expns_dt

def loop_files(directory_in_str):
    temp = []
    for root, dirs, files in os.walk(directory_in_str):
        for name in files:
            if os.path.join(root, name).endswith('.txt'):
                temp.append(os.path.join(root, name))
    # return sorted(temp, key=lambda x: get_file_mtime(x))
    return temp

def html_writer(book_name,pageGen):
    filename='c:\\Users\\Administrator\\SynologyDrive\\zhuabao\\output.html'
    part1='''<html>
    <head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" media="screen" href="main.css">
  <script src="main.js"></script>
  <body>'''
    print(part1.format(book_name),file=open(filename,'a',encoding='utf8'))
    
    for page in pageGen:
        print(page,file=open(filename,'a',encoding='utf8'))

    part3='''</body>
    </html> '''
    print(part3,file=open(filename,'a',encoding='utf8'))
def main():
    fileList = loop_files(directory_str)
    fullPage = []
    for file in fileList:
        dts = split_body(file)
        if dts:
            fullPage.append(parse_content(dts))
    sortedPage=sorted(fullPage,key=lambda x:(int(x[0]),int(x[1])))
    for page in sortedPage:
        yield page[-1]

if __name__ == '__main__':
    pageG=main()    
    html_writer(bookName,pageG)