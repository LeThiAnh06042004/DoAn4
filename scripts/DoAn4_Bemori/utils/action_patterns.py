# “từ điển keyword” cho module extract_action()
# Mỗi automation keyword sẽ có danh sách pattern nhận diện

ACTION_PATTERNS = {

    "INPUT_TEXT": [
        "nhập",
        "điền",
        "gõ",
        "type",
        "enter",
        "fill"
    ],

    "CLICK": [
        "click",
        "nhấn",
        "bấm",
        "tap",
        "truy cập",
        "chuyển tới",
        "điều hướng",
        "đi đến",
        "vào trang chi tiết",
        "mở sản phẩm"
    ],

    "DOUBLE_CLICK": [
        "double click",
        "nhấp đúp"
    ],

    "RIGHT_CLICK": [
        "right click",
        "chuột phải"
    ],

    "HOVER": [
        "hover",
        "di chuột"
    ],

    "CLEAR_TEXT": [
        "xóa",
        "clear"
    ],

    "PRESS_ENTER": [
        "nhấn enter",
        "press enter"
    ],

    "SELECT_BY_TEXT": [
        "chọn",
        "select"
    ],

    "CHECK_CHECKBOX": [
        "tick",
        "check checkbox"
    ],

    "UNCHECK_CHECKBOX": [
        "bỏ tick",
        "uncheck"
    ],


    "VERIFY_TEXT_CONTAINS": [
        "chứa",
        "contains",
        "có chứa",
        "bao gồm",
        "message contains"
    ],


    "VERIFY_ELEMENT_TEXT_EQUALS": [
        "hiển thị thông báo",
        "kiểm tra thông báo",
        "kiểm tra nội dung",
        "hiển thị nội dung",
        "thông báo",
        "nội dung",
        "hiển thị chính xác",
        "hiển thị đúng",
        "thông báo chính xác",
        "kiểm tra chính xác",
        "kiểm tra đúng nội dung",
        "verify text",
        "verify message",
        "verify exact text",
        "verify exact message",
        "exact text",
        "exact message"
    ],

    "VERIFY_ELEMENT_VISIBLE": [
        "kiểm tra hiển thị",
        "verify visible",
        "hiển thị",
        "xuất hiện"
    ],

    "VERIFY_ELEMENT_PRESENT": [
        "kiểm tra tồn tại",
        "verify exists"
    ],

    "WAIT_FOR_ELEMENT_VISIBLE": [
        "chờ hiển thị",
        "wait visible"
    ],

    "WAIT_FOR_ELEMENT_CLICKABLE": [
        "chờ click được",
        "wait clickable"
    ]
}