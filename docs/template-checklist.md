# Checklist trước khi viết `template.yaml` (AWS SAM)

> Cách dùng: copy file này cho dự án mới → điền cột **Dự án** → mỗi dòng đã điền sẽ thành 1 đoạn trong template.
> Cột **Lab** là ví dụ đã điền của `cicd-lab`. Dòng không áp dụng thì ghi `—` (đừng xoá, để biết là đã cân nhắc).
> ⚠️ Không ghi giá trị secret thật vào file này, chỉ ghi **tên** secret.

## 0. Sơ đồ request (vẽ trước tiên)
```
Lab:  Trình duyệt → CloudFront ─┬─ /*     → S3 (FE)
                                └─ /api/* → API Gateway (Prod) → Lambda
Dự án:
```

## 1. Kiến trúc
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Backend chạy ở đâu? (Lambda / ECS / EC2) | Lambda | | `AWS::Serverless::Function` |
| [ ] | Gọi backend qua đâu? (REST API GW / HTTP API / Function URL / ALB) | REST API Gateway | | `Events: Type: Api` |
| [ ] | FE host ở đâu? | S3 + CloudFront | | `AWS::S3::Bucket`, `AWS::CloudFront::Distribution` |
| [ ] | FE và API chung domain hay tách? | Chung (`/api/*`) | | `CacheBehaviors` |

## 2. Backend (Lambda)
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Runtime | `python3.12` | | `Runtime` |
| [ ] | Kiến trúc CPU (binary native hỗ trợ arm64 không?) | `x86_64` (mặc định) | | `Architectures` |
| [ ] | Thư mục code | `backend/` | | `CodeUri` |
| [ ] | Hàm được gọi | `lambda_function.lambda_handler` | | `Handler` |
| [ ] | Timeout (API GW chờ tối đa ~29s) | 10s | | `Timeout` |
| [ ] | RAM | 256 MB | | `MemorySize` |
| [ ] | Thư viện / file binary đặc biệt? | `native/hello` (mode `100755`) | | ảnh hưởng `sam build` |
| [ ] | Path + method | `/api/{proxy+}`, `ANY` | | `Events.*.Properties` |
| [ ] | Router tự viết hay mỗi path 1 Lambda? | Router tự viết (`api_route.py`) | | số lượng Function |

## 3. Môi trường và cấu hình
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Có mấy môi trường? | `stg`, `prd` | | `Parameters: Env` (`AllowedValues`) |
| [ ] | Các env khác nhau ở đâu? | Chỉ khác secret | | `${Env}` / `Conditions` |
| [ ] | Biến cấu hình thường (không bí mật) | `RUNTIME_ENV` | | `Environment.Variables` |
| [ ] | Biến **bí mật** (chỉ ghi tên) | `APP_MESSAGE` | | `{{resolve:secretsmanager:...}}` |
| [ ] | Tên secret theo env | `cicd-lab/<env>` | | tạo **trước** lần deploy đầu |
| [ ] | Region | `ap-northeast-1` | | `samconfig.toml` |
| [ ] | Tên stack theo env | `cicd-lab-<env>` | | `samconfig.toml` |

## 4. Mạng và bảo mật
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Bucket FE ai được đọc? | Chỉ CloudFront (OAC) | | `BucketPolicy`, `OriginAccessControl` |
| [ ] | Bắt buộc HTTPS? | Có | | `ViewerProtocolPolicy` |
| [ ] | Lambda cần gọi dịch vụ AWS nào? (S3, Secrets Manager, SES…) | Không | | `Policies` |
| [ ] | Lambda có phải vào VPC (DB riêng)? | Không | | `VpcConfig` (subnet, SG) |
| [ ] | Xác thực API? (Cognito / authorizer) | Không | | `Auth` |
| [ ] | WAF / giới hạn tốc độ? | Không | | `WebACLId`, throttling |
| [ ] | Domain riêng + chứng chỉ? | Không (`*.cloudfront.net`) | | `Aliases`, `ViewerCertificate` (ACM ở `us-east-1`) |

## 5. Cache (CloudFront)
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | File FE | Có cache (`CachingOptimized`) | | `DefaultCacheBehavior` |
| [ ] | API | Không cache (`CachingDisabled`) | | `CacheBehaviors: /api/*` |
| [ ] | Origin path tới API GW | `/Prod` | | `OriginPath` |
| [ ] | SPA: path lạ trả `index.html`? | Chưa cần | | `CustomErrorResponses` |

## 6. Vận hành
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Log giữ bao lâu? | Có giới hạn | | `AWS::Logs::LogGroup` (`RetentionInDays`) |
| [ ] | Alarm khi lỗi, báo đi đâu? | Không | | `AWS::CloudWatch::Alarm`, SNS |
| [ ] | Tag theo dõi chi phí | Không | | `Tags` |
| [ ] | Resource nào **không được xoá** khi xoá stack? (bucket dữ liệu…) | Không | | `DeletionPolicy: Retain` |

## 7. Output cho bước sau (script / CI)
| ✓ | Cần chốt | Lab | Dự án | Phần trong template |
|---|---|---|---|---|
| [ ] | Bước sau cần giá trị nào? | `FrontendBucket`, `DistributionId`, `SiteUrl`, `ApiUrl` | | `Outputs` |

## 8. Kiểm tra sau khi viết
- [ ] `sam validate --lint` không lỗi
- [ ] `sam build` + `sam local start-api` gọi được API
- [ ] Không ghi cứng region / account ID (dùng `${AWS::Region}`, `${AWS::AccountId}`)
- [ ] Không có secret thật trong template / git
- [ ] Đọc changeset trước khi gõ `y`, chú ý cột `Replacement`
- [ ] Deploy stg → kiểm tra cả `SiteUrl` và `ApiUrl`
