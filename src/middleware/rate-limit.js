/**
 * 简易内存速率限制器（无需 Redis）
 */
const requests = new Map();
const CLEANUP_INTERVAL = 60_000;

// 定期清理过期记录
setInterval(() => {
  const now = Date.now();
  for (const [key, data] of requests) {
    if (now - data.windowStart > data.windowMs) requests.delete(key);
  }
}, CLEANUP_INTERVAL).unref();

function rateLimit({ windowMs = 60_000, max = 60, keyFn } = {}) {
  return (req, res, next) => {
    const key = keyFn ? keyFn(req) : req.ip;
    const now = Date.now();
    let record = requests.get(key);

    if (!record || now - record.windowStart > windowMs) {
      record = { count: 0, windowStart: now, windowMs };
      requests.set(key, record);
    }

    record.count++;
    res.setHeader('X-RateLimit-Limit', max);
    res.setHeader('X-RateLimit-Remaining', Math.max(0, max - record.count));

    if (record.count > max) {
      return res.status(429).json({
        success: false,
        error: 'Too many requests. Please try again later.',
        retryAfter: Math.ceil((record.windowStart + windowMs - now) / 1000),
      });
    }
    next();
  };
}

module.exports = rateLimit;
