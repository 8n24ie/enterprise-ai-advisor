# 可选案例原文接入

公开版不分发《Datawhale FDE案例100》PDF或其全文提取缓存。核心需求诊断、试点设计与项目续接无需这些文件。

## 使用已有的合法资料

请从作者或获授权渠道取得资料，并确认允许在当前 AI 环境使用。项目不提供第三方下载镜像。若你没有原文，直接进行业务咨询即可；技能会说明案例原文未核实。

本项目的页码索引针对246页、24案版本。`source-manifest.json` 只含版本哈希、页数及案例定位元数据，不含正文。

将该版本保存在本技能的 `references/source.pdf`，或者指定任意本地路径：

```text
python scripts/case_source.py --info --pdf "你的文件.pdf"
python scripts/case_source.py --search "预计" --case 6 --pdf "你的文件.pdf"
python scripts/case_source.py --pages 61-62 --pdf "你的文件.pdf"
```

从技能目录运行。搜索与读页需要 Python 和 pypdf；检查版本只需 Python 标准库。没有 pypdf 时可自行选择安装，或使用已有 PDF 阅读工具。脚本不会联网、上传、安装软件或写入缓存。

版本哈希不符时脚本停止：不要将本项目页码套到其他版本，也不要仅改哈希绕过校验；应重新核对索引。扫描页与图表需视觉核对。

`.gitignore` 排除了PDF、全文缓存及ZIP；请勿把用户资料提交到公开仓库。
