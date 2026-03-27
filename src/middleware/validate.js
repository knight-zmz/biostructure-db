/**
 * 输入验证中间件
 */
function validate(rules) {
  return (req, res, next) => {
    const errors = [];
    for (const [field, check] of Object.entries(rules)) {
      const val = req.params[field] ?? req.query[field];
      if (!check(val)) errors.push(`Invalid ${field}`);
    }
    if (errors.length) {
      return res.status(400).json({ success: false, error: errors.join('; ') });
    }
    next();
  };
}

const v = {
  pdbId: (val) => /^[A-Za-z0-9]{4}$/.test(val),
  page: (val) => !val || (+val > 0 && +val <= 10000),
  limit: (val) => !val || (+val > 0 && +val <= 100),
  sort: (val) => !val || ['pdb_id', 'resolution', 'method', 'deposit_date'].includes(val),
  order: (val) => !val || ['asc', 'desc'].includes(val),
  q: (val) => !val || (typeof val === 'string' && val.length <= 500),
};

module.exports = { validate, v };
