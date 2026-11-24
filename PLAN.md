# CI/CD Lab – Checklist

> Học CI/CD trên **AWS account cá nhân** với khung code giống `fresco2-tesac-fraroms`.
> Thư mục: `/Users/dothuyduong/Documents/JAFIC/cicd-lab/` (ngang hàng repo dự án, `git init` riêng).
> File này được lưu thành `cicd-lab/PLAN.md`; làm lần lượt từng mục, mỗi lần update có thể chia nhỏ thêm.
> Không dùng secret / key / ID nào của dự án thật. Claude chỉ tạo code + chạy kiểm tra local; mọi thao tác AWS do bạn tự làm.

Ký hiệu: `[ ]` chưa làm · `[x]` xong · 👤 bạn làm · 🤖 Claude làm

## Lịch dự kiến – xong trong tháng 11/2026 (mỗi ngày 2–3 tiếng)

| Ngày | Phase | Việc chính |
|---|---|---|
| T4 18/11 | 0 + 1 | 👤 làm Phase 0 · 🤖 dựng khung code song song |
| T5 19/11 | 2 + 3 | Chạy local · tạo secret · viết `deploy.sh` |
| T6 20/11 | 3 | Deploy tay stg, mở SiteUrl chạy được |
| T2 23/11 | 4 | ② CodeBuild + webhook + EventBridge schedule |
| T3 24/11 | 5 | ① Pipeline: Source → Build → Deploy stg |
| T4 25/11 | 5 + 6 | Manual approval → prd · tạo OIDC provider + role |
| T5 26/11 | 6 | ③ GitHub Actions: `ci.yml`, `deploy.yml`, Environment `prd` |
| T6 27/11 | 7 | Cố ý làm hỏng (4 tình huống) |
| T2 30/11 | 8 + 9 | Bảng so sánh, chọn hướng · dọn dẹp AWS |

- **9 buổi**; cuối tuần 21–22/11 và 28–29/11 để **dự phòng** khi bị chậm.
- Bỏ để kịp: EventBridge S3 (Phase 4), thử rollback (Phase 5). Nếu dư thời gian thì làm lại.
- Mỗi buổi dành ~10 phút ghi "hôm nay hiểu gì / còn mù mờ gì" vào `LEARNING.md` → dùng cho Phase 8.

---|---|---|---|
| 0 | Chuẩn bị account, công cụ, repo | 1 ngày | 1 |
| 1 | Khung code (🤖 tạo, 👤 đọc hiểu) | 1 ngày | 2 |
| 2 | Chạy local | 1 ngày | 3 |
| 3 | Deploy tay (CloudFront tạo lần đầu ~15 phút, hay phải sửa lỗi) | 2 ngày | 5 |
| 4 | ② CodeBuild + EventBridge | 2 ngày | 7 |
| 5 | ① CodePipeline + CodeBuild | 2 ngày | 9 |
| 6 | ③ GitHub Actions + OIDC | 2 ngày | 11 |
| 7 | Cố ý làm hỏng | 1 ngày | 12 |
| 8 + 9 | Tổng kết + dọn dẹp | 1 ngày | 13 |

- **Tổng: ~13 ngày học ≈ 3 tuần** (5 ngày/tuần). Tính thêm ~20% dự phòng (lỗi IAM, chờ deploy) → **3–4 tuần**.
- Mốc kiểm tra: hết **tuần 1** xong Phase 3 (deploy tay chạy được) · hết **tuần 2** xong Phase 5 · hết **tuần 3** xong Phase 7.
- Chậm hơn 2 ngày so với mốc → báo Claude để chia nhỏ / bỏ bớt mục tuỳ chọn (vd. EventBridge S3, rollback ở Phase 5).

---

## Phase 0 – Chuẩn bị
- [x] 🤖 Tạo thư mục `cicd-lab/`, `git init`, lưu `PLAN.md` (file này)
- [x] 👤 AWS account cá nhân + bật MFA root
- [x] 👤 Tạo IAM user `cicd-lab-admin` + access key (CLI)
- [x] 👤 Tạo AWS Budget báo động $5
- [x] 👤 Cấu hình AWS CLI profile `cicd-lab` (`aws sts get-caller-identity --profile cicd-lab`)
  - Mỗi terminal làm lab: `export AWS_PROFILE=cicd-lab` (profile `default` = account khác!)
- [x] 👤 Cài / kiểm tra: SAM CLI, Python 3.12, Node 20, Git
- [x] 👤 Tạo repo GitHub cá nhân `cicd-lab` (public để dùng miễn phí Environment reviewer ở Phase 6)

## Phase 1 – Khung code (giống dự án) – dựng từng bước, mỗi bước giải thích rồi chờ "tiếp"
> Bản làm sẵn để tham khảo: nhánh `phase1-ref` (`git diff main phase1-ref`)
- [x] 1.1 🤖 Backend lõi: `lambda_function.py`, `api_route.py`, `api/common/health_check.py`, `conf/`, `error/`, `logger/`
- [x] 1.2 🤖 API `hello` + `native/hello` (script cần quyền chạy – mô phỏng `native/tesac`, mode `100755`)
- [x] 1.3 🤖 Test `backend/tests/` (route, handler, quyền chạy) + lint (black / isort / flake8, `.pre-commit-config.yaml`)
- [x] 1.4 🤖 `template.yaml` (Function + REST Api + S3 + CloudFront OAC, secret từ Secrets Manager) + `samconfig.toml`
- [x] 1.5 🤖 Frontend Vue 3 + Vite: màn gọi `/api/hello`, `VITE_API_BASE_URL=/api/`
- [x] 1.6 🤖 Kiểm tra local (`pytest`, `sam validate --lint`, `npm run build`, grep) → 👤 tự commit

## Phase 2 – Chạy local
- [x] 👤 `pytest backend/tests`
- [x] 👤 `sam build` → `sam local start-api` → gọi `http://127.0.0.1:3000/api/hello`
  - Colima: cần `export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"` + `colima start --vz-rosetta` (xem LEARNING Ngày 2)
- [x] 👤 `npm run dev` ở `frontend/`

## Phase 3 – Deploy tay (baseline)
- [x] 👤 Tạo secret `cicd-lab/stg`, `cicd-lab/prd` trong Secrets Manager
- [x] 🤖 `scripts/deploy.sh <env>`: sam build/deploy → đọc Outputs → build FE → `s3 sync` → invalidate CloudFront
- [x] 👤 `bash scripts/deploy.sh stg` → mở SiteUrl, kiểm tra `/api/hello`
- [x] 👤 Ghi lại các bước tay / thời gian (để so sánh khi có CI/CD)

## Phase 4 – Hướng ② CodeBuild (+ EventBridge)
- [x] 🤖 `buildspec.yml`: lint → pytest → `test -x native/hello` → sam build/deploy → FE sync → invalidate (biến `ENV`)
- [x] 👤 Tạo GitHub connection (CodeConnections) – `cicd-lab-github`
- [x] 👤 Tạo project CodeBuild `cicd-lab-stg` (image `standard:7.0`, `ENV=stg`) + service role `cicd-lab-codebuild-role`
- [ ] 👤 Bật webhook PUSH `main` → push thử → xem log CloudWatch
- [ ] 👤 EventBridge rule (schedule) → StartBuild
- [ ] 👤 (Tuỳ chọn – bỏ nếu thiếu giờ) EventBridge rule S3 Object Created → StartBuild
- [ ] 👤 Tắt webhook + rule trước khi sang Phase 5

## Phase 5 – Hướng ① CodePipeline + CodeBuild
- [ ] 🤖 `cicd/pipeline/buildspec-build.yml` (test + `sam package` + `dist` làm artifact), `buildspec-deploy.yml` (deploy theo `ENV`)
- [ ] 👤 Tạo 2 project CodeBuild: `cicd-lab-build`, `cicd-lab-deploy`
- [ ] 👤 Tạo pipeline V2: Source (GitHub) → Build → Deploy stg → Manual approval → Deploy prd
- [ ] 👤 Chạy thử, duyệt prd
- [ ] 👤 (Tuỳ chọn – bỏ nếu thiếu giờ) Thử rollback (chạy lại execution cũ)
- [ ] 👤 Tắt pipeline trước khi sang Phase 6

## Phase 6 – Hướng ③ GitHub Actions + OIDC
- [ ] 👤 Tạo OIDC provider `token.actions.githubusercontent.com` (audience `sts.amazonaws.com`)
- [ ] 👤 Tạo IAM role, trust giới hạn `repo:<user>/cicd-lab:ref:refs/heads/main` và `repo:<user>/cicd-lab:environment:prd`
- [ ] 🤖 `.github/workflows/ci.yml` (PR: lint, test, sam validate, build FE – không cần AWS)
- [ ] 🤖 `.github/workflows/deploy.yml` (main: stg → prd qua Environment `prd`)
- [ ] 👤 Tạo Environment `prd` + required reviewer, lưu role ARN vào repo variables
- [ ] 👤 Mở PR thử → merge → duyệt prd

## Phase 7 – Cố ý làm hỏng
- [ ] 👤 `chmod 644 native/hello` + commit → CI phải đỏ
- [ ] 👤 Viết 1 test fail → không deploy
- [ ] 👤 Gỡ quyền Secrets Manager khỏi role → đọc lỗi `AccessDenied`
- [ ] 👤 Chạy workflow OIDC từ nhánh khác → bị từ chối

## Phase 8 – Tổng kết
- [ ] 👤 Điền bảng so sánh ②/①/③: thời gian dựng, thời gian chạy, chi phí, độ dễ đọc log, cách duyệt prd
- [ ] 👤 Chọn hướng đề xuất cho dự án thật

## Phase 9 – Dọn dẹp
- [ ] 👤 `sam delete` stack stg / prd (và `aws-sam-cli-managed-default` nếu không dùng nữa)
- [ ] 👤 Xoá pipeline, project CodeBuild, EventBridge rule, connection
- [ ] 👤 Xoá OIDC provider, IAM role, secret
- [ ] 👤 Kiểm tra Billing không còn phát sinh

---
### Phụ lục (không thuộc lab): plan A8 đang hoãn
Xoá logic CSV cũ của FISID ở cả `JustFRAROMS/` + `hasTesacFRAROMS/`, mọi năm (`backend/common/s3_util.py`).
