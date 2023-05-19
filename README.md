改用 sentence transformer 库实现向量提取和搜索

打包指令
```shell
pyinstaller -w --collect-data torch --copy-metadata torch --collect-data transformers --copy-metadata transformers --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers main.py
```
