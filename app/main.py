import asyncio
import aiosqlite
import os
import json
import aiohttp
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="JLU Protein Database",
    description="A comprehensive protein structure database with 3D visualization, REST API, and real PDB data integration",
    version="3.0.0"
)

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "protein.db")
PDB_CACHE_DIR = os.path.join(BASE_DIR, "static", "pdb_files")
os.makedirs(PDB_CACHE_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# RCSB PDB API base
RCSB_API = "https://data.rcsb.org/rest/v1/core/entry"
RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Enhanced schema
        await db.execute('''CREATE TABLE IF NOT EXISTS proteins (
            id TEXT PRIMARY KEY,
            name TEXT,
            organism TEXT,
            organism_taxid INTEGER,
            method TEXT,
            resolution REAL,
            r_free REAL,
            r_work REAL,
            sequence TEXT,
            sequence_length INTEGER,
            date TEXT,
            deposition_date TEXT,
            chain_count INTEGER DEFAULT 1,
            residue_count INTEGER DEFAULT 0,
            atom_count INTEGER DEFAULT 0,
            structure_class TEXT,
            keywords TEXT,
            authors TEXT,
            pdb_file_url TEXT,
            has_ligands BOOLEAN DEFAULT 0,
            ligand_list TEXT,
            related_entries TEXT,
            pubmed_id TEXT,
            doi TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Sequence similarity index
        await db.execute('''CREATE INDEX IF NOT EXISTS idx_proteins_organism ON proteins(organism)''')
        await db.execute('''CREATE INDEX IF NOT EXISTS idx_proteins_method ON proteins(method)''')
        await db.execute('''CREATE INDEX IF NOT EXISTS idx_proteins_resolution ON proteins(resolution)''')
        
        count = await db.execute("SELECT count(*) FROM proteins")
        if (await count.fetchone())[0] == 0:
            await seed_db(db)
        await db.commit()

async def seed_db(db):
    """Seed with enhanced real-world-like protein data"""
    proteins = [
        {
            "id": "1JLU", "name": "Hemoglobin Alpha Chain", "organism": "Homo sapiens",
            "organism_taxid": 9606, "method": "X-RAY DIFFRACTION", "resolution": 2.1,
            "r_free": 0.245, "r_work": 0.198, "sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH-GSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
            "sequence_length": 141, "date": "2026-01-15", "deposition_date": "2025-12-01",
            "chain_count": 2, "residue_count": 282, "atom_count": 2356,
            "structure_class": "All Alpha", "keywords": "OXYGEN TRANSPORT, HEME, IRON",
            "authors": "Kendrew JC, Perutz MF", "has_ligands": 1,
            "ligand_list": "[\"HEM\", \"OXY\"]", "related_entries": "[\"2HHB\", \"3HHB\"]",
            "pubmed_id": "12345678", "doi": "10.1038/nature12345"
        },
        {
            "id": "2ABC", "name": "Green Fluorescent Protein", "organism": "Aequorea victoria",
            "organism_taxid": 6100, "method": "X-RAY DIFFRACTION", "resolution": 1.9,
            "r_free": 0.221, "r_work": 0.182, "sequence": "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGM",
            "sequence_length": 238, "date": "2025-11-20", "deposition_date": "2025-10-05",
            "chain_count": 1, "residue_count": 238, "atom_count": 1876,
            "structure_class": "All Beta", "keywords": "FLUORESCENT PROTEIN, GFP, BIOLUMINESCENCE",
            "authors": "Tsien RY, Zimmer M", "has_ligands": 0,
            "ligand_list": "[]", "related_entries": "[\"1EMA\", \"4KW4\"]",
            "pubmed_id": "8734567", "doi": "10.1126/science.273.5280.1392"
        },
        {
            "id": "4HHB", "name": "Human Deoxyhemoglobin", "organism": "Homo sapiens",
            "organism_taxid": 9606, "method": "X-RAY DIFFRACTION", "resolution": 2.5,
            "r_free": 0.258, "r_work": 0.210, "sequence": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH-GSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
            "sequence_length": 146, "date": "2025-09-10", "deposition_date": "2025-08-01",
            "chain_count": 4, "residue_count": 574, "atom_count": 4892,
            "structure_class": "All Alpha", "keywords": "OXYGEN TRANSPORT, TETRAMER, ALLOSTERY",
            "authors": "Fermi G, Perutz MF", "has_ligands": 1,
            "ligand_list": "[\"HEM\"]", "related_entries": "[\"1JLU\", \"2HHB\"]",
            "pubmed_id": "7654321", "doi": "10.1016/j.jmb.2005.06.059"
        },
        {
            "id": "6M0J", "name": "SARS-CoV-2 Spike Glycoprotein", "organism": "Severe acute respiratory syndrome coronavirus 2",
            "organism_taxid": 2697049, "method": "ELECTRON MICROSCOPY", "resolution": 3.5,
            "r_free": 0.285, "r_work": 0.245, "sequence": "MFVFLVLLPLVSSQCVNLTTRTQLPPAYTNSFTRGVYYPDKVFRSSVLHSTQDLFLPFFSNVTWFHAIHVSGTNGTKRFDNPVLPFNDGVYFASTEKSNIIRGWIFGTTLDSKTQSLLIVNNATNVVIKVCEFQFCNDPFLGVYYHKNNKSWMESEFRVYSSANNCTFEYVSQPFLMDLEGKQGNFKNLREFVFKNIDGYFKIYSKHTPINLVRDLPQGFSALEPLVDLPIGINITRFQTLLALHRSYLTPGDSSSGWTAGAAAYYVGYLQPRTFLLKYNENGTITDAVDCALDPLSETKCTLKSFTVEKGIYQTSNFRVQPTESIVRFPNITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKST",
            "sequence_length": 1273, "date": "2026-02-20", "deposition_date": "2026-01-15",
            "chain_count": 3, "residue_count": 3216, "atom_count": 25678,
            "structure_class": "Alpha/Beta", "keywords": "VIRAL PROTEIN, SPIKE, CORONAVIRUS, MEMBRANE FUSION",
            "authors": "Wrapp D, McLellan JS", "has_ligands": 1,
            "ligand_list": "[\"NAG\", \"FUL\"]", "related_entries": "[\"6VSB\", \"7DF4\"]",
            "pubmed_id": "32075877", "doi": "10.1126/science.abb2507"
        },
        {
            "id": "1TIM", "name": "Triosephosphate Isomerase", "organism": "Trypanosoma brucei",
            "organism_taxid": 5691, "method": "X-RAY DIFFRACTION", "resolution": 1.9,
            "r_free": 0.215, "r_work": 0.175, "sequence": "MSRVLLGAFVNADQAEATEMKKAGVGKISVSTIGASMLKDLIGATSKVDSDGAKTVAIECIKKLGATQKISADNPDAASVACSVGISDTSGNPNITNSCVKDIVVAYEPVWAIGTGKTATPEQAEAAIGQKVSKMVADIVATARDLSGSTGGSVNGCSIGKAAALAVDTEIGVSLEKKNRVTPGFNLKEFAKLIPEVANLKHFIDNATDQVQKALEEKFGVQPTLVISGGASLELAGYTDATVPSHDFTTDAWNTAISTYAKKNGYNTRNGWVTNISENIIAATGTTNPKVHFVQGFKEGKDTTTPTGAAAVEQVPYVATFLAHDNQPVIVGGNMGGGHEVVGARTFRKDMYETMVKAGNGIPATRDEIIPQMAAAVQKAKKG",
            "sequence_length": 250, "date": "2025-08-15", "deposition_date": "2025-07-01",
            "chain_count": 2, "residue_count": 500, "atom_count": 3890,
            "structure_class": "Alpha/Beta Barrel", "keywords": "GLYCOLYSIS, ISOMERASE, TIM BARREL",
            "authors": "Wierenga RK, Kaptein R", "has_ligands": 1,
            "ligand_list": "[\"PEP\", \"SO4\"]", "related_entries": "[\"2YHB\", \"7TIM\"]",
            "pubmed_id": "6543210", "doi": "10.1002/prot.340010103"
        },
        {
            "id": "2Q8Q", "name": "Aquaporin-0 Junction", "organism": "Bos taurus",
            "organism_taxid": 9913, "method": "ELECTRON CRYSTALLOGRAPHY", "resolution": 3.0,
            "r_free": 0.275, "r_work": 0.230, "sequence": "MDAEETGGRLFSVTFAGIVLAALSFAFATGLNPAKNPQFTPAVTVLGLMGTMAGMSLGHISPAIALAQARQWALIFWGPLPGLAVVENLCSFSYVQEVGQHIQVFGKEAIPNASGNMNKSVEMFVQKSGGWTMNPAIPLAVIIFSTQLAGVIDSRTRSPFSYASQINKAMGPEDEKGANFYTSIPAMLAFLALYFFASATSLPAEIGHSQVSPSLSLGLKII",
            "sequence_length": 263, "date": "2025-10-22", "deposition_date": "2025-09-10",
            "chain_count": 4, "residue_count": 1052, "atom_count": 7824,
            "structure_class": "All Alpha", "keywords": "MEMBRANE PROTEIN, WATER CHANNEL, JUNCTION",
            "authors": "Gonen T, Sliz P", "has_ligands": 0,
            "ligand_list": "[]", "related_entries": "[\"1SOR\", \"2B6P\"]",
            "pubmed_id": "16840511", "doi": "10.1038/nature04973"
        },
        {
            "id": "3K3N", "name": "Taq DNA Polymerase with DNA", "organism": "Thermus aquaticus",
            "organism_taxid": 271, "method": "X-RAY DIFFRACTION", "resolution": 2.5,
            "r_free": 0.265, "r_work": 0.205, "sequence": "MPIKNIKEYLRKHNQKIDKIIPMPVKERIEAKFKEAKQGLKPLASSEEELKKLLELYSLLGIDEDDPKVEKALQEMTKEYGLQNPDDKATETKQIEEIYKEGKPVFYKGGRIRFDFKRPNTAKTALRIKDGNVKELFQYGYDRVTDYKKAYTKVEVPGDSLIDWRLDTPDPEEAFETLRDTFAEYLEKIRKEGYEVDIFKAGKLYTQKPELLEAPYIRIRGRNIDDKIEEVKEKFYEKGLKEPVEVTWETGKFDTKPEAIEKIAQKYANLNQIPQRTIAEVYNDLIEGTHSHLRHCLRLVENNLLGRDIARDIPQFALEQRYAEAKDFEGDDSEDPEEPEPPEPPEPPEPEDEEGEDEEEEDETLEPQESDPEMEPEPEPEPEPEPEPEPEPEPEPEPEIIPDDPVPPEPEPVPKIEELEKKEAQKAKAAAKAAAQAKAAKQAKQAKAKAKQAKQAEAEAEAEAEEEEVPEEP",
            "sequence_length": 832, "date": "2026-03-01", "deposition_date": "2026-01-20",
            "chain_count": 1, "residue_count": 832, "atom_count": 6540,
            "structure_class": "Alpha/Beta", "keywords": "DNA POLYMERASE, PCR, THERMOSTABLE, REPLICATION",
            "authors": "Eom SH, Steitz TA", "has_ligands": 1,
            "ligand_list": "[\"DNA\", \"MG\", \"DTP\"]", "related_entries": "[\"1TAQ\", \"5TAQ\"]",
            "pubmed_id": "9234567", "doi": "10.1038/382278a0"
        },
        {
            "id": "5P21", "name": "Ras p21 Oncoprotein", "organism": "Homo sapiens",
            "organism_taxid": 9606, "method": "X-RAY DIFFRACTION", "resolution": 1.9,
            "r_free": 0.225, "r_work": 0.185, "sequence": "MTEYKLVVVGAVGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQEEYSAMRDQYMRTGEGFLCVFAINNTKSFEDIHHYREQIKRVKDSEDVPMVLVGNKCDLAARTVESRQAQDLARSYGIPYIETSAKTRQGVEDAFYTLVREIRQH",
            "sequence_length": 166, "date": "2025-07-18", "deposition_date": "2025-06-01",
            "chain_count": 1, "residue_count": 166, "atom_count": 1324,
            "structure_class": "Alpha/Beta", "keywords": "GTP-BINDING, ONCOGENE, SIGNALING, G-PROTEIN",
            "authors": "Pai EF, Wittinghofer A", "has_ligands": 1,
            "ligand_list": "[\"GDP\", \"MG\"]", "related_entries": "[\"4Q21\", \"5P21\"]",
            "pubmed_id": "2505829", "doi": "10.1038/341209a0"
        },
        {
            "id": "1CRN", "name": "Crambin", "organism": "Crambe hispanica",
            "organism_taxid": 3704, "method": "X-RAY DIFFRACTION", "resolution": 1.5,
            "r_free": 0.210, "r_work": 0.165, "sequence": "TTCCPSIVARSNFNVCRLPGTPEALCATYTGCIIIPGATCPGDYAN",
            "sequence_length": 46, "date": "2025-12-05", "deposition_date": "2025-11-01",
            "chain_count": 1, "residue_count": 46, "atom_count": 456,
            "structure_class": "All Alpha", "keywords": "PLANT PROTEIN, SEED STORAGE, DISULFIDE",
            "authors": "Hendrickson WA, Teeter MM", "has_ligands": 0,
            "ligand_list": "[]", "related_entries": "[\"1EJG\", \"3CRN\"]",
            "pubmed_id": "7248991", "doi": "10.1038/290107a0"
        },
        {
            "id": "7XYZ", "name": "CRISPR-Cas9 Complex", "organism": "Streptococcus pyogenes",
            "organism_taxid": 1314, "method": "X-RAY DIFFRACTION", "resolution": 2.6,
            "r_free": 0.270, "r_work": 0.220, "sequence": "MKKQYITKRASEFDRVQRQIAKLGLKPEACTQCYHFTKDSDCDVRNCAILKMVEKAPYVIEEFSRVEDFIHLAGSIEQDQKQYQKILLLNEDGFSILPSQIAKRTGYQVTRNILKAIGGTDVKQWPNHEFGEYFKALDFIKGDKLYEQTLKDPQYKILKKFKKELPYNLIEDFSNKKNKIINLVGKTILGNMKEKAKDKIEKYLKSTGKYQIKTFKEKKENKIKNIAKIIGVQECPETWRENLYKEIIKKKGAEKVVDILAQHNLAENHNLIELEKELEEALKQKKEELIKKAEKPYIVPKEWFDNIPMQTNLQKQIEKIKKEGLHTEILHKLLAEELKEKEEKIKELQKKLDELQKKKQYEKEIETLEIKKQKKELEEKIKELEQKLDELQ",
            "sequence_length": 1368, "date": "2026-01-28", "deposition_date": "2025-12-10",
            "chain_count": 2, "residue_count": 1520, "atom_count": 12450,
            "structure_class": "Alpha/Beta", "keywords": "CRISPR, GENE EDITING, ENDONUCLEASE, RNA-GUIDED",
            "authors": "Jinek M, Doudna JA", "has_ligands": 1,
            "ligand_list": "[\"RNA\", \"DNA\", \"MG\"]", "related_entries": "[\"4CMP\", \"5F9R\"]",
            "pubmed_id": "22745249", "doi": "10.1126/science.1225829"
        },
        {
            "id": "8ADK", "name": "Adenylate Kinase", "organism": "Escherichia coli",
            "organism_taxid": 562, "method": "X-RAY DIFFRACTION", "resolution": 2.0,
            "r_free": 0.240, "r_work": 0.195, "sequence": "MKFKLLFTAAKPAQAAGKAGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQEEYSAMRDQYMRTGEGFLCVFAINNTKSFEDIHHYREQIKRVKDS",
            "sequence_length": 214, "date": "2025-06-15", "deposition_date": "2025-05-01",
            "chain_count": 1, "residue_count": 214, "atom_count": 1678,
            "structure_class": "Alpha/Beta", "keywords": "KINASE, PHOSPHOTRANSFERASE, NUCLEOTIDE METABOLISM",
            "authors": "Muller CW, Schulz GE", "has_ligands": 1,
            "ligand_list": "[\"AMP\", \"AP5A\"]", "related_entries": "[\"1AKE\", \"4AKE\"]",
            "pubmed_id": "1377660", "doi": "10.1016/0022-2836(92)90816-6"
        },
        {
            "id": "9INS", "name": "Insulin", "organism": "Homo sapiens",
            "organism_taxid": 9606, "method": "X-RAY DIFFRACTION", "resolution": 1.5,
            "r_free": 0.205, "r_work": 0.160, "sequence": "FVNQHLCGSHLVEALYLVCGERGFFYTPKT GIVEQCCTSICSLYQLENYCN",
            "sequence_length": 51, "date": "2025-09-25", "deposition_date": "2025-08-10",
            "chain_count": 2, "residue_count": 51, "atom_count": 432,
            "structure_class": "All Alpha", "keywords": "HORMONE, PANCREAS, DIABETES, DISULFIDE",
            "authors": "Hodgkin DC", "has_ligands": 1,
            "ligand_list": "[\"ZN\"]", "related_entries": "[\"1INS\", \"3INS\"]",
            "pubmed_id": "5360034", "doi": "10.1098/rspb.1969.0025"
        },
        {
            "id": "1A4Y", "name": "Bacteriorhodopsin", "organism": "Halobacterium salinarum",
            "organism_taxid": 2241, "method": "ELECTRON CRYSTALLOGRAPHY", "resolution": 1.55,
            "r_free": 0.218, "r_work": 0.172, "sequence": "MTEYTQATISTSTIAGAVILIGLILFWAPSAIAFGEIPELYQILFWIIGSVLNGLFIGMFYEVLPMILGIIFGLAEKFPELIIAFIIANIVPLIIGTILNQLIMAIKTIEKVYPFSGEEIPVAEIIHLPVIIFVMIVPYLLGLLVDADLNFTEEEVAATLGSLAIVLGFAMSEIPLAQIYTWIFVIFTVLPLFTGIQLIFAGKHWWVFS",
            "sequence_length": 248, "date": "2025-11-30", "deposition_date": "2025-10-15",
            "chain_count": 3, "residue_count": 744, "atom_count": 5890,
            "structure_class": "All Alpha", "keywords": "MEMBRANE PROTEIN, PROTON PUMP, RETINAL, ARCHAEA",
            "authors": "Luecke H, Richter HT", "has_ligands": 1,
            "ligand_list": "[\"RET\"]", "related_entries": "[\"1BRX\", \"2AT9\"]",
            "pubmed_id": "10560278", "doi": "10.1006/jmbi.1999.3179"
        },
        {
            "id": "2V0O", "name": "HIV-1 Protease", "organism": "Human immunodeficiency virus 1",
            "organism_taxid": 11676, "method": "X-RAY DIFFRACTION", "resolution": 2.0,
            "r_free": 0.245, "r_work": 0.198, "sequence": "PQITLWQRPLVTIKIGGQLKEALLDTGADDTVLEEMNLPGRWKPKMIGGIGGFIKVRQYDQILIEICGHKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF",
            "sequence_length": 99, "date": "2026-02-10", "deposition_date": "2026-01-05",
            "chain_count": 2, "residue_count": 198, "atom_count": 1560,
            "structure_class": "All Beta", "keywords": "VIRAL PROTEIN, PROTEASE, HIV, ASPARTIC PROTEASE, DRUG TARGET",
            "authors": "Wlodawer A, Miller M", "has_ligands": 1,
            "ligand_list": "[\"DRUG\", \"ACT\"]", "related_entries": "[\"1HVR\", \"3HVP\"]",
            "pubmed_id": "2715545", "doi": "10.1126/science.2715545"
        },
        {
            "id": "3CRW", "name": "Calmodulin", "organism": "Homo sapiens",
            "organism_taxid": 9606, "method": "X-RAY DIFFRACTION", "resolution": 2.2,
            "r_free": 0.255, "r_work": 0.208, "sequence": "MADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK",
            "sequence_length": 148, "date": "2025-08-20", "deposition_date": "2025-07-05",
            "chain_count": 1, "residue_count": 148, "atom_count": 1156,
            "structure_class": "All Alpha", "keywords": "CALCIUM BINDING, SIGNALING, EF-HAND",
            "authors": "Babu YS, Bugg CE", "has_ligands": 1,
            "ligand_list": "[\"CA\"]", "related_entries": "[\"1CLL\", \"4CLN\"]",
            "pubmed_id": "3173396", "doi": "10.1038/315037a0"
        }
    ]
    
    for p in proteins:
        p["pdb_file_url"] = f"https://files.rcsb.org/download/{p['id']}.pdb"
        await db.execute('''INSERT INTO proteins VALUES (
            :id, :name, :organism, :organism_taxid, :method, :resolution,
            :r_free, :r_work, :sequence, :sequence_length, :date, :deposition_date,
            :chain_count, :residue_count, :atom_count, :structure_class, :keywords,
            :authors, :pdb_file_url, :has_ligands, :ligand_list, :related_entries,
            :pubmed_id, :doi, :created_at, :updated_at
        )''', {**p, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()})

@app.on_event("startup")
async def startup():
    await init_db()

# ==================== WEB PAGES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, search: Optional[str] = Query(None), method: Optional[str] = Query(None)):
    db = await get_db()
    conditions = []
    params = []
    
    if search:
        conditions.append("(id LIKE ? OR name LIKE ? OR organism LIKE ? OR keywords LIKE ?)")
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern, pattern])
    
    if method:
        conditions.append("method = ?")
        params.append(method)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM proteins WHERE {where_clause} ORDER BY date DESC LIMIT 50"
    
    async with db.execute(query, params) as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "proteins": proteins,
        "search": search or "",
        "method": method or ""
    })

@app.get("/pdb/{pdb_id}", response_class=HTMLResponse)
async def detail(request: Request, pdb_id: str):
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    
    protein_dict = dict(protein)
    # Parse JSON fields
    for field in ["ligand_list", "related_entries"]:
        try:
            protein_dict[field] = json.loads(protein_dict[field]) if protein_dict[field] else []
        except:
            protein_dict[field] = []
    
    return templates.TemplateResponse("detail.html", {
        "request": request, 
        "protein": protein_dict
    })

@app.get("/viewer/{pdb_id}", response_class=HTMLResponse)
async def viewer(request: Request, pdb_id: str):
    """3D Structure Viewer page"""
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    return templates.TemplateResponse("viewer.html", {
        "request": request,
        "protein": dict(protein)
    })

@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    db = await get_db()
    async with db.execute("SELECT COUNT(*) as total FROM proteins") as cursor:
        total = (await cursor.fetchone())["total"]
    async with db.execute("SELECT COUNT(DISTINCT method) as methods FROM proteins") as cursor:
        methods = (await cursor.fetchone())["methods"]
    async with db.execute("SELECT AVG(resolution) as avg_res, SUM(atom_count) as total_atoms FROM proteins") as cursor:
        stats = await cursor.fetchone()
    async with db.execute("SELECT method, COUNT(*) as count FROM proteins GROUP BY method ORDER BY count DESC") as cursor:
        method_dist = await cursor.fetchall()
    async with db.execute("SELECT structure_class, COUNT(*) as count FROM proteins WHERE structure_class IS NOT NULL GROUP BY structure_class ORDER BY count DESC") as cursor:
        class_dist = await cursor.fetchall()
    async with db.execute("SELECT organism, COUNT(*) as count FROM proteins GROUP BY organism ORDER BY count DESC LIMIT 10") as cursor:
        organism_dist = await cursor.fetchall()
    await db.close()
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "total": total,
        "methods": methods,
        "avg_res": round(stats["avg_res"], 2) if stats["avg_res"] else 0,
        "total_atoms": stats["total_atoms"] or 0,
        "method_dist": method_dist,
        "class_dist": class_dist,
        "organism_dist": organism_dist
    })

@app.get("/blast", response_class=HTMLResponse)
async def blast_page(request: Request):
    """Simple BLAST-like sequence similarity search"""
    return templates.TemplateResponse("blast.html", {"request": request, "results": None, "query": ""})

@app.post("/blast", response_class=HTMLResponse)
async def blast_search(request: Request):
    """Perform simple sequence similarity search"""
    form = await request.form()
    query_seq = form.get("sequence", "").upper().replace("\n", "").replace(" ", "")
    
    if not query_seq:
        return templates.TemplateResponse("blast.html", {"request": request, "results": None, "query": "", "error": "Please enter a sequence"})
    
    db = await get_db()
    async with db.execute("SELECT id, name, organism, sequence, sequence_length FROM proteins") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    
    # Simple similarity scoring
    results = []
    for p in proteins:
        seq = p["sequence"].upper().replace("-", "")
        score = simple_sequence_similarity(query_seq, seq)
        if score > 0.1:  # Threshold
            results.append({**p, "similarity": round(score * 100, 1)})
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    
    return templates.TemplateResponse("blast.html", {
        "request": request,
        "results": results[:20],
        "query": query_seq
    })

def simple_sequence_similarity(seq1: str, seq2: str) -> float:
    """Simple k-mer based similarity (fast approximation)"""
    if not seq1 or not seq2:
        return 0.0
    k = 3
    if len(seq1) < k or len(seq2) < k:
        return 0.0
    
    def get_kmers(s, k):
        return set(s[i:i+k] for i in range(len(s)-k+1))
    
    kmers1 = get_kmers(seq1, k)
    kmers2 = get_kmers(seq2, k)
    
    if not kmers1 or not kmers2:
        return 0.0
    
    intersection = kmers1 & kmers2
    union = kmers1 | kmers2
    
    return len(intersection) / len(union) if union else 0.0

# ==================== REST API ====================

@app.get("/api/v1/proteins", response_class=JSONResponse)
async def api_list_proteins(
    search: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    organism: Optional[str] = Query(None),
    structure_class: Optional[str] = Query(None),
    min_resolution: Optional[float] = Query(None),
    max_resolution: Optional[float] = Query(None),
    has_ligands: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    db = await get_db()
    conditions = []
    params = []
    
    if search:
        conditions.append("(id LIKE ? OR name LIKE ? OR organism LIKE ? OR keywords LIKE ?)")
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern, pattern])
    if method:
        conditions.append("method = ?")
        params.append(method)
    if organism:
        conditions.append("organism LIKE ?")
        params.append(f"%{organism}%")
    if structure_class:
        conditions.append("structure_class = ?")
        params.append(structure_class)
    if min_resolution is not None:
        conditions.append("resolution >= ?")
        params.append(min_resolution)
    if max_resolution is not None:
        conditions.append("resolution <= ?")
        params.append(max_resolution)
    if has_ligands is not None:
        conditions.append("has_ligands = ?")
        params.append(1 if has_ligands else 0)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM proteins WHERE {where_clause} ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        proteins = [dict(row) async for row in cursor]
    
    count_query = f"SELECT COUNT(*) as total FROM proteins WHERE {where_clause}"
    async with db.execute(count_query, params[:-2]) as cursor:
        total = (await cursor.fetchone())["total"]
    
    await db.close()
    
    return {
        "data": proteins,
        "pagination": {"total": total, "limit": limit, "offset": offset, "has_more": offset + limit < total}
    }

@app.get("/api/v1/proteins/search", response_class=JSONResponse)
async def api_search(q: str = Query(..., min_length=1)):
    db = await get_db()
    query = """SELECT *, 
               (CASE 
                   WHEN id LIKE ? THEN 3
                   WHEN name LIKE ? THEN 2
                   WHEN organism LIKE ? THEN 1
                   ELSE 0
               END) as relevance
               FROM proteins 
               WHERE id LIKE ? OR name LIKE ? OR organism LIKE ? OR sequence LIKE ? OR keywords LIKE ?
               ORDER BY relevance DESC, id LIMIT 50"""
    pattern = f"%{q}%"
    async with db.execute(query, (pattern, pattern, pattern, pattern, pattern, pattern, pattern, pattern)) as cursor:
        proteins = [dict(row) async for row in cursor]
        for p in proteins:
            p.pop("relevance", None)
    await db.close()
    return {"results": proteins, "count": len(proteins)}

@app.get("/api/v1/proteins/{pdb_id}", response_class=JSONResponse)
async def api_get_protein(pdb_id: str):
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    return dict(protein)

@app.get("/api/v1/proteins/{pdb_id}/fasta", response_class=JSONResponse)
async def api_get_fasta(pdb_id: str):
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    protein = dict(protein)
    fasta = f">{protein['id']} {protein['name']}|{protein['organism']}\n{protein['sequence']}"
    return {"format": "FASTA", "data": fasta, "pdb_id": protein["id"]}

@app.get("/api/v1/proteins/{pdb_id}/pdb", response_class=JSONResponse)
async def api_get_pdb_url(pdb_id: str):
    """Get PDB file download URL"""
    return {"pdb_id": pdb_id.upper(), "url": f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"}

@app.get("/api/v1/stats", response_class=JSONResponse)
async def api_stats():
    db = await get_db()
    async with db.execute("SELECT COUNT(*) as total FROM proteins") as cursor:
        total = (await cursor.fetchone())["total"]
    async with db.execute("SELECT AVG(resolution) as avg_res, MIN(resolution) as min_res, MAX(resolution) as max_res, SUM(atom_count) as total_atoms FROM proteins") as cursor:
        res_stats = await cursor.fetchone()
    async with db.execute("SELECT method, COUNT(*) as count FROM proteins GROUP BY method ORDER BY count DESC") as cursor:
        method_dist = [dict(row) async for row in cursor]
    async with db.execute("SELECT structure_class, COUNT(*) as count FROM proteins WHERE structure_class IS NOT NULL GROUP BY structure_class ORDER BY count DESC") as cursor:
        class_dist = [dict(row) async for row in cursor]
    async with db.execute("SELECT organism, COUNT(*) as count FROM proteins GROUP BY organism ORDER BY count DESC LIMIT 10") as cursor:
        organism_dist = [dict(row) async for row in cursor]
    async with db.execute("SELECT id, name, date FROM proteins ORDER BY date DESC LIMIT 5") as cursor:
        recent = [dict(row) async for row in cursor]
    await db.close()
    return {
        "total_entries": total,
        "total_atoms": res_stats["total_atoms"] or 0,
        "resolution": {"average": round(res_stats["avg_res"], 2) if res_stats["avg_res"] else 0, "min": res_stats["min_res"], "max": res_stats["max_res"]},
        "methods": method_dist,
        "structure_classes": class_dist,
        "top_organisms": organism_dist,
        "recent_entries": recent
    }

@app.get("/api/v1/download/fasta", response_class=JSONResponse)
async def api_download_all_fasta():
    db = await get_db()
    async with db.execute("SELECT * FROM proteins ORDER BY id") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    fasta_entries = [f">{p['id']} {p['name']}|{p['organism']}\n{p['sequence']}" for p in proteins]
    return {"format": "FASTA", "count": len(proteins), "data": "\n".join(fasta_entries)}

@app.get("/api/v1/download/json", response_class=JSONResponse)
async def api_download_all_json():
    db = await get_db()
    async with db.execute("SELECT * FROM proteins ORDER BY id") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    return {"proteins": proteins, "count": len(proteins), "exported_at": datetime.now().isoformat()}

@app.get("/api/v1/blast", response_class=JSONResponse)
async def api_blast(sequence: str = Query(..., min_length=5, description="Query amino acid sequence")):
    """Simple BLAST-like sequence similarity search via API"""
    sequence = sequence.upper()
    db = await get_db()
    async with db.execute("SELECT id, name, organism, sequence, sequence_length FROM proteins") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    
    results = []
    for p in proteins:
        seq = p["sequence"].upper().replace("-", "")
        score = simple_sequence_similarity(sequence, seq)
        if score > 0.1:
            results.append({**p, "similarity": round(score * 100, 1)})
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return {"query": sequence, "results": results[:20], "count": len(results)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "3.0.0"}
