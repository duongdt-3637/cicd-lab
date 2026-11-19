#!/usr/bin/env bash
# Deploy tay 1 môi trường: backend (SAM) + frontend (S3 + CloudFront).
# Dùng: export AWS_PROFILE=cicd-lab && bash scripts/deploy.sh stg   (hoặc prd)
# Phase 4–6 CI sẽ làm lại đúng các bước này, chỉ khác là chạy tự động.
set -euo pipefail # lỗi ở bất kỳ bước nào → dừng ngay, không deploy nửa vời

ENV="${1:-}"
REGION="ap-northeast-1"
STACK="cicd-lab-${ENV}"

# ---------- 0. Kiểm tra đầu vào ----------
if [[ "$ENV" != "stg" && "$ENV" != "prd" ]]; then
  echo "Dùng: bash scripts/deploy.sh <stg|prd>" >&2
  exit 1
fi

# Máy cá nhân: profile `default` là account khác → bắt buộc chọn profile.
# CI (CodeBuild / GitHub Actions) không cần, vì dùng role.
if [[ -z "${AWS_PROFILE:-}" && -z "${CI:-}" && -z "${CODEBUILD_BUILD_ID:-}" ]]; then
  echo "Chưa set AWS_PROFILE. Chạy: export AWS_PROFILE=cicd-lab" >&2
  exit 1
fi

cd "$(dirname "$0")/.." # luôn chạy từ thư mục gốc repo
START=$(date +%s)

echo "==> Account: $(aws sts get-caller-identity --query Account --output text) · Env: $ENV · Stack: $STACK"

# ---------- 1. Backend: build + deploy ----------
echo "==> [1/4] sam build + deploy"
sam build
sam deploy --config-env "$ENV" # cấu hình lấy từ samconfig.toml, mục [stg] / [prd]

# ---------- 2. Đọc Outputs của stack ----------
echo "==> [2/4] Đọc Outputs"
output() {
  aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}
BUCKET=$(output FrontendBucket)
DIST_ID=$(output DistributionId)
SITE_URL=$(output SiteUrl)

# ---------- 3. Frontend: build + upload ----------
echo "==> [3/4] Build FE + upload s3://$BUCKET"
(cd frontend && npm ci && npm run build)
aws s3 sync frontend/dist "s3://$BUCKET" --delete # --delete: xoá file cũ không còn trong dist/

# ---------- 4. Xoá cache CloudFront ----------
echo "==> [4/4] Invalidate CloudFront $DIST_ID"
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" \
  --query "Invalidation.Id" --output text

echo "==> Xong sau $(($(date +%s) - START))s · Mở: $SITE_URL"
