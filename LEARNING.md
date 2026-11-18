# Nhật ký học CI/CD

## Ngày 1 – 18/11 (`template.yaml`, `samconfig.toml`, Budget, IAM)
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
- **AWS Budget**
  - Mục tiêu: cảnh báo qua email khi chi phí account sắp / đã vượt ngưỡng ($5/tháng).
  - Giải quyết: phát hiện sớm tài nguyên quên xoá, key bị lộ, chi phí bất thường.
  - Thành phần: loại (cost / usage / Savings Plans), kỳ (monthly / daily), ngưỡng (thực tế 85%, 100% · dự báo 100%), scope (cả account hoặc lọc theo service / tag), email nhận.
  - Lưu ý: chỉ cảnh báo, **không tự chặn**; tên không đổi được sau khi tạo; account riêng → theo dõi toàn bộ account; 2 budget đầu miễn phí.
- **IAM**
  - Mục tiêu: tạo danh tính riêng (`cicd-lab-admin`) để làm việc hằng ngày, không dùng root.
  - Giải quyết: root có toàn quyền và không giới hạn được → lộ root là mất account; IAM user giới hạn được quyền, có MFA, xoá được.
  - Thành phần: user / group / role / policy (identity-based gắn vào người, resource-based gắn vào tài nguyên); cấp quyền qua group (best practice), copy, hoặc attach trực tiếp; MFA; access key (cho CLI).
  - Lưu ý: IAM user không có email, dùng chung Account ID với root; least privilege; Deny luôn thắng Allow; group không lồng nhau; access key + mật khẩu chỉ hiện 1 lần; dịch vụ AWS / CI dùng **role**, không dùng access key.
