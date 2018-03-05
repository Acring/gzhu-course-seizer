# 广大抢课脚本

>  本脚本只做学习使用, 不做商业用途

- version: 1.0.1
- author: acring
- 简介:

广大抢课脚本, 可多线程自动选全校性选课和体育选课的课程

- usage:

1. 点开run.py, 按提示修改上面的学号,密码,目标老师等信息

```python
data = {
    "tag": "xxx",  # 标志
    "username": "xxx",  # 学号
    "password": "xxx",  # 密码
    "cour_type": "whole",  # 选课类型 sport/whole
    "teacher": "方碧真",  # 目标老师
    "index": 1  # 相同老师,选第几个
}
```

2. `python run.py` 运行脚本

- package:
  - requests
  - bs4
- 运行截图


![Snipaste_2018-03-05_11-35-32.png](http://upload-images.jianshu.io/upload_images/3026741-0fdefcb30810db09.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![Snipaste_2018-03-05_11-34-11.png](http://upload-images.jianshu.io/upload_images/3026741-d1571c59947428a5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



