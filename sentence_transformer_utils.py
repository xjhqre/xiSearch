import glob
import os
import pickle
import time

import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util

import config

torch.set_num_threads(4)

model = SentenceTransformer('clip-ViT-B-32')


# 存储张量
def dump(img_names, img_emb):
    with open(config.feature_path + str(int(time.time())) + ".pickle", 'wb') as fOut:
        pickle.dump((img_names, img_emb), fOut)


# 提取特征方法
def extract(message_signal):
    # 错误图片列表
    error_img = []
    time_start = time.time()  # 记录开始时间
    img_names = list(glob.glob(config.gallery_path + "/*"))
    # 过滤掉其他文件
    img_names = [name for name in img_names if os.path.splitext(name)[1] in config.allow_types]

    message_signal.emit("开始提取图片特征\n")

    img_emb = None
    img_path_list = []
    cnt = 1
    for filepath in img_names:
        try:
            img = Image.open(filepath)
            emb = model.encode([img], batch_size=1, convert_to_tensor=True, show_progress_bar=False)
            img.close()

            img_path_list.append(filepath)
            if img_emb is None:
                img_emb = emb
            else:
                img_emb = torch.concat((img_emb, emb), dim=0)

            # 每 1024 个维度存储一次
            if cnt % 1024 == 0:
                dump(img_path_list, img_emb)
                img_path_list.clear()
                img_emb = None
            message_signal.emit("当前图片：" + filepath + " - " + str(cnt) + "\n")
            cnt += 1
        except Exception as e:
            # 图片打开失败
            # print(e)
            error_img.append(filepath)
            img_names.remove(filepath)

    # 存储剩余维度
    dump(img_path_list, img_emb)

    time_end = time.time()  # 记录结束时间
    time_sum = time_end - time_start
    message_signal.emit("提取特征耗时：" + str(time_sum) + " 秒\n")

    if error_img:
        message_signal.emit("提取失败图片:\n")
        for path in error_img:
            message_signal.emit(path + "\n")


# 搜索图片
def search(query, k=30):
    if not os.path.exists(config.feature_path):
        print("没有特征文件")
        return

    img_names = []
    img_emb = None
    feature_list = list(glob.glob(config.feature_path + "*"))
    for feature_path in feature_list:
        with open(feature_path, 'rb') as fIn:
            names, emb = pickle.load(fIn)
            img_names.extend(names)
            if img_emb is None:
                img_emb = emb
            else:
                img_emb = torch.concat((img_emb, emb), dim=0)

    img = Image.open(query)
    query_emb = model.encode([img], convert_to_tensor=True, show_progress_bar=False)
    img.close()

    hits = util.semantic_search(query_emb, img_emb, top_k=k)[0]

    return [img_names[hit['corpus_id']] for hit in hits]
