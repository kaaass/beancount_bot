# beancount_bot

适用于 Beancount 记账的 Telegram 机器人

**该项目正在开发中，可能会发生：API 频繁修改且不向上兼容、发布版本主要功能因 BUG 无法使用等**

![GitHub](https://img.shields.io/github/license/kaaass/beancount_bot)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/kaaass/beancount_bot?color=green&label=version)
![PyPI](https://img.shields.io/pypi/v/beancount_bot)
[![Build Status](https://app.travis-ci.com/kaaass/beancount_bot.svg?branch=master)](https://app.travis-ci.com/kaaass/beancount_bot)

## Features

- 支持简易鉴权
- 支持交易创建、撤回
- 内建自由且强大的模板语法，适用于各种记账需求
- 允许通过插件扩展记账语法
- 支持定时任务

## 安装

```shell
pip install beancount_bot
```

## 使用

1. 下载示例配置文件 `beancount_bot.example.yml`、`template.example.yml`
2. 修改后保存为 `beancount_bot.yml`、`template.yml`
3. 执行 `beancount_bot`

## 推荐插件

1. [kaaass/beancount_bot_costflow](https://github.com/kaaass/beancount_bot_costflow)：支持 Costflow 语法

欢迎在 Issue 推荐优秀插件。

## 插件开发

请查阅项目 Wiki。

## Roadmap

1. [x] ~~支持定时备份~~ 使用定时任务支持
2. [ ] 支持账单导入
