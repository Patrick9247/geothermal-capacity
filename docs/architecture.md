# 架构说明

```
Vue 页面 → api/ → FastAPI 路由 → Service → Domain Model
                                  └→ Repository → SQLite
```

`app/domain` 是纯计算层，不引用 Web 框架或 ORM。新增计算方法时，在此层实现模型并由 `CalculationService` 调用；可按需要添加模型注册表与对应 API 路由。

热流量计算使用 `seuif97.pt2h(P, T)` 获取焓值（kJ/kg）：

- `Qw = W1 × hW(T1, P1) ÷ 1000`（MW）
- `Qs = W2 × hS(T2, P2) ÷ 1000`（MW）
- `Q总 = Qw + Qs`
