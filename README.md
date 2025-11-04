# 交易延迟监控脚本（含 Redis 缓存）

本项目用 Python 模拟上游交易查询（~800ms 延迟），并通过 Redis 缓存把读延迟降到 ~120ms 左右（命中缓存时基本是毫秒级）。

## 环境要求
- Python 3.10+
- 可选：本机 Redis（默认连接 `127.0.0.1:6379`，也可设置 `REDIS_URL`）

## 安装
```bash
pip install -r requirements.txt
```

## 运行（基准测试/监控）
- 启用缓存（默认启用，TTL 1s）：
```bash
python -m src.trade_monitor --symbol BTCUSDT --iterations 20 --use-cache --ttl 1
```
- 关闭缓存对比：
```bash
python -m src.trade_monitor --symbol BTCUSDT --iterations 5 --no-use-cache
```

## 配置 Redis
- 默认连接：`REDIS_HOST=127.0.0.1`，`REDIS_PORT=6379`
- 或使用 `REDIS_URL`：`export REDIS_URL=redis://127.0.0.1:6379/0`

> 如果没有 Redis，本脚本会自动退化为内存缓存（仅当前进程有效）。

## 结果示例
- 无缓存：平均 ~800ms
- 有缓存（TTL=1s，命中时）：平均 ~100-150ms，甚至更低

实际数值视机器性能而定。

## 目录
```
src/
  cache.py            # Redis/内存缓存封装
  mock_exchange.py    # 模拟上游接口，固定 ~800ms 延迟
  trade_monitor.py    # CLI：监控/基准测试
requirements.txt
```

