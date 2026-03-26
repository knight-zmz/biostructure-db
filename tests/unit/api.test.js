const assert = require('assert');

describe('API Tests', () => {
  describe('GET /api/stats', () => {
    it('should return statistics', async () => {
      const http = require('http');
      const options = {
        hostname: 'localhost',
        port: 3000,
        path: '/api/stats',
        method: 'GET'
      };
      
      return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
          assert.strictEqual(res.statusCode, 200);
          let data = '';
          res.on('data', (chunk) => data += chunk);
          res.on('end', () => {
            const result = JSON.parse(data);
            assert.strictEqual(result.success, true);
            assert(result.data.hasOwnProperty('totalStructures'));
            resolve();
          });
        });
        req.on('error', reject);
        req.end();
      });
    });
  });
});
