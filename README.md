# double ma

一个基于双均线策略提供投资决策的程序。

需要手工添加一些数据指标，然后程序会提供操作建议。

## 基本操作

先进入文件夹`doublema`所在目录。

### 添加一条记录

`python -m doublema.doublema add mana -d 2022-03-27 -k 2.6204 --ma13-price=2.4818 --ma55-price=2.6951 --crypto=7.774672 --usdt=20`

### 设置一条记录里的某一项

`python -m doublema.doublema set people -d 2022-03-26 --crypto=264.4399878 --usdt=8`

### 查看已有的记录

`python -m doublema.doublema show doge`

### 获得交易建议

`python -m doublema.doublema advice eth`

### 回放策略效果

`python -m doublema.doublema playback luna`

## 使用流程

1. 先更新前一天的记录（已经收盘）
1. 获取建议
1. 根据建议做交易
1. 设置交易后的结果
