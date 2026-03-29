/**
 * BioStructure DB MCP Server
 * 让 AI 助手可以直接查询生物数据库
 */

const { Pool } = require('pg');

// 数据库连接池 (从环境变量读取)
const pool = new Pool({
  user: process.env.DB_USER || 'myapp_user',
  host: process.env.DB_HOST || '127.0.0.1',
  database: process.env.DB_NAME || 'myapp',
  password: process.env.DB_PASSWORD || 'MyApp@2026',
  port: process.env.DB_PORT || 5432,
});

// MCP 工具定义
const tools = {
  /**
   * 搜索结构
   */
  search_structures: {
    description: '搜索蛋白质结构 (按 PDB ID、基因名、生物体等)',
    inputSchema: {
      type: 'object',
      properties: {
        pdb_id: { type: 'string', description: 'PDB ID (如 1CRN)' },
        gene: { type: 'string', description: '基因名' },
        organism: { type: 'string', description: '生物体名称' },
        method: { type: 'string', description: '实验方法 (X-RAY/NMR/EM)' },
        max_resolution: { type: 'number', description: '最大分辨率 (Å)' }
      }
    },
    handler: async (args) => {
      const conditions = ['1=1'];
      const params = [];
      let paramCount = 0;
      
      if (args.pdb_id) {
        paramCount++;
        conditions.push(`pdb_id ILIKE $${paramCount}`);
        params.push(`%${args.pdb_id}%`);
      }
      
      if (args.gene) {
        paramCount++;
        conditions.push(`gene_name ILIKE $${paramCount}`);
        params.push(`%${args.gene}%`);
      }
      
      if (args.organism) {
        paramCount++;
        conditions.push(`organism_scientific_name ILIKE $${paramCount}`);
        params.push(`%${args.organism}%`);
      }
      
      if (args.method) {
        paramCount++;
        conditions.push(`method ILIKE $${paramCount}`);
        params.push(`%${args.method}%`);
      }
      
      if (args.max_resolution) {
        paramCount++;
        conditions.push(`resolution <= $${paramCount}`);
        params.push(args.max_resolution);
      }
      
      const query = `SELECT pdb_id, title, resolution, method, gene_name, organism_scientific_name 
                     FROM structures 
                     WHERE ${conditions.join(' AND ')} 
                     LIMIT 50`;
      
      const result = await pool.query(query, params);
      return { content: [{ type: 'text', text: JSON.stringify(result.rows, null, 2) }] };
    }
  },
  
  /**
   * 获取结构详情
   */
  get_structure_details: {
    description: '获取蛋白质结构的完整信息 (包括序列、配体、活性位点等)',
    inputSchema: {
      type: 'object',
      properties: {
        pdb_id: { type: 'string', description: 'PDB ID', required: true }
      }
    },
    handler: async (args) => {
      const structure = await pool.query('SELECT * FROM structures WHERE pdb_id = $1', [args.pdb_id]);
      
      if (structure.rows.length === 0) {
        return { content: [{ type: 'text', text: `未找到结构：${args.pdb_id}` }] };
      }
      
      const chains = await pool.query('SELECT * FROM polypeptides WHERE pdb_id = $1', [args.pdb_id]);
      const ligands = await pool.query('SELECT * FROM ligands WHERE pdb_id = $1', [args.pdb_id]);
      const sites = await pool.query('SELECT * FROM active_sites WHERE pdb_id = $1', [args.pdb_id]);
      
      const result = {
        structure: structure.rows[0],
        chains: chains.rows,
        ligands: ligands.rows,
        active_sites: sites.rows
      };
      
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  },
  
  /**
   * 搜索序列
   */
  search_sequence: {
    description: '搜索包含特定序列片段的结构',
    inputSchema: {
      type: 'object',
      properties: {
        sequence: { type: 'string', description: '氨基酸序列片段', required: true },
        exact: { type: 'boolean', description: '是否精确匹配' }
      }
    },
    handler: async (args) => {
      const query = args.exact
        ? 'SELECT pdb_id, chain_id, sequence FROM sequence_index WHERE sequence = $1'
        : 'SELECT pdb_id, chain_id, sequence FROM sequence_index WHERE sequence ILIKE $1 LIMIT 50';
      
      const params = args.exact ? [args.sequence] : [`%${args.sequence}%`];
      const result = await pool.query(query, params);
      
      return { content: [{ type: 'text', text: JSON.stringify(result.rows, null, 2) }] };
    }
  },
  
  /**
   * 获取统计信息
   */
  get_stats: {
    description: '获取数据库统计信息',
    inputSchema: {
      type: 'object',
      properties: {}
    },
    handler: async () => {
      const total = await pool.query('SELECT COUNT(*) FROM structures');
      const methods = await pool.query('SELECT method, COUNT(*) FROM structures GROUP BY method');
      const ligands = await pool.query('SELECT COUNT(DISTINCT ligand_name) FROM ligands');
      
      const stats = {
        total_structures: parseInt(total.rows[0].count),
        methods: methods.rows,
        unique_ligands: parseInt(ligands.rows[0].count)
      };
      
      return { content: [{ type: 'text', text: JSON.stringify(stats, null, 2) }] };
    }
  },
  
  /**
   * 搜索配体
   */
  search_ligands: {
    description: '搜索小分子配体',
    inputSchema: {
      type: 'object',
      properties: {
        name: { type: 'string', description: '配体名称或 3 字母代码' },
        formula: { type: 'string', description: '化学式' }
      }
    },
    handler: async (args) => {
      const conditions = ['1=1'];
      const params = [];
      
      if (args.name) {
        conditions.push(`ligand_name ILIKE $${params.length + 1}`);
        params.push(`%${args.name}%`);
      }
      
      if (args.formula) {
        conditions.push(`formula ILIKE $${params.length + 1}`);
        params.push(`%${args.formula}%`);
      }
      
      const query = `SELECT * FROM ligands WHERE ${conditions.join(' AND ')} LIMIT 50`;
      const result = await pool.query(query, params);
      
      return { content: [{ type: 'text', text: JSON.stringify(result.rows, null, 2) }] };
    }
  }
};

// MCP 协议实现
async function handleRequest(request) {
  const { method, params } = request;
  
  if (method === 'initialize') {
    return {
      jsonrpc: '2.0',
      id: request.id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {}
        },
        serverInfo: {
          name: 'biostructure-db',
          version: '1.0.0'
        }
      }
    };
  }
  
  if (method === 'tools/list') {
    return {
      jsonrpc: '2.0',
      id: request.id,
      result: {
        tools: Object.entries(tools).map(([name, tool]) => ({
          name,
          description: tool.description,
          inputSchema: tool.inputSchema
        }))
      }
    };
  }
  
  if (method === 'tools/call') {
    const { name, arguments: args } = params;
    
    if (!tools[name]) {
      return {
        jsonrpc: '2.0',
        id: request.id,
        error: { code: -32601, message: `Unknown tool: ${name}` }
      };
    }
    
    try {
      const result = await tools[name].handler(args || {});
      return {
        jsonrpc: '2.0',
        id: request.id,
        result
      };
    } catch (error) {
      return {
        jsonrpc: '2.0',
        id: request.id,
        error: { code: -32603, message: error.message }
      };
    }
  }
  
  return {
    jsonrpc: '2.0',
    id: request.id,
    error: { code: -32601, message: `Method not found: ${method}` }
  };
}

// 从 stdin 读取请求
process.stdin.on('data', async (data) => {
  try {
    const request = JSON.parse(data.toString());
    const response = await handleRequest(request);
    process.stdout.write(JSON.stringify(response) + '\n');
  } catch (error) {
    console.error('Error processing request:', error);
  }
});

console.error('BioStructure DB MCP Server started');
