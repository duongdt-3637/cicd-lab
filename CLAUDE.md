# cicd-lab – bối cảnh

## Mục đích
Lab cá nhân để **học CI/CD** trên AWS account cá nhân, với khung code giống dự án thật `../fresco2-tesac-fraroms`.
Học xong sẽ chọn hướng CI/CD đề xuất cho dự án thật. Tiến độ theo dõi trong `PLAN.md` (checklist).

## Người dùng
- FE dev, mới học infra, trao đổi bằng tiếng Việt.
- Thích câu trả lời ngắn, dễ hiểu, có ví dụ; dùng bảng / checklist.
- Làm **từng bước một**: xong 1 phase → báo lại → chờ người dùng nói tiếp. Đánh `[x]` trong `PLAN.md` khi xong; có thể chia nhỏ mục.
- Ký hiệu trong PLAN: 🤖 Claude làm · 👤 người dùng làm.

## Quy tắc an toàn
- **Không** dùng bất kỳ secret / key / ID / tên bucket nào của dự án thật (Oracle, Cognito, SMTP, subnet, SG, bucket `jafic-*`…).
- Claude chỉ tạo code + chạy kiểm tra local. **Mọi thao tác lên AWS do người dùng tự chạy.**
- Không push repo đi đâu khi người dùng chưa yêu cầu.

## Dự án thật (để mô phỏng)
- Backend: AWS SAM, 1 Lambda Python 3.12 (`backend/lambda_function.py` → router tự viết `api_route.py` theo `httpMethod`/`path` của REST API Gateway), log JSON ra stdout → CloudWatch.
- `backend/native/tesac`: binary gọi bằng subprocess, **cần quyền chạy** — từng bị lỗi `PermissionError` trên Lambda vì trong git là `100644`.
- Frontend: Vue 3 + Vite (`build:stg` / `build:prd`), host trên S3 + CloudFront; `/api/*` đi qua CloudFront tới API Gateway.
- Hiện trạng deploy: repo trên **CodeCommit**, deploy tay bằng `scripts/deploy-stg.sh` (`sam build --use-container` + `sam deploy` truyền toàn bộ `--parameter-overrides`), secret nằm ở file trên máy cá nhân, FE build + upload S3 tay, chưa có unit test, có `.pre-commit-config.yaml` (black / isort / flake8) nhưng chỉ chạy local.

## Đã thống nhất
- **CI/CD tối thiểu trước, unit test sau** (viết test dần khi sửa bug, gắn `pytest` vào CI).
- Trước khi làm CI/CD cho dự án thật cần: sửa quyền chạy file binary trong git; chuyển secret sang Secrets Manager (`{{resolve:secretsmanager:...}}` trong template).
- So sánh hướng: ② chỉ CodeBuild (đơn giản, rẻ) → ① CodePipeline + CodeBuild (có Manual approval cho prd) → ③ GitHub Actions + OIDC (dễ dùng nhất nhưng phải chuyển repo sang GitHub). Không chọn Jenkins / deploy tay lâu dài.
- Thứ tự học trong lab: ② → ① → ③. Account mới không tạo được CodeCommit → cả 3 hướng dùng **GitHub** làm source (AWS nối qua CodeConnections).

## Thiết kế lab (Phase 1)
- `template.yaml`: Function + REST Api `/api/{proxy+}` + S3 bucket FE + CloudFront (OAC; `/api/*` → API GW, origin path `/Prod`); secret từ Secrets Manager `cicd-lab/<env>`; Outputs: `ApiUrl`, `SiteUrl`, `FrontendBucket`, `DistributionId`.
- FE gọi `VITE_API_BASE_URL=/api/` (cùng domain CloudFront) → 1 bản build dùng cho mọi env.
- `backend/native/hello`: script mô phỏng `native/tesac`, commit với mode `100755`.
- CI dùng `sam build` (không container, image CodeBuild `standard:7.0` đã có Python 3.12) và `sam deploy --no-confirm-changeset --no-fail-on-empty-changeset`.
- OIDC: job có `environment:` thì claim `sub` đổi thành `repo:<user>/cicd-lab:environment:<env>` — trust policy phải cho cả dạng này.

## Bước tiếp theo
Phase 0 (👤): AWS account + MFA, Budget $5, CLI profile `cicd-lab`, cài SAM CLI / Python 3.12 / Node 20, tạo repo GitHub `cicd-lab` (public).
Phase 1 (🤖): dựng khung code — làm khi người dùng nói "tiếp Phase 1".
