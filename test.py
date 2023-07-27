from sentence_transformers import SentenceTransformer, util
from PIL import Image

# 下载模型
model = SentenceTransformer('clip-ViT-B-32')

if __name__ == '__main__':
    print("下载模型")