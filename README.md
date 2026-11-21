# 产品素材库 · Product Asset Library

给 Codex 一个素材文件夹，它会把产品照片、规格书和安装指南整理成能查询的资料库。比如客户问“P39 用哪份安装指南”，你能从产品卡直接点回 PDF 的具体页。以后建 WordPress 页面，还可以把已确认的素材交给 WP Build。

**[下载学员包](https://github.com/Miraclemin/product-asset-library/releases/download/v1.1.0/student-kit.zip)**　·　**[看可复制的提示词手册](docs/提示词手册.md)**　·　**[下载讲师演示卡](https://github.com/Miraclemin/product-asset-library/releases/download/v1.1.0/instructor.html)**

## 第一次用

1. **解压学员包。** 在已登录的 Codex 桌面版中，打开解压后的整个「产品素材库课堂」文件夹。学员包里已放好项目 Skill。第一次使用可以告诉 Codex：“请检查这个项目里的 product-asset-library 和 Python 3.9 或更新版本是否可用。”
2. **给原始资料。** 新开对话，将「01 客户素材」拖进输入框。这个目录里只有两份 PDF。复制下面这句话发送。

   > 用 product-asset-library 整理这个文件夹。逐份读 PDF，按产品型号建立资料卡。每个参数和适用型号都标出原文件和页码。完成后把能直接打开的知识库首页给我。

3. **打开结果。** 点 Codex 返回的「打开素材库.html」或产品卡。你应该看到 P25 和 P39。P25 卡写着点间距 **2.5 mm**，两张卡都引用 **installation.pdf**。点击依据，和 PDF 第 1 页对照。
4. **让 Codex 查一次。** 发：“P39 的安装指南是哪份？还有哪款也用它？给我原件链接。”预期答案是 **installation.pdf，适用于 P25 和 P39**。做到这里，你已经从零建好了可查询的知识库。

课堂练习只需 Codex、可读取 PDF 的本地环境和 Python 3.9+。学员用自然语言操作，索引脚本由 Codex 调用。若想在 Obsidian 中看卡片，选择“打开文件夹为仓库”，打开整个客户素材目录，再点素材库首页。

## 它能帮你做什么

| 你遇到的事 | 可以直接对 Codex 说 | 看哪份结果 |
|---|---|---|
| 一批来稿里照片、PDF 和表格混在一起 | “按画面和资料内容归类。找出完全重复的文件，保留各自的原路径。” | 素材总表、品类卡、重复项 |
| 想知道某个型号的参数或适用说明书 | “P25 点间距是多少？标出原文件和页码。” | 产品卡及可点击的出处 |
| 有照片，却不知道具体型号 | “先按看得出来的品类整理。把缺少型号依据的列在待确认里。” | 分类后的图片和需要补问的清单 |
| 销售补发一份规格书 | “只检查这份补件，更新它影响的产品，给我看新旧版次和审核状态。” | 更新后的产品卡、批次记录 |
| 想指定封面或查某张图的去向 | “登记 column.jpg 用于本机练习站 FLEX-DEMO 产品页封面。然后查它用在哪里。” | 素材、型号、网站页面和位置之间的用途索引 |
| 要把已确认的资料挂到网站 | “生成这款产品的上传清单，交给 WP Build 写到本机产品草稿，再打开验收。” | 上传清单、WordPress 草稿、附件编号 |

首次整理时，Codex 读取原件并建库。以后查已有用途可以直接读索引。已知变更文件时可以定向检查，发整个目录重新盘点时会枚举文件名，并利用元数据跳过未变化的内容。生成的主页、产品卡、总表和索引放在素材目录下的「素材库整理结果」里，原件留在原位置。

## 课堂怎么讲

先给学员看两份原始 PDF，再现场生成产品卡，让学员点出处核对答案。最后复制「02 课中补件」里的待审第三版，再看 P25 卡如何区分现行资料和待审稿。讲师演示卡附有 8 分钟的顺序、提问和核对点。[下载可离线打开的讲师演示卡](https://github.com/Miraclemin/product-asset-library/releases/download/v1.1.0/instructor.html)

## 在自己的项目使用

在学员项目里发这句话，之后新开一个素材整理对话，把你自己的文件夹地址发进去即可。

> 请把本项目 .agents/skills/product-asset-library 安装成我的个人 Codex Skill，保留 scripts 和 references。如果已有同名版本，先告诉我两版的差异。

从 GitHub 源码安装时，把上句中的路径换成 `skills/product-asset-library`。只有照片也可以开始整理。客户已有的产品表、说明书和交接单可以和图片放在同一目录，Codex 会自行查找。

## 怎样和 WP Build 一起用

先用素材库查清“哪个文件、属于哪个型号、放哪个位置”，生成上传清单。准备好已连接的本机 WordPress 练习站、支持所需字段的产品类型，以及能写入草稿的 WP Build / `wordpress-content`，再交给它上传、设置页面字段和预览。网站上的附件编号在这一步由 WordPress 分配。

另一个可跟做的案例用 AI 生成的圆柱屏和舞台屏示意图演示上传。FLEX-DEMO 实跑中新增了一个媒体附件，草稿预览里实际加载了同一张图。你自己操作时以自己站点返回的编号为准。[图片练习资料](examples/LED-来稿) · [WordPress 图文步骤](docs/从素材到WordPress草稿.md) · [下载图片教学包](https://github.com/Miraclemin/product-asset-library/releases/download/v1.0.1/product-asset-library-v1.0.1.zip) · [下载离线 HTML 演示](https://github.com/Miraclemin/product-asset-library/releases/download/v1.1.0/wordpress-tutorial.html)
