# READING

&emsp;&emsp;以下将介绍如何使用Hexo搭建静态博客框架，并将其部署于Github Pages生成博客网页。全过程无需自行购买域名与服务器。

# 需要准备的工具  

- ✅**Hexo** [Hexo官网](https://hexo.io/zh-cn/) ←博客皮肤可以在里面选择  

- ✅**Github** [Github官网](https://github.com/) 要建立一个库（repository）

- ✅安装Node.js（Hexo 依赖） [Node.js官网](https://nodejs.org/zh-cn)  
安装后在cmd检查是否安装成功：  

```
node -v  #显示版本号即成功
npm -v
```

- ✅安装Git [Git官网](https://git-scm.cn/downloads)  
🌟默认路径安装，不要改！  
（安装包下载慢的问题可以尝试换用Chrome浏览器解决。）  

# 开始吧！

## 搭建Github repository并clone至本地  

[一个非常详细的Github使用/上传作品的指南](https://blog.csdn.net/A1_3_9_7/article/details/144674444?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_baidulandingword~default-0-144674444-blog-149396411.235^v43^pc_blog_bottom_relevance_base1&spm=1001.2101.3001.4242.1&utm_relevant_index=3)

⬆️ 链接详细介绍了如何获取SSH密钥并配置至GitHub。配置了SSH密钥，就可以免密执行`git push`（注：git部署操作请参考以上链接，本文仅讨论基于Hexo博客框架下如何进行内容部署）


## 初始化Hexo项目  
&emsp;&emsp;以下全部均在根目录/Github/xxxx完成！在根目录右键选择“Open Git Bash Here”以输入指令。

### 安装Hexo  

```
# 安装Hexo命令行工具
npm install -g hexo-cli
```

### 初始化博客  
&emsp;&emsp;hexo init要求在根目录内安装，且必须是**空白文件夹**，但如果按照本文顺序操作，此时读者应该已经完成GitHub仓库克隆到本地的操作，根目录内已生成README.md文件，导致无法在根目录内完成安装工作。此时可以通过新建空白文件夹安装后再拷贝回根目录的方法解决。（理论上也可以先把README.md文件移走，待完成初始化后再移回，但我试过貌似不work）  

```
hexo init
npm install
```

&emsp;&emsp;**至此，你已经完成了整个博客的基本框架搭建！！！恭喜你！！！**👏🏻👏🏻👏🏻

&emsp;&emsp;现在可以到Hexo官网选择喜欢的皮肤，并根据发布者提供的指引进行安装以及个性化修改~  
&emsp;&emsp;推荐两个皮肤，都是非常成熟，功能超多的，但体感自定义空间较少...  
[Butterfly](https://butterfly.js.org/)
[maupassant](https://www.haomwei.com/technology/maupassant-hexo.html)

# 文章部署流程  

## 内容编辑

### hexo new “文件名”  

```
hexo new “文件名”
```

&emsp;&emsp;运行后将在source/_posts/中生成对应的.md文件。  

**创建tags页**（categories、about页同理）

```
hexo new page tags
```

### Markdown语法编辑文本  

```
---
title: xxx
date: 2025-07-25 ~~20:39:53~~
tags: [xx,xx]
categories: xxx
---
```

⬆️ Frountmatter
&emsp;&emsp;建议把“date”的时间删除，仅留下日期，因为comfig文件内没有时间配置，无法识别时间，导致部署报错。  
&emsp;&emsp;“tags”、“categories”等可以自定义，Hexo会根据文章的tags自动汇总所有标签，并生成标签页（需主题支持）。  
[Markdown语法学习](https://markdown.com.cn/)

## 上传步骤

### hexo clean

```
hexo clean
```

&emsp;&emsp;运行后清理旧的pubilc/文件。

### hexo g/hexo generate

```
hexo g
```

&emsp;&emsp;运行后会将.md文件编译为 **HTML、CSS、JS 等静态资源**，输出到public/文件夹。只有public/中的文件才能被部署到 GitHub Pages。  
&emsp;&emsp;pubilc/中的文件包含核心文件和资源文件：  

核心文件：

```
public/
├── index.html                # 博客首页
├── archives/                 # 归档目录
│   └── index.html            # 归档页
├── tags/                     # 标签目录
│   └── index.html            # 标签列表页
│   └── [标签名]/index.html   # 单个标签下的文章列表
├── categories/               # 分类目录
│   └── index.html            # 分类列表页
│   └── [分类名]/index.html   # 单个分类下的文章列表
```

资源文件：

```
public/
├── css/                      # CSS 样式文件
├── js/                       # JavaScript 文件
├── images/                   # 图片资源（来自 source/images/）
└── favicon.ico               # 网站图标
```

&emsp;&emsp;**source/_posts/中的文件不可以清空！**

### hexo d/hexo deploy

```
hexo d
```

&emsp;&emsp;运行后即把文章部署到GitHub。（首次部署会要求输入 GitHub 账号密码）

&emsp;&emsp;至此，文章已经可以在你的静态博客网页看到你发布的文章啦！  
&emsp;&emsp;可以选择 [Vercel](https://markdown.com.cn/) 托管部署（但网页需要梯子才能打开），也可以直接使用Github Pages（在repository的界面找到Settings--Pages）节约开发成本。

# 可能会用到的网站

- ✅适配Markdown语法的emoji网站： https://emojipedia.org/  
- ✅远程调用网页图标的icon库：https://fontawesome.com/?o=r （需把icon云库的地址配置进皮肤文件内以调用）  
- ✅十分方便好用的评论区模块 [Hyvor talk](https://talk.hyvor.com/) ，但要花钱（气晕了）  
- ✅完全开源的一个评论区模块 [Remark42](https://remark42.com/) ，但我还没研究出来怎么安装配置（目移  
- ✅文章字数统计Hexo插件与配置： https://github.com/willin/hexo-wordcount
