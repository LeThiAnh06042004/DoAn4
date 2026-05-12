from sentence_transformers import SentenceTransformer #biến câu văn → vector số
from sklearn.metrics.pairwise import cosine_similarity #đo độ giống nhau giữa 2 vector


# load mô hình
# model này có khả năng hiểu nghĩa câu, không phụ thuộc từ khóa, hỗ trợ đa ngôn ngữ
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def semantic_score(text1, text2):

    # thiếu dữ liệu → không so sánh được → trả 0
    if not text1 or not text2:
        return 0.0

    # CHUYỂN TEXT → VECTOR
    emb1 = model.encode([text1])
    emb2 = model.encode([text2])

    # Tính COSINE SIMILARITY để đo góc giữa 2 vector
    # giống nhau: 1.0, gần giống: 0.5 - 0.8, khác: gần =0
    score = cosine_similarity(emb1, emb2)[0][0]

    return float(score)