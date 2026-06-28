# Contributing

Cảm ơn bạn quan tâm đóng góp cho `samvnstock`!

## Quy trình

1. Fork repo, tạo branch từ `main`: `git checkout -b feat/ten-tinh-nang`.
2. Cài đặt môi trường dev:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
3. Viết code + test (mục tiêu coverage ≥ 80%).
4. Chạy kiểm tra trước khi commit:
   ```bash
   ruff check .
   mypy src
   pytest
   ```
5. Commit theo [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`, `ci:`.
6. Mở Pull Request, mô tả rõ thay đổi + test plan.

## Thêm nguồn dữ liệu mới (provider)

- Tạo thư mục mới trong `src/samvnstock/providers/<ten_nguon>/`.
- Triển khai các interface trừu tượng định nghĩa trong `providers/base.py`.
- Không sửa code trong `api/` — lớp facade chỉ gọi qua registry.
- Đảm bảo dữ liệu trả về đi qua `core/normalize.py` để chuẩn hoá schema.

## Quy tắc test mạng

- Test mock HTTP (dùng `respx`) chạy trong CI bình thường.
- Test gọi API thật phải đánh dấu `@pytest.mark.network` — không chạy trong CI,
  chỉ chạy thủ công hoặc qua cron riêng.

## Báo lỗi / đề xuất tính năng

Dùng issue templates trong `.github/ISSUE_TEMPLATE/`.
