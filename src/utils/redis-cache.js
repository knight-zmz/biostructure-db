/**
 * Redis 缓存工具类
 * 用于缓存数据库查询结果，提高响应速度
 */

const Redis = require('ioredis');

class RedisCache {
  constructor() {
    this.client = null;
    this.enabled = false;
    this.defaultTTL = 300; // 5 分钟
  }

  /**
   * 初始化 Redis 连接
   */
  async connect() {
    try {
      this.client = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: process.env.REDIS_PORT || 6379,
        retryDelayOnFailover: 100,
        maxRetriesPerRequest: 3,
        lazyConnect: true
      });

      await this.client.connect();
      this.enabled = true;
      console.log('✅ Redis 缓存已启用');
    } catch (err) {
      console.warn('⚠️ Redis 连接失败，缓存功能已禁用:', err.message);
      this.enabled = false;
    }
  }

  /**
   * 从缓存获取数据
   * @param {string} key - 缓存键
   * @returns {Promise<any>} 缓存的数据，如果不存在则返回 null
   */
  async get(key) {
    if (!this.enabled || !this.client) {
      return null;
    }

    try {
      const data = await this.client.get(key);
      if (data) {
        return JSON.parse(data);
      }
      return null;
    } catch (err) {
      console.error('Redis GET error:', err.message);
      return null;
    }
  }

  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {any} value - 要缓存的数据
   * @param {number} ttl - 过期时间 (秒)，默认 300 秒
   */
  async set(key, value, ttl = this.defaultTTL) {
    if (!this.enabled || !this.client) {
      return false;
    }

    try {
      await this.client.setex(key, ttl, JSON.stringify(value));
      return true;
    } catch (err) {
      console.error('Redis SET error:', err.message);
      return false;
    }
  }

  /**
   * 删除缓存
   * @param {string} key - 缓存键
   */
  async del(key) {
    if (!this.enabled || !this.client) {
      return false;
    }

    try {
      await this.client.del(key);
      return true;
    } catch (err) {
      console.error('Redis DEL error:', err.message);
      return false;
    }
  }

  /**
   * 批量删除匹配模式的缓存
   * @param {string} pattern - 匹配模式，如 'structure:*'
   */
  async delPattern(pattern) {
    if (!this.enabled || !this.client) {
      return false;
    }

    try {
      const keys = await this.client.keys(pattern);
      if (keys.length > 0) {
        await this.client.del(...keys);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Redis DEL PATTERN error:', err.message);
      return false;
    }
  }

  /**
   * 获取或设置缓存 (带回调)
   * @param {string} key - 缓存键
   * @param {Function} fetchFn - 获取数据的函数 (当缓存未命中时调用)
   * @param {number} ttl - 过期时间 (秒)
   * @returns {Promise<any>}
   */
  async getOrSet(key, fetchFn, ttl = this.defaultTTL) {
    // 尝试从缓存获取
    const cached = await this.get(key);
    if (cached !== null) {
      return cached;
    }

    // 缓存未命中，执行 fetchFn
    const data = await fetchFn();
    
    // 存入缓存
    await this.set(key, data, ttl);
    
    return data;
  }

  /**
   * 获取缓存统计信息
   */
  async getStats() {
    if (!this.enabled || !this.client) {
      return { enabled: false };
    }

    try {
      const info = await this.client.info('stats');
      const memory = await this.client.info('memory');
      
      return {
        enabled: true,
        stats: info,
        memory: memory
      };
    } catch (err) {
      return { enabled: false, error: err.message };
    }
  }

  /**
   * 关闭连接
   */
  async disconnect() {
    if (this.client) {
      await this.client.quit();
      this.enabled = false;
      console.log('Redis 连接已关闭');
    }
  }
}

// 导出单例
const cache = new RedisCache();
module.exports = cache;
