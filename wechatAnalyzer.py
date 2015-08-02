# Author: Jichen Yang <jichenyang@gmail.com>
#
# (c) 2015
#
# License: MIT

# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
import os
import jieba
import re
import codecs
from scipy.misc import imread
from radar_plot import *
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

class wechatAnalyzer(object):
    """wechatAnalyzer object for analyzing wechat historical messages.

    Parameters
    ----------
    font_path : string
        Font path to the font that will be used (OTF or TTF).
        Defaults to DroidSansMono path on a Linux machine. If you are on
        another OS or don't have this font, you need to adjust this path.


    Attributes
    ----------
        ``_relationship``: saved relationship matrix indicating how close two names are.
        ``_file_path``: the path for saved dataset.
        ``_zhfont``: saved font file, which can display chinese character.
        ``_contactsAndNick``: will be generated during the analysis.
        ``_contacts_topN``: top N active people.
        ``_topN``: only generates analysis for top N active people.
        ``_radarList``: words most interested and will used to generate radar plot.

    Notes
    -----
    Larger canvases with make the code significantly slower. If you need a large
    word cloud, try a lower canvas size, and set the scale parameter.

    The algorithm might give more weight to the ranking of the words
    than their actual frequencies, depending on the ``max_font_size`` and the
    scaling heuristic.
    """

    def __init__(self, file_path="test.xlsx"):
        self._file_path = file_path
        self._relationship = None
        self._contactsAndNick = None
        self._contacts_topN = None
        self._topN = 10
        self._radarList = ['男神', '女神','八卦','红包','Photo','呲牙','约']
        self._zhfont = matplotlib.font_manager.FontProperties(fname='./fonts/msyhbd.ttc')

    def loaddata(self):
        """Load a xlsx file with wechat messages saved in.

        Returns: a pandas table
        """
        if self._file_path is not None:
            yizhongzhazha = pd.read_excel(self._file_path,
                                        'Sheet1',index_col=None, na_values=['NA'],parse_dates=['Date'])
        else:
            print("Please indicate the message file want to be loaded.")
            return
        return yizhongzhazha

    def clockheat(self, yizhongzhazha):
        """Make clock heatmap to show the hottest hour.

        Parameters:
            yizhongzhazha: a pandas object for message table

        Returns: clock heat plots.
        """
        if yizhongzhazha is None:
            print("Need load message table first.")
            return
        date = yizhongzhazha.iloc[:, 0]
        date_hour = []
        for i in range(len(date)):
            date_hour += [date[i].strftime("%H")]
        date_hour = pd.DataFrame(date_hour)
        date_hour_counts = date_hour.iloc[:, 0].value_counts()
        print("let's have a look which hour people like to talk most? \
        \nThe following table shows top 5 hours have most messages.\
        \n4797 messages appeared at 9 oclock!")
        pd.DataFrame(date_hour_counts.head())
        print("shows the dinstribution of message counts across hours.")
        print("seems that at "+date_hour_counts.index[date_hour_counts == max(date_hour_counts)][0] \
             + ' oclock we have most messages!')
        tmp = date_hour_counts/max(date_hour_counts)
        radii = [0 for i in range(24)]
        for i in range(24):
            if len(tmp[tmp.index.astype(int) == i]) == 0:
                continue
            radii[i] = tmp[tmp.index.astype(int) == i][0]
        N = 24
        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        width = [np.pi / 13 for i in range(24)]
        ax = plt.subplot(111, polar=True)
        bars = ax.bar(theta, radii, width=width, bottom=0.1, linewidth=0)
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_xticks(np.linspace(0, 2*np.pi, 24, endpoint=False))
        ax.set_xticklabels(range(24))
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.pi/2.0)
        plt.grid(which='both', alpha=0.3)
        for r, bar in zip(radii, bars):
            bar.set_facecolor(plt.cm.jet(r/1.))
            bar.set_alpha(0.8)
        plt.savefig("clockheatmap.png",dpi=300)
        plt.close()
        #plt.show()

    def relationship(self, yizhongzhazha=None):
        """calculate relationship.

        Returns:
            _relationship: a pandas object
        """
        if yizhongzhazha is None:
            print("Need load message table first.")
            return
        nicknames = ['胡一刀','TT',
           '骚哥','鸭鸭',
           '氨基','霍乱','小安子']
        contacts = yizhongzhazha.iloc[:,1]
        contacts = list(contacts.value_counts().index)
        # only consider top topN=50 active people
        contacts_topN = contacts[:self._topN]
        contactsAndNick = contacts+nicknames+self._radarList
        relationship = np.zeros(shape=(len(contactsAndNick), len(contacts_topN)), dtype=int)
        relationship = pd.DataFrame(relationship)
        relationship.index = contactsAndNick
        relationship.columns = contacts_topN
        messages = yizhongzhazha.iloc[:, 4]
        messages = list(messages)
        for i in range(len(messages)):
            for j in range(len(contactsAndNick)):
                if contactsAndNick[j] in str(messages[i]):
                    tmp = yizhongzhazha.iloc[i, 1]
                    if tmp not in contacts_topN:
                        continue
                    ncol = contacts.index(tmp)
                    relationship.iloc[j, ncol] += 1
        relationship.to_csv("relationship.csv", encoding='utf-8')
        self._relationship = relationship
        self._contactsAndNick = contactsAndNick
        self._contacts_topN = contacts_topN


    def attriplot(self, yizhongzhazha=None):
        """Do attributes plots. need to run relationship()
        first to get self._relationship.

        Returns: None, plots will be saved in 'attriplots.png'
        """
        if yizhongzhazha is None:
            print("Need load message table first.")
            return
        if self._relationship is None:
            print("Need to calculate relationship first.")
            return
        contacts = yizhongzhazha.iloc[:, 1]
        contacts = list(contacts.value_counts().index)
        # only consider top topN=50 active people
        contacts_topN = contacts[:self._topN]
        sumMessage = yizhongzhazha.iloc[:, 1].value_counts().values[:self._topN]
        data_radar = self._relationship.iloc[(len(self._relationship)-len(self._radarList)):, ]
        data_radar = data_radar.append(pd.Series(sumMessage, index=contacts_topN), ignore_index=True)
        data_radar.index = self._radarList+['sum']
        data_radar = data_radar.apply(lambda x: x/(x.max()+0.01))
        data_radar = data_radar.apply(lambda x: x/(x.max()+0.0001), axis=1)
        # set score as square root
        data_radar = data_radar.applymap(lambda x: math.sqrt(x))
        data_radar = data_radar.drop('sum')
        # now prepare data for radar plot
        data_to_radar = {'column names': ['花痴', '色', '八卦', '红包', '真相党', '龅牙', '求约']}
        for i in range(len(data_radar.iloc[0, :])):
            tmp_index = data_radar.columns[i]
            tmp_data = [list(data_radar.iloc[:, i].values)]
            data_to_radar[tmp_index] = tmp_data
        self.plot_radar(data_to_radar, len(data_to_radar['column names']))

    def plot_radar(self, example_data, nVar):
        N = nVar
        theta = radar_factory(N, frame='polygon')
        data = example_data
        people_Num = len(data)
        spoke_labels = data.pop('column names')
        fig = plt.figure(figsize=(9, 2*people_Num))
        fig.subplots_adjust(wspace=0.55, hspace=0.10, top=0.95, bottom=0.05)
        colors = ['b', 'r', 'g', 'm', 'y']
        # Plot the four cases from the example data on separate axes
        for n, title in enumerate(data.keys()):
            ax = fig.add_subplot(int(people_Num/3)+1, 3, n+1, projection='radar')
            plt.rgrids([0.2, 0.4, 0.6, 0.8])
            plt.setp(ax.get_yticklabels(), visible=False)
            plt.ylim([0,1])
            ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),color='b',
                         horizontalalignment='center', verticalalignment='center',fontproperties=zhfont)
            for d, color in zip(data[title], colors):
                ax.plot(theta, d, color=color)
                ax.fill(theta, d, facecolor=color, alpha=0.25)
            ax.set_varlabels(spoke_labels)
        # add legend relative to top-left plot
        plt.subplot(int(people_Num/3)+1, 3, 1)
        plt.figtext(0.5, 0.965, '战力统计',fontproperties=self._zhfont,
                    ha='center', color='black', weight='bold', size='large')
        plt.savefig("attriplots.png", dpi=300)
        plt.close()

    def wordcloudplot_focus(self, yizhongzhazha=None, backimage=None):
        """Do wordcloud plots for contacts. need to run relationship()
        first to get self._relationship.
        Parameters
            yizhongzhazha: pandas object by loading the data
            backimage: background image file's directory

        Returns: basic word cloud plots saved in files
        """
        if yizhongzhazha is None:
            print("Need load message table first.")
            return
        if self._contacts_topN is None:
            print("need to run relationship() first.")
            return
        if backimage is not None:
            custompic = imread(backimage)
        else:
            custompic = None
        if not os.path.exists('./wordcloud'):
            os.makedirs('./wordcloud')
        wordcloud = WordCloud(background_color="white", mask=custompic,
                              max_words=2000,scale=3)
        for k in range(len(self._contacts_topN)):
            text=self._relationship.iloc[:,k]
            text_to_wordcloud=[]
            for i in range(len(text)):
                text_to_wordcloud.append((text.index.values[i]+' ')*text[i])
            text=''.join(text_to_wordcloud)
            wordcloud.generate(text)
            wordcloud.to_file("./wordcloud/"+self._relationship.columns[k]+'2.png')

    def generatedict(self):
        userDict=list(self._contactsAndNick)
        for i in range(len(userDict)):
            tmp=re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*%？，。《》“”！\
            ]", "", userDict[i])
            if len(tmp)==0:
                userDict[i]='\n'
            else:
                userDict[i]=tmp+' 1000\n'
        dictfile = codecs.open("userdict.dict", "w", "utf-8")
        for i in range(len(userDict)):
            tmp=userDict[i].encode('utf-8').decode('utf-8','ignore').encode("utf-8")
            dictfile.write(tmp.decode("utf-8",'ignore'))
        dictfile.close()


    def wordcloudplot_all(self, yizhongzhazha=None, backimage=None):
        """Do wordcloud plots for all messages. need to do word tokenization.
        run relationship() first, and if user-defined dict is not avaliable,
        do generatedict() first. This function will run for a while (about 30 minutes).
        Parameters
            yizhongzhazha: pandas object by loading the data
            backimage: background image file's directory

        Returns: basic word cloud plots saved in files
        """
        if yizhongzhazha is None:
            print("Need load message table first.")
            return
        if self._contacts_topN is None:
            print("need to run relationship() first.")
            return
        messages2=yizhongzhazha.iloc[:,4]
        # Replace in 'text' all occurences of any key in the given dictionary by its corresponding value
        def multiple_replace(dict, text):
            regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
            return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)
        if os.path.exists("userdict.dict"):
            print("detected user-defined dictionary, loading...")
            jieba.load_userdict("userdict.dict")
        else:
            print("no user dictionary found, " + "will use default dictionary, " +
                  "but if want a better tokenization, run generatedict() first.")
        nonsense={' 一下 ': ' ', ' 了 ': ' ', ' 啊 ': ' ', ' 是 ': ' ', ' 的 ': ' ' , ' 你 ': ' ', ' 我 ': ' ', ' 都 ': ' ',
         ' 他 ': ' ', ' 又 ': ' ', ' 一个 ': ' ', ' 比 ': ' ', ' 让 ': ' ', ' 子 ': ' ', ' 吧 ': ' ', ' 就 ': ' ',
         ' 个 ': ' ', ' 吗 ': ' ', ' 和 ': ' ', ' 有 ': ' ', ' 人 ': ' ', ' 到 ': ' ', ' 那 ': ' ', ' 里 ': ' ',
         ' 下 ': ' ', ' 从 ': ' ', ' 后 ': ' ', ' 呀 ': ' ', ' 只 ': ' ', ' 哦 ': ' ', ' 去 ': ' ', ' 也 ': ' ',
         ' 在 ': ' ', ' 还 ': ' ', ' 才 ': ' ', ' 再 ': ' ', ' 啊 ': ' ', ' 不 ': ' '}
        if backimage is not None:
            custompic = imread(backimage)
        else:
            custompic = None
        if not os.path.exists('./wordcloud2'):
            os.makedirs('./wordcloud2')
        wc = WordCloud(background_color="white", mask=custompic,
                              max_words=2000,scale=3)
        for i in range(len(self._contacts_topN)):
            peopleID = self._contacts_topN[i]
            chosedIndex = list(yizhongzhazha.index[yizhongzhazha.iloc[:,1].values==peopleID].values)
            chosedMessage = messages2[chosedIndex]
            chosedMessage = chosedMessage.apply(str)
            chosedString = ' '.join(list(chosedMessage.values))
            chosedString = re.sub("[A-Za-z0-9\[\`\~\!\@\#\$\^\&\*\(\)\=\|\{\}\'\:\;\'\,\[\]\.\<\>\/\?\~\！\@\#\\\&\*%？，。《》“”！\
            '\r\n']", "", chosedString)
            cutWords = jieba.cut(chosedString)
            text = " ".join(cutWords)
            text = multiple_replace(nonsense, text)
            wc.generate(text)
            wc.to_file("./wordcloud2/"+self._relationship.columns[i]+'.png')


if __name__ == "__main__":
    import wechatAnalyzer as wa
    test = wa.wechatAnalyzer(file_path="test.xlsx")
    data = test.loaddata()
    test.clockheat(data)
    test.relationship(data)
    test.attriplot(data)
    test.wordcloudplot_focus(data)
    test.generatedict()
    test.wordcloudplot_all(data,backimage='guitar.png')






