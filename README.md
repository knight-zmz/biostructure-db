# 🧬 BioStructure DB

> Professional protein structure database reference PDB + UniProt + Pfam

[![Build](https://github.com/knight-zmz/biostructure-db/workflows/CI/badge.svg)](https://github.com/knight-zmz/biostructure-db/actions)
[![Version](https://img.shields.io/github/v/release/knight-zmz/biostructure-db)](https://github.com/knight-zmz/biostructure-db/releases)
[![License](https://img.shields.io/github/license/knight-zmz/biostructure-db)](LICENSE)
[![Stars](https://img.shields.io/github/stars/knight-zmz/biostructure-db)](https://github.com/knight-zmz/biostructure-db/stargazers)

**Live Demo**: http://101.200.53.98/  
**Documentation**: https://knight-zmz.github.io/biostructure-db/docs/

---

## ✨ Features

- 🔍 **Search**: Search protein structures by PDB ID, gene name, organism
- 🧬 **3D Visualization**: Interactive 3D molecular visualization with 3Dmol.js
- 📊 **Statistics**: Comprehensive statistical analysis
- 🚀 **RESTful API**: Well-documented REST API
- 💾 **PostgreSQL**: Robust database backend with 15+ tables
- 🔄 **Auto-deploy**: GitHub Actions CI/CD pipeline

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone repository
git clone https://github.com/knight-zmz/biostructure-db.git
cd biostructure-db

# Install dependencies
npm install
```

### 2. Configure Database

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE myapp;"
sudo -u postgres psql -c "CREATE USER myapp_user WITH PASSWORD 'MyApp@2026';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;"

# Import schema
psql -U myapp_user -d myapp -f src/db/schema.sql
```

### 3. Run Application

```bash
# Start server
npm start

# Or development mode
npm run dev
```

### 4. Access

- **Frontend**: http://localhost:3000/
- **API**: http://localhost:3000/api/stats

---

## 📦 Installation

### Prerequisites

- Node.js >= 20
- PostgreSQL >= 13
- Nginx (for production)
- PM2 (for production)

### Production Deployment

```bash
# Install PM2
npm install -g pm2

# Install dependencies
npm install --production

# Start application
pm2 start src/app.js --name biostructure-db

# Save PM2 configuration
pm2 save

# Setup PM2 startup
pm2 startup
```

---

## 📚 Documentation

### User Guide

- [Quick Start](docs/getting-started/quickstart.md)
- [Installation](docs/getting-started/installation.md)
- [FAQ](docs/getting-started/faq.md)

### API Reference

- [REST API](docs/api/rest-api.md)
- [OpenAPI Spec](docs/api/openapi.yaml)
- [Examples](docs/api/examples.md)

### Developer Guide

- [Architecture](docs/developer/architecture.md)
- [Contributing](docs/developer/contributing.md)
- [Release Guide](docs/developer/release.md)

---

## 🎯 Usage Examples

### Search Structures

```bash
# Search by PDB ID
curl http://localhost:3000/api/structures/1CRN

# Search by gene
curl "http://localhost:3000/api/bio/gene/TP53"

# Search by organism
curl "http://localhost:3000/api/bio/organism/Homo%20sapiens"
```

### Import PDB Structures

```bash
# Import single structure
curl -X POST http://localhost:3000/api/import/1CRN

# Batch import
./scripts/import-pdb-batch.sh
```

### 3D Visualization

Access http://localhost:3000/ and click on any structure to view 3D model.

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │
│  (HTML/CSS) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Nginx    │
│  (Reverse   │
│   Proxy)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Node.js +  │
│  Express    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
│   (15+      │
│   tables)   │
└─────────────┘
```

---

## 📊 Database Schema

### Core Tables

- `structures` - Protein structure metadata
- `polypeptides` - Polypeptide chains with sequences
- `residues` - Residue annotations
- `atoms` - 3D atomic coordinates
- `assemblies` - Biological assemblies
- `entities` - Molecular entities

### Annotation Tables

- `active_sites` - Active/binding sites
- `ligands` - Small molecule ligands
- `metal_ions` - Metal ions
- `ptms` - Post-translational modifications
- `secondary_structures` - Secondary structure annotations

### External References

- `uniprot_mappings` - UniProt cross-references
- `pfam_domains` - Pfam protein domains
- `citations` - Literature references

---

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Test Coverage

| Category | Coverage |
|----------|----------|
| Statements | 75% |
| Branches | 70% |
| Functions | 80% |
| Lines | 75% |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

```bash
# Install dependencies
npm install

# Run lint
npm run lint

# Format code
npm run format
```

---

## 📈 Roadmap

### v1.0 (Current)
- ✅ Basic structure search
- ✅ 3D visualization
- ✅ REST API
- ✅ PDB import

### v1.1 (Next)
- ⏳ Advanced search
- ⏳ Sequence alignment
- ⏳ Structure comparison
- ⏳ Download (PDB/mmCIF)

### v2.0 (Future)
- ⏳ User system
- ⏳ Favorites
- ⏳ Batch operations
- ⏳ AlphaFold integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **RCSB PDB**: https://www.rcsb.org
- **UniProt**: https://www.uniprot.org
- **Pfam**: https://www.ebi.ac.uk/interpro
- **3Dmol.js**: https://3dmol.org

---

## 📞 Contact

- **GitHub**: https://github.com/knight-zmz/biostructure-db
- **Issues**: https://github.com/knight-zmz/biostructure-db/issues
- **Email**: (TODO)

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/knight-zmz/biostructure-db?style=social)
![GitHub forks](https://img.shields.io/github/forks/knight-zmz/biostructure-db?style=social)
![GitHub issues](https://img.shields.io/github/issues/knight-zmz/biostructure-db)
![GitHub pull requests](https://img.shields.io/github/issues-pr/knight-zmz/biostructure-db)

---

**Made with 🦞 and ❤️ by OpenClaw**
