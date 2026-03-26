# 🧬 BioStructure DB MCP Server

## 配置说明

### 在 OpenClaw 中配置

编辑 `~/.openclaw/openclaw.json`，添加：

```json
{
  "mcpServers": {
    "biostructure-db": {
      "command": "node",
      "args": ["/var/www/myapp/src/mcp-server.js"],
      "env": {
        "DATABASE_URL": "postgresql://myapp_user:MyApp@2026@localhost:5432/myapp"
      }
    }
  }
}
```

### 重启 OpenClaw

```bash
openclaw restart
```

### 验证配置

```bash
openclaw mcp list
```

应该看到：
```
✅ biostructure-db - connected
```

---

## 可用工具

### search_structures
搜索蛋白质结构

**参数**:
- `pdb_id`: PDB ID (如 "1CRN")
- `gene`: 基因名 (如 "TP53")
- `organism`: 生物体名称
- `method`: 实验方法
- `max_resolution`: 最大分辨率

**示例**:
```javascript
tools/call {
  name: "search_structures",
  arguments: { gene: "TP53", max_resolution: 2.5 }
}
```

### get_structure_details
获取结构详情

**参数**:
- `pdb_id`: PDB ID (必需)

**示例**:
```javascript
tools/call {
  name: "get_structure_details",
  arguments: { pdb_id: "1CRN" }
}
```

### search_sequence
搜索序列

**参数**:
- `sequence`: 氨基酸序列
- `exact`: 是否精确匹配

**示例**:
```javascript
tools/call {
  name: "search_sequence",
  arguments: { sequence: "PLAQ", exact: true }
}
```

### get_stats
获取统计信息

**参数**: 无

**示例**:
```javascript
tools/call {
  name: "get_stats"
}
```

### search_ligands
搜索配体

**参数**:
- `name`: 配体名称
- `formula`: 化学式

**示例**:
```javascript
tools/call {
  name: "search_ligands",
  arguments: { name: "ATP" }
}
```

---

## 故障排除

### 问题：MCP Server 未连接

**解决**:
```bash
# 检查进程
ps aux | grep mcp-server

# 重启 OpenClaw
openclaw restart

# 查看日志
tail -f ~/.openclaw/logs/mcp.log
```

### 问题：数据库连接失败

**解决**:
```bash
# 检查 PostgreSQL
systemctl status postgresql

# 测试连接
psql -U myapp_user -d myapp -c "SELECT 1"
```

---

**最后更新**: 2026-03-26
