"""Chỉ mở khôi phục khi đã thoát phiên đang chạy."""
from BAO_CAO_CA import main
if __name__ == '__main__':
    main(['--restore', '--quiet'])
