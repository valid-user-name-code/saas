# 数据 Schema

每行是 (customer_id, snapshot_month) 的组合，表示某客户在某个月初的状态。

## 主键

| 字段 | 类型 | 说明 |
|---|---|---|
| `customer_id` | int | 客户唯一标识 |
| `snapshot_month` | date (YYYY-MM-01) | 快照所属的月份（月初） |

## 客户画像（静态）

| 字段 | 类型 | 说明 |
|---|---|---|
| `industry` | str | 行业（saas, retail, finance, manufacturing, health, education, media, other） |
| `company_size` | str | 公司规模（SMB, MID, ENT） |
| `region` | str | 地区（NA, EU, APAC） |
| `signup_date` | date | 客户注册日期 |
| `months_since_signup` | int | 从注册到 snapshot_month 的月数 |
| `plan_tier` | str | 套餐档位（starter, pro, business, enterprise） |
| `contract_length_months` | int | 合同期长度（月） |
| `discount_pct` | float | 合同折扣比例（0~0.3） |
| `referral_source` | str | 客户来源（organic, paid, partner, referral） |
| `has_sso` | bool | 是否启用了 SSO |
| `has_premium_support` | bool | 是否购买了高级支持 |
| `has_custom_integration` | bool | 是否有定制集成 |

## 使用行为（snapshot 当月）

| 字段 | 类型 | 说明 |
|---|---|---|
| `mau` | int | Monthly Active Users，月活用户数 |
| `api_calls_30d` | int | 过去 30 天 API 调用次数 |
| `avg_session_min` | float | 过去 30 天平均会话时长（分钟） |
| `active_seats` | int | 当前活跃席位数 |
| `mau_trend_90d` | float | 过去 90 天 MAU 的相对变化（正=增长，负=下降） |

## 商务

| 字段 | 类型 | 说明 |
|---|---|---|
| `contract_value` | float | 当前合同年化金额（USD） |
| `days_since_last_payment` | int | 距上次成功付款的天数 |
| `payment_failures_90d` | int | 过去 90 天内的付款失败次数 |
| `billing_status` | str | 当前账单状态（current, past_due, dunning） |

## 客户成功

| 字段 | 类型 | 说明 |
|---|---|---|
| `support_tickets_30d` | int | 过去 30 天内提交的工单数 |
| `csm_touch_count_30d` | int | 过去 30 天内 CSM（客户成功经理）与该客户的接触次数 |
| `nps_last` | float | 最近一次 NPS 评分（0~10，可能为空） |
| `health_score` | float | 客户当前健康度评分（0~100，由内部模型给出） |
| `onboarding_score` | float | 客户在 onboarding 阶段的完成度评分（0~100） |
| `avg_response_time_hours` | float | 客户工单的平均响应时长（小时，可能为空） |

## 标签

| 字段 | 类型 | 说明 |
|---|---|---|
| `renewed_next_month` | int (0/1) | 该客户在 snapshot_month 的下个月是否续约。1=续约，0=流失。仅 train.csv 和 valid.csv 含此列。 |

---

## 数据规模

- `train.csv`：~12 万行
- `valid.csv`：~2 万行
- 类别比例：~80% 续约，~20% 流失
