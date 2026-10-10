import MetaTrader5 as mt5

# 1. Khởi động kết nối với phần mềm MT5
if not mt5.initialize():
    print("Khởi động MT5 thất bại, lỗi:", mt5.last_error())
    quit()

# 2. Lấy toàn bộ thông tin tài khoản đang đăng nhập
account_info = mt5.account_info()

if account_info is None:
    print("Không thể lấy thông tin tài khoản, lỗi:", mt5.last_error())
else:
    # 3. Trích xuất thuộc tính balance từ đối tượng thông tin tài khoản
    balance = account_info.balance
    currency = account_info.currency
    
    print(f"Số dư tài khoản (Balance): {balance} {currency}")

# 4. Ngắt kết nối khi hoàn thành
mt5.shutdown()
