# WECHATANALYZER
WeChat (Chinese: 微信) has become the most popular instant messager in China. It provides mobile text and voice messaging communication service, and is available on Android, iPhone, BlackBerry, Windows Phone and Symbian phones. According to wikipedia.org, WeChat has 438 million active users as of august 2014, with 70 million outside of China. People use wechat to interact and socialize, sharing information and comments, as well as communicating to colleagues, therefore, it is quite interesting to explore valuable information from wechat historical messages. 

## HOW TO USE
Download the project, and unzip into a folder. Set the folder as the current work directory, then import wechatAnalyzer.py. The following is an simple example:

```python
import wechatAnalyzer as wa
test = wa.wechatAnalyzer(file_path="test.xlsx")
data = test.loaddata()
test.clockheat(data)
test.relationship(data)
test.attriplot(data)
test.wordcloudplot_focus(data)
test.generatedict()
test.wordcloudplot_all(data,backimage='guitar.png')
```

## DEPENDENCY
wechatAnalyzer requires the following libraries installed:
- pandas
- numpy
- matplotlib
- wordcloud
- jieba
For wechat messages, we expect a lot of Chinese characters, which can not be displayed correctly when generating wordcloud plots with default settings in 'wordcloud' package. The default font used by 'wordcloud' package is 'DroidSansMono.ttf', a true type font by Google, that is apache licensed. The solution is to do the following modification:
  1. copy a font file (here just take 'msyh.ttc' as an example, should use your own lisenced font) to the folder of 'wordcloud' module (e.g. 'C:\Python34\Lib\site-packages\wordcloud')
  2. under the same folder, edit 'wordcloud.py' and find the line start with 'FONT_PATH = ', replace 'DroidSansMono.ttf' by 'msyh.ttc' at the end of this line. 

## EXAMPLES
As an exmpale, 'test.xlsx' file stores a group's wechat messages. iPhone wechat messages can be exported by a tool named 'Tongbu Assistant' (Chinese name: 同步助手). To be noted, exported wechat messages must be saved as a .xlsx file with the exact format.

1 wechatAnalyzer generates a plot to show which clock is the hottest one with most messages happening. 
```python
test.clockheat(data)
```
This command will generate a distribution plot showing how many messages happened on each hour, as follows
<img src="https://github.com/yangyangjuanjuan/wechatAnalyzer/blob/master/example/clockheatmap.png" width="500">

2 wechatAnalyzer can provide interesting plot to rank pre-defined index for each person. Pre-defined index include: '花痴', '色', '八卦', '红包', '真相党', '龅牙', '求约'.
```python
test.relationship(data)
test.attriplot(data)
```
<img src="https://github.com/yangyangjuanjuan/wechatAnalyzer/blob/master/example/index.PNG" width="200">

3 wechatAnalyzer provides different types of wordcloud plots for each person in the group.
```python
test.wordcloudplot_focus(data)
```


