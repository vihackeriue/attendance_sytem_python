class UserManager:
    # Lớp quản lý trạng thái người dùng
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
            cls._instance.user_id = None  # Không có user_id khi chưa đăng nhập
        return cls._instance

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def is_logged_in(self):
        return self.user_id is not None

    def logout(self):
        self.user_id = None  # Đăng xuất