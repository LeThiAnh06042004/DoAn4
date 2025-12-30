from openai import OpenAI


client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content": "you are an code assistance editor. Your task is format this test script in the right way. And DO NOT change anything including comments and code"},
                    {"role":"user","content": "Viết cho tôi các dữ liệu để kiểm thử cho trường hợp đăng nhập với mật khẩu có 8 số và tên tài khoản có tối đa 20 số"}]
        )
result =  completion.choices[0].message.content

print(result)
