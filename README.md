改用 sentence transformer 库实现向量提取和搜索

运行 main.py 文件即可

特征文件保存在 feature 文件夹

打包指令
```shell
pyinstaller -w --add-data "config.ini;." --copy-metadata pillow --collect-data torch --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers main.py
```

### BUG：

#### 问题一：

requests.exceptions.ConnectionError: (ProtocolError('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None)), '(Request ID: ae191776-0c4e-4470-8280-1fe1ff6e2b2c)')

是因为第一次启动程序需要下载模型，网络不通所致。

解决方法：

可以尝试启动 test.py 文件下载

或者

下载 Releases 中的 sentence-transformers_clip-ViT-B-32 压缩宝，解压至 C:\Users\你的用户名\.cache\torch\sentence_transformers 目录下即可

#### 问题二：
AttributeError: 'NoneType' object has no attribute 'flush'

解决方法：
https://github.com/huggingface/transformers/issues/24047

#### 问题三：
打包后报错找不到transformers文件

解决方法：
将transformers依赖文件夹复制到打包后的目录