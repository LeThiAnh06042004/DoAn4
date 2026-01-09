# Gửi prompt cho AI và nhận kq về

import requests #Gửi POST request đến LM Studio và nhận phản hồi JSON từ model

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions" #khai báo openAI api endpoint do lm cung cấp
MODEL_NAME = "local-model" #khai báo model đã load trong lm

#ĐN hàm: hàm nhận vào prompt (nội dung muốn ai xử lý) và trả về chuỗi text do AI sinh ra
def call_llm(prompt: str) -> str:
    #tạo payload gửi cho AI
    payload = {
        "model": MODEL_NAME, #chỉ định model sẽ xử lý request
        "messages": [
            {"role": "system", "content": "Bạn là Tester chuyên nghiệp"}, #đn persona cho AI, ép AI tư duy như 1 tester
            {"role": "user", "content": prompt} #nội dung động do test case truyền vào, vd như sinh keyword, ...
        ]
    }

    response = requests.post(LM_STUDIO_URL, json=payload) #gửi request đến AI (gửi HTTP POST)
    response.raise_for_status() #Nếu HTTP status ≠ 200 thì ném exception
    return response.json()["choices"][0]["message"]["content"] #parse kq AI trả về
