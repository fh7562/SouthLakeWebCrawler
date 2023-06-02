"""
a southlake crawler
"""

import sys                           # 引入系统模块
import os                            # 引入操作系统模块
import shutil                        # 引入文件操作模块
import re                            # 引入正则表达式模块
import requests                      # 引入网络请求模块
import jieba                         # 引入中文分词模块
from wordcloud import WordCloud      # 引入词云模块
import matplotlib.pyplot as plt      # 引入绘图模块

start_year = 0  # 初始化
start_month = 0
end_year = 0
end_month = 0
step = 4
max_page = 20

news_channel = ''
news_channel_cn = ''
news_channels = ['xykx', 'rcpy', 'kxyj', 'xsjl', 'shfw',
                 'hnrw', 'sssp', 'mthn', 'nhsd']   # 新闻频道在网站url中的名称列表
news_channels_cn = ['校园快讯', '人才培养', '科学研究', '学术交流', '社会服务',
                    '华农人物', '狮山时评', '媒体华农', '南湖视点']  # 新闻频道的中文名称列表

print("---a southlake crawler---")
print("请选择对应的新闻频道或者操作，输入对应的数字后按回车键\n\
1.校园快讯 2.人才培养 3.科学研究 4.学术交流 5.社会服务\n\
6.华农人物 7.狮山时评 8.媒体华农 9.南湖视点 10.所有频道\n\
0.删除所有生成文件\n\
输入其它数字以退出")
channel_num = int(input())           # 获取用户输入的频道编号
if channel_num < 0 or channel_num > 10:  # 如果用户输入的编号不在范围内，则退出程序
    print("退出程序！")
    sys.exit()
elif channel_num == 0:              # 如果用户输入的编号为0，则删除所有生成文件
    for item in news_channels_cn:
        if os.path.exists(item):
            shutil.rmtree(item)
    print("删除完毕！")
    sys.exit()
elif channel_num == 10:             # 如果用户输入的编号为10，则抓取所有频道
    first = 1
    last = 10
else:                               # 如果用户输入的编号为1-9，则只抓取对应频道
    first = channel_num
    last = channel_num + 1

print("是否在创建词云图后展示？\n0.不展示 1.展示")
show = int(input())

for channel_num in range(first, last):  # 遍历频道编号的范围，获取新闻频道的名称和中文名
    news_channel = news_channels[channel_num - 1]
    news_channel_cn = news_channels_cn[channel_num - 1]
    stop = False
    print(f"正在创建“{news_channel_cn}”频道！")
    file_path = f'./{news_channels_cn[channel_num - 1]}'  # 创建存储文件夹，文件夹名为频道的中文名
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    for i in range(1, max_page//step + 2):  # 遍历网站上的新闻页码，获取每个新闻的标题和发布日期
        start_page = (i - 1) * step + 1
        end_page = i * step
        titles = ''
        all_dates = []
        file_name = ''
        find = ''
        for page in range(start_page, end_page + 1):
            if page > max_page:
                break
            print(f"访问第{page}页中……")
            # 访问新闻页面并获取页面内容
            url = f"http://news.hzau.edu.cn/news/{news_channel}/{page}.shtml"
            try:
                res = requests.get(url, timeout=30)
            except requests.exceptions.Timeout:
                print("网站访问超时！")
                sys.exit()
            article = res.content.decode(res.apparent_encoding)
            # 从页面内容中提取标题和发布日期
            find = re.findall(
                r"class=\"title\" target=\"_blank\">(.*?)</a><span class=\"date\">", article)
            # 如果无法获取到标题和发布日期，则停止遍历该频道的新闻页码
            if len(find) == 0:
                end_page = page - 1
                print(f"第{page}页后无内容！")
                stop = True  # 由于一张词云采用了数页内容，此处设置stop变量，可以对已爬取内容进行处理，且在页面为空时及时停止爬取
                break
            # 去除标题中的【】和[]
            for line in find:
                line = re.sub(r"【.*?】|\[.*?\]", "", line)
                titles += line + '\n'
            # 从页面内容中提取所有的发布日期
            dates = re.findall(
                r"<span class=\"date\">(\d+)年(\d+)月", article)
            all_dates = all_dates + dates
        # 如果获取到的标题和发布日期为空，则停止遍历该频道的新闻页码
        if len(titles) == 0:
            break

        start_date_str = all_dates[0]  # 获取爬取的新闻中第一篇文章的发布日期
        start_year = start_date_str[0]  # 提取发布日期中的年份
        start_month = start_date_str[1]  # 提取发布日期中的月份
        end_date_str = all_dates[-1]  # 获取爬取的新闻中最后一篇文章的发布日期
        end_year = end_date_str[0]  # 提取发布日期中的年份
        end_month = end_date_str[1]  # 提取发布日期中的月份

        # 构造文件名，格式为“最后一篇文章的发布时间-第一篇文章的发布时间”
        file_name = f"{end_year}.{end_month}-{start_year}.{start_month}"
        full_name = f"{file_name}.txt"

        fo = open(os.path.join(
            file_path, f"{news_channel_cn}_{file_name}.txt"), 'wb')  # 创建文件并写入爬取的文章标题
        fo.write(titles.encode('utf_8'))
        fo.close()

        print(f"第{start_page}-{end_page}页爬取完毕！\n建立第{i}个词云中……")

        text = open(os.path.join(
            file_path, f"{news_channel_cn}_{file_name}.txt"), 'r', encoding="utf-8").read()  # 读取刚刚创建的文件
        text = ' '.join(jieba.cut(text))  # 对文件中的文本进行分词
        exclude = {'的', '了', '和', '是', '在', '我们', '要', '与', '我校', '第', '次',
                   '我', '学校', '校', '年', '高翅', '李召虎', '开展', '推进', '召开', '工作', '学习'}  # 除去一些不必要的词语，可根据具体情况进行更改
        wc = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', width=1600, height=1200,
                       mode="RGBA", background_color="black", stopwords=exclude).generate(text)  # 生成词云
        plt.axis('off') # 展示生成的内容，并附带日期标签
        plt.text(800, 100, file_name, fontsize=15, ha='center', va='center', color='black', bbox=dict(
            boxstyle='round,pad=0.5', fc='white', ec='black', lw=1, alpha=0.75))
        plt.imshow(wc)
        plt.savefig(f'./{news_channel_cn}/{news_channel_cn}_{file_name}.png', bbox_inches='tight')
        if show != 0:
            plt.show()
        plt.close()
        print(f"第{i}个词云建立完毕！")

        if stop is True:
            break

print("建立完毕，程序结束！")
