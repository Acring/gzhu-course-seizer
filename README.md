# 广大抢课脚本

本脚本只做学习使用, 不做商业用途



- version: 1.0.0
- author: acring
- 简介:

广大抢课脚本, 可抢全校性选课和体育选课的课程

- usage:

点开run.py, 按提示修改上面的学号,密码,目标老师等信息

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



- package:

  - requests
  - bs4

  ​