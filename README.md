# beancount_bot

适用于 Beancount 记账的 Telegram 机器人

![GitHub](https://img.shields.io/github/license/kaaass/beancount_bot)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/kaaass/beancount_bot?color=green&label=version)
![PyPI](https://img.shields.io/pypi/v/beancount_bot)
[![Test and Lint](https://github.com/kaaass/beancount_bot/actions/workflows/test-with-lint.yml/badge.svg?branch=master)](https://github.com/kaaass/beancount_bot/actions/workflows/test-with-lint.yml)

## Features

- 支持简易鉴权
- 支持交易创建、撤回
- 内建自由且强大的模板语法，适用于各种记账需求
- 允许通过插件扩展记账语法
- 支持定时任务
- 支持多个用户同时记账，设置不同的标签

## 安装

### 通过 Pip (Pypi)

```shell
pip install beancount_bot
```

### 通过 Docker

- [kaaass/beancount_bot_docker](https://github.com/kaaass/beancount_bot_docker)：beancount_bot 的 Docker 镜像
- [kaaass/beancount_bot_costflow_docker](https://github.com/kaaass/beancount_bot_costflow_docker)：包含 beancount_bot 与 Costflow 插件的 Docker 镜像

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
2. [ ] ~~支持账单导入~~ 暂时搁置
3. [ ] i18n support
4. [ ] 完善对多人记账的支持
