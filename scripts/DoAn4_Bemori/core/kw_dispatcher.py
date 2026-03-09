class KeywordDispatcher:
    def __init__(self, keyword_obj):
        self.keyword_obj = keyword_obj

    def execute(self, keyword: str, args: list = None):
        if args is None:
            args = []

        print(f"DEBUG: Gọi keyword '{keyword}' với args: {args}")

        if not hasattr(self.keyword_obj, keyword):
            raise Exception(f"Keyword không tồn tại: {keyword}. Kiểm tra tên method trong KWCommon.")

        method = getattr(self.keyword_obj, keyword)

        if not callable(method):
            raise TypeError(f"'{keyword}' không phải là method callable.")

        if not isinstance(args, list):
            raise TypeError("Args phải là list")

        try:
            result = method(*args)
            print(f"DEBUG: Kết quả '{keyword}': {result}")
            return result
        except Exception as e:
            print(f"ERROR trong '{keyword}': {str(e)}")
            raise