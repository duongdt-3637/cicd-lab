# Nhật ký học CI/CD

## Ngày 1 – 18/11 (`template.yaml`, `samconfig.toml`)
- **`template.yaml`**
  - Mục tiêu: mô tả toàn bộ hạ tầng AWS bằng file (Infrastructure as Code); `sam deploy` → CloudFormation tạo 1 stack.
  - Giải quyết: không phải bấm tay trên Console cho từng môi trường; có lịch sử thay đổi trong git.
  - Thành phần: Header (`Transform` bật SAM) · `Parameters` (Env stg / prd) · `Globals` (cài đặt chung) · `Resources` (tài nguyên) · `Outputs` (giá trị sau deploy).
  - Lưu ý: `!Ref` lấy giá trị, `!Sub` ghép chuỗi; `Globals` chỉ áp dụng cho `AWS::Serverless::*`; không ghi cứng region / account (dùng `AWS::Region`…).
- **`samconfig.toml`**
  - Mục tiêu: lưu sẵn cờ cho lệnh `sam` (chỉ SAM CLI đọc, AWS không đọc).
  - Giải quyết: thay lệnh deploy dài bằng `sam deploy --config-env stg`.
  - Thành phần: khối `[env.lệnh.parameters]` + các key = value (`stack_name`, `region`, `parameter_overrides`…).
  - Lưu ý: chỉ `env` đặt tự do; `lệnh` và key phải đúng cờ thật trong `sam <lệnh> --help` (bỏ `--`, `-` → `_`); key sai bị bỏ qua, không báo lỗi.
