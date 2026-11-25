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

## Ngày 2 – 19/11 (venv, lệnh SAM, chạy local)
- **Python venv (`source .venv/bin/activate`)**
  - Mục tiêu: bật môi trường Python riêng của project (giống `node_modules` bên Node).
  - Giải quyết: `pytest`, `black`, `flake8`… chỉ cài trong `.venv`, mỗi project giữ version thư viện riêng, không đụng nhau.
  - Cơ chế: đưa `.venv/bin` lên đầu `PATH` → `python` / `pip` / `pytest` dùng bản trong `.venv`; prompt hiện `(.venv)`.
  - Lưu ý: chỉ có hiệu lực ở terminal hiện tại, mở terminal mới phải chạy lại; tắt bằng `deactivate`; CI thường không cần (mỗi lần build là máy sạch).
- **`sam validate --lint`**
  - Mục tiêu: bắt lỗi template trước khi deploy (đỡ chờ AWS 5–15 phút rồi mới fail).
  - Input → Output: `template.yaml` → báo valid / danh sách lỗi kèm số dòng; không tạo file.
  - Cơ chế: dịch SAM sang CloudFormation thuần → chạy `cfn-lint` (tên resource, kiểu thuộc tính, `!Ref` / `!GetAtt`).
- **`sam build`**
  - Mục tiêu: đóng gói code thành bản sẵn sàng chạy trên Lambda (giống `npm run build` → `dist/`).
  - Input → Output: `template.yaml` + `backend/` + `requirements.txt` → `.aws-sam/build/` (template mới + code + thư viện).
  - Cơ chế: mỗi Function: copy source theo `CodeUri` → `pip install` vào cùng thư mục → viết lại template trỏ `CodeUri` sang bản build.
  - Lưu ý: `--use-container` build trong Docker giống Lambda (dự án thật dùng); lab / CodeBuild `standard:7.0` có sẵn Python 3.12 nên không cần.
- **`sam local start-api`**
  - Mục tiêu: test API giống môi trường thật, không tốn tiền, không cần AWS (giống `npm run dev`).
  - Input → Output: `.aws-sam/build/` + `env.local.json` + `Env=stg` → API ở `http://127.0.0.1:3000`, log in ra terminal.
  - Cơ chế: web server :3000 theo path trong template → HTTP đổi thành event API Gateway (`httpMethod`, `path`…) → chạy container Docker Lambda Python 3.12 → gọi `lambda_handler(event, context)` → `{statusCode, body}` đổi lại thành HTTP response.
  - Lưu ý: cần Docker đang chạy; chỉ giả lập Lambda + API Gateway, **không** có S3 / CloudFront / Secrets Manager → secret lấy từ `env.local.json`, FE dùng Vite proxy thay CloudFront.
- **`sam deploy --config-env stg`**
  - Mục tiêu: đưa app lên AWS. Đây là bước CI/CD sẽ tự động hoá.
  - Input → Output: `.aws-sam/build/` + mục `[stg]` trong `samconfig.toml` + quyền AWS → stack `cicd-lab-stg` + Outputs `ApiUrl`, `SiteUrl`, `FrontendBucket`, `DistributionId`.
  - Cơ chế: zip code → upload S3 (`resolve_s3`) → thay `CodeUri` bằng đường dẫn S3 → CloudFormation tạo changeset (diff) → xác nhận → tạo/sửa resource (lúc này mới đọc secret `{{resolve:secretsmanager:...}}`) → chờ xong.
  - Lưu ý (CI): `--no-confirm-changeset` (không có người bấm `y`) · `--no-fail-on-empty-changeset` (không đổi gì vẫn xanh).
- **Lệnh phụ**: `sam local invoke` (gọi Lambda 1 lần với event JSON) · `sam logs` (kéo log CloudWatch) · `sam delete` (xoá stack + resource; bucket phải rỗng).
- **Luồng**: `validate` → `build` → `local start-api` (Phase 2) / `deploy` (Phase 3 → CI/CD).
- **Lỗi gặp khi chạy local (Colima trên Mac chip M)**
  - `colima start` lỗi `attach disk ... in use by instance "colima"`: lần trước tắt đột ngột, còn sót khoá `~/.colima/_lima/_disks/colima/in_use_by` → `colima stop -f`, xoá symlink đó (không mất dữ liệu), `colima start`.
  - `sam` báo `requires a container runtime` dù `docker ps` chạy được: lệnh `docker` đọc **context** (colima), còn SAM chỉ đọc biến `DOCKER_HOST`, mặc định `/var/run/docker.sock` (trỏ Docker Desktop đang tắt) → `export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"` (thêm vào `~/.zshrc` để khỏi gõ lại).
  - `502` + `timed out` + `Lambda response must be valid json`: Lambda mặc định **x86_64**, VM Colima là **arm64**, `rosetta: false` → giả lập QEMU rất chậm, quá timeout → `colima stop && colima start --vz-rosetta`.
  - Bài học: lỗi local thường do **môi trường** (runtime, kiến trúc CPU), không phải code; CI (CodeBuild / GitHub Actions x86) sẽ không gặp các lỗi này. Cân nhắc `Architectures: [arm64]` (rẻ hơn ~20%) chỉ khi binary native hỗ trợ arm64.
- **Luồng local = luồng AWS**: Trình duyệt → Vite :5173 (vai CloudFront, proxy `/api/*`) → sam local :3000 (vai API Gateway) → Lambda (Docker).

## Ngày 4 – 23/11 (deploy tay vs CodeBuild, `buildspec.yml`)
- **Deploy tay (Phase 3) → CodeBuild (Phase 4)**
  - Ý chính: lệnh deploy gần như **không đổi** (`sam build` / `sam deploy` / `s3 sync` / invalidate); thứ đổi là **ai chạy, chạy ở đâu, quyền gì, chặn lỗi ở đâu**.
  - Luồng: `git push main` → GitHub webhook → CodeConnections → CodeBuild bật container sạch (`standard:7.0`, x86_64) → tải source → chạy `buildspec.yml` bằng **service role** → AWS; log → CloudWatch Logs.

    | Tiêu chí | Tay | CodeBuild |
    |---|---|---|
    | Kích hoạt | Gõ lệnh | Push `main` (webhook) / lịch (EventBridge) |
    | Nơi chạy | Mac (arm64, có sẵn venv) | Container sạch x86_64, dùng xong xoá |
    | Code | Thư mục máy, **kể cả chưa commit** | Chỉ code đã push |
    | Quyền | Access key IAM user (`AWS_PROFILE`) | Service role (key tạm, không lưu key) |
    | Kiểm tra | Không bắt buộc | `pre_build` bắt buộc |
    | Changeset | Bấm `y` | `--no-confirm-changeset` |
    | Log / lịch sử | Terminal, mất khi tắt | CloudWatch + build ID, commit, thời gian |
    | Chi phí | 0 | Theo phút build (free tier 100 phút/tháng) |

  - Thành phần mới ↔ tương ứng Phase 3: `buildspec.yml` ↔ `deploy.sh` · CodeConnections ↔ `git clone` · CodeBuild project ↔ Mac · service role ↔ IAM user + profile · webhook / EventBridge ↔ tự gõ lệnh.
  - Một câu: **Phase 4 = đem `deploy.sh` lên máy chung trên AWS, tự chạy khi push, thêm "cổng kiểm tra" trước deploy.**
- **`buildspec.yml`**
  - Mục tiêu: kịch bản CodeBuild chạy mỗi lần build (đặt ở gốc repo).
  - Thành phần: `version: 0.2` · `env.variables` (`ENV=stg`, ghi đè được ở project) · `phases`: `install` (cài công cụ) → `pre_build` (kiểm tra) → `build` → `post_build`.
  - Lưu ý: lệnh nào exit ≠ 0 → phase FAILED, build đỏ · `runtime-versions` chọn Python / Node có sẵn trong image · container sạch nên không cần venv · CI chỉ **kiểm tra** (`black --check`, `isort --check-only`), không tự sửa code.
  - pre-commit (local, bỏ qua được bằng `--no-verify`) ≠ `pre_build` (CI, ai push cũng phải qua) → CI là **chốt chặn cuối**.
- **Webhook**
  - Mục tiêu: khi có sự kiện (push), GitHub **tự gửi HTTP POST** báo cho CodeBuild → build tự chạy (giống event listener; ngược với polling / bấm tay Start build).
  - Lưu ý: chỉ **báo tin** (branch, commit SHA, người push), không mang code; CodeBuild tự tải source · **filter** quyết định có build không (`EVENT=PUSH`, `HEAD_REF=^refs/heads/main$`) · bật "Rebuild every time a code change is pushed" là AWS tự đăng ký với GitHub.
  - Webhook = theo **sự kiện**; EventBridge schedule = theo **thời gian**.
  - Tắt trước Phase 5: nếu không, 1 lần push → CodeBuild + CodePipeline cùng deploy 1 stack → xung đột (`UPDATE_IN_PROGRESS`).

## Ngày 5 – 24/11 (CodeConnections, service role CodeBuild)
- GitHub connection `cicd-lab-github` (CodeConnections): cho AWS đọc repo GitHub; dùng chung cho CodeBuild (Phase 4) + CodePipeline (Phase 5).
- Service role CodeBuild = "IAM user" của máy build, nhưng không có access key (key tạm). Policy riêng, giới hạn `cicd-lab-*`.
- Cách đọc policy / ARN, ý nghĩa từng `Sid`: xem `cicd/codebuild/README.md`.

## Ngày 5 – 24/11 (CodeConnections, service role CodeBuild)
- **GitHub connection (CodeConnections)**
  - Mục tiêu: cho AWS quyền đọc repo GitHub (thay cho `git clone` khi làm tay); CodeBuild (Phase 4) và CodePipeline (Phase 5) dùng chung.
  - Lưu ý: cài GitHub App **chỉ cho repo `cicd-lab`** · trạng thái `Pending` = chưa cài xong app → "Update pending connection" · tên service cũ là `codestar-connections` → policy ghi cả 2 tên cho chắc.
- **Service role** (`cicd-lab-codebuild-role`)
  - Mục tiêu: role mà CodeBuild "đóng vai" để gọi AWS; ứng với IAM user + `AWS_PROFILE` khi deploy tay; chỉ có **key tạm**, không lưu access key.
  - 2 phần của 1 role: **trust policy** (`codebuild.amazonaws.com`) = **ai** được đóng vai · **permission policy** (`cicd/codebuild/service-role-policy.json`) = **được làm gì**.
- **Cấu trúc 1 policy** (file JSON không có comment → ghi ở đây)

  | Thành phần | Ý nghĩa | Ví dụ |
  |---|---|---|
  | `Version` | Phiên bản cú pháp, luôn là `2012-10-17` | |
  | `Statement` | Danh sách các luật | |
  | `Sid` | Tên luật, chỉ để đọc cho dễ | `ReadAppSecret` |
  | `Effect` | `Allow` / `Deny` (Deny thắng Allow) | `Allow` |
  | `Action` | `service:HànhĐộng`; `*` = mọi hành động | `lambda:*`, `s3:PutObject` |
  | `Resource` | ARN tài nguyên áp dụng; `*` = tất cả | `...:function:cicd-lab-*` |
  | `Condition` | Điều kiện thêm (tuỳ chọn) | `iam:PassedToService = lambda.amazonaws.com` |

- **ARN** = "địa chỉ" của tài nguyên: `arn:aws:<service>:<region>:<account>:<loại>/<tên>`
  - S3 và IAM không có region: `arn:aws:s3:::bucket`, `arn:aws:iam::<account>:role/x` (S3 không có cả account).
  - Bucket cần 2 dòng: `bucket` (quyền với bucket, vd. list) và `bucket/*` (quyền với object, vd. put / get).
- **Từng `Sid` dùng cho bước nào**

  | Sid | Dùng khi | Giới hạn |
  |---|---|---|
  | `CodeBuildLogs` | CodeBuild ghi log build ra CloudWatch | `/aws/codebuild/cicd-lab*` |
  | `UseGitHubConnection` | Tải source từ GitHub | Đúng connection `cicd-lab-github` |
  | `CloudFormationStacks` | `sam deploy`: tạo / cập nhật stack, changeset | Stack `cicd-lab-*`, `aws-sam-cli-managed-default` |
  | `SamTransform` | Changeset chứa `Transform: AWS::Serverless` → CloudFormation đổi cú pháp SAM sang tài nguyên thường | Transform `Serverless-2016-10-31` |
  | `CloudFormationReadOnly` | SAM kiểm tra template | `*` (chỉ đọc) |
  | `S3Buckets` | Upload code Lambda (bucket của SAM) · tạo bucket FE · `s3 sync` | `aws-sam-cli-managed-default-*`, `cicd-lab-*` |
  | `LambdaFunctions` | Tạo / cập nhật Lambda | `function:cicd-lab-*` |
  | `IamRolesForLambda` | Tạo role cho Lambda (SAM tự sinh `AppFunctionRole`) | `role/cicd-lab-*` |
  | `PassRoleToLambdaOnly` | Gắn role đó vào Lambda | Chỉ được gắn cho Lambda |
  | `ApiGateway` | Tạo REST API, stage `Prod` | Không giới hạn theo tên được |
  | `CloudFront` | Distribution, OAC, `create-invalidation` | `*` (CloudFront không giới hạn theo tên được) |
  | `LambdaLogGroups`, `DescribeLogGroups` | Log group của Lambda, giữ log 7 ngày | `/aws/lambda/cicd-lab-*` |
  | `ReadAppSecret` | Resolve `{{resolve:secretsmanager:cicd-lab/<env>...}}` lúc deploy | `secret:cicd-lab/*` |

- **Lưu ý**
  - **Least privilege**: chỉ cấp đủ quyền cần dùng, giới hạn theo tên `cicd-lab-*` → role không đụng được tài nguyên khác trong account. Dịch vụ nào không giới hạn theo tên được thì đành dùng `*`.
  - `iam:PassRole` + `Condition` = chỉ được gắn role `cicd-lab-*` cho Lambda. Nếu không có điều kiện này, role có thể gắn một role mạnh hơn cho service khác → leo quyền.
  - CloudFormation resolve secret bằng **quyền của người gọi** `sam deploy` (ở đây là service role) → role phải có `GetSecretValue` (Phase 7 bỏ quyền này để xem lỗi).
  - Thiếu quyền → log báo `AccessDenied ... not authorized to perform: <action> on resource: <arn>` → thêm **đúng action đó** vào policy, không cấp Admin cho nhanh.
  - Policy có account ID mà repo là public: account ID không phải secret, nhưng vẫn nên hạn chế công khai.
- **Lỗi build #1: `pyenv: version '3.12.12' is not installed`** (phase INSTALL, lệnh `pip install`)
  - Đọc log: dòng `COMMAND_EXECUTION_ERROR` chỉ là tóm tắt → nguyên nhân thật nằm **ngay phía trên** nó.
  - Nguyên nhân: `.python-version` (`3.12.12`, cấu hình pyenv của máy dev) đã commit vào repo. Image CodeBuild cũng dùng pyenv → đọc file này → đòi đúng bản `3.12.12`, mà image chỉ có một bản 3.12.x khác.
  - Sửa: trong `buildspec.yml`, `rm -f .python-version` trước `pip install` (chỉ xoá trong container, máy dev vẫn giữ) → dùng Python do `runtime-versions` chọn.
  - Bài học: **cấu hình riêng của máy dev lọt vào CI** là lỗi rất hay gặp. Chạy được ở máy ≠ chạy được trên CI → đây chính là lý do cần CI.
- **Lỗi build #2: `AccessDenied ... cloudformation:CreateChangeSet`** (phase BUILD, lúc `sam deploy`)
  - Đọc lỗi theo 3 ý: **ai** (`assumed-role/<tên role>`) · **làm gì** (action) · **trên cái gì** (resource).
  - Lần này sai ở **ai**: role là `codebuild-cicd-lab-stg-service-role`, do CodeBuild **tự tạo** vì lúc tạo project để *New service role*. Role này chỉ có quyền tối thiểu (log, source). Role mình tạo là `cicd-lab-codebuild-role`, policy đã có sẵn quyền này.
  - Sửa: project → Edit → Environment → *Existing service role* → `cicd-lab-codebuild-role`, bỏ tick "Allow AWS CodeBuild to modify this service role" → build lại → **Succeeded**. Không sửa file policy.
  - Bài học: gặp `AccessDenied` thì **kiểm tra đúng role trước**, sau đó mới thêm quyền. Thêm quyền vào nhầm role thì lỗi không hết, còn làm role thừa mở rộng quyền.
  - Dọn sau (Phase 9 hoặc lúc tiện): xoá role thừa `codebuild-cicd-lab-stg-service-role` + policy `CodeBuildBasePolicy-cicd-lab-stg-...`.
- **Build xanh nhưng chỉ S3 có "Last modified" mới, vì sao?** `sam deploy` chỉ cập nhật phần **có thay đổi**.
  - Template và code giống Phase 3 → change set rỗng (`No changes to deploy`) → Lambda, API GW, cấu hình CloudFront giữ nguyên. Nhờ `--no-fail-on-empty-changeset` nên build không đỏ.
  - FE thì `npm run build` tạo file mới trong container → `s3 sync` upload lại → S3 đổi ngày. CloudFront có thêm 1 dòng trong tab Invalidations.
  - **Idempotent**: chạy lại bao nhiêu lần, kết quả vẫn như nhau. Ví von: thợ so bản vẽ với nhà thật, giống thì không làm gì.
  - Kiểm chứng: log build có `No changes to deploy` · CloudFormation Events không có sự kiện mới. Muốn Lambda đổi thì phải sửa code backend / template rồi deploy.
