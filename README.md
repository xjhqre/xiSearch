改用 sentence transformer 库实现向量提取和搜索

运行 main.py 文件即可

打包指令
```shell
pyinstaller -w --collect-data torch --copy-metadata torch --collect-data transformers --copy-metadata transformers --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers main.py
```

### 若启动程序遇到报错：

requests.exceptions.ConnectionError: (ProtocolError('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None)), '(Request ID: ae191776-0c4e-4470-8280-1fe1ff6e2b2c)')

是因为第一次启动程序需要下载模型，网络不通所致。

### 解决方法：

可以尝试启动 test.py 文件下载

或者

下载 Releases 中的 sentence-transformers_clip-ViT-B-32 压缩宝，解压至 C:\Users\你的用户名\.cache\torch\sentence_transformers 目录下即可