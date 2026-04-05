import asyncio
import aiosqlite
import os
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(
    title="JLU Protein Database",
    description="A comprehensive protein structure database with REST API",
    version="2.0.0"
)

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "protein.db")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Helper functions
async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def dict_from_row(row):
    if row is None:
        return None
    return dict(row)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS proteins (
            id TEXT PRIMARY KEY,
            name TEXT,
            organism TEXT,
            method TEXT,
            resolution REAL,
            sequence TEXT,
            date TEXT,
            chain_count INTEGER DEFAULT 1,
            residue_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        count = await db.execute("SELECT count(*) FROM proteins")
        if (await count.fetchone())[0] == 0:
            await seed_db(db)
        await db.commit()

async def seed_db(db):
    proteins = [
        ("1JLU", "Hemoglobin Alpha Chain", "Homo sapiens", "X-RAY DIFFRACTION", 2.1, "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH-GSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR", "2026-01-15", 2, 141),
        ("2ABC", "Green Fluorescent Protein", "Aequorea victoria", "X-RAY DIFFRACTION", 1.9, "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGM", "2025-11-20", 1, 238),
        ("3XYZ", "Insulin", "Bos taurus", "X-RAY DIFFRACTION", 1.5, "GIVEQCCTSICSLYQLENYCN FVNQHLCGSHLVEALYLVCGERGFFYTPKT", "2025-09-10", 2, 51),
        ("4DNA", "DNA Polymerase I", "Escherichia coli", "X-RAY DIFFRACTION", 2.5, "MRSLLILVLCFLPLAALGKVRQAPKQTGRKLAEMFSKYLDKDWPAMQARNAEELAQNGADVHQMFGRTLSDAVRAGDPEWRMFSYGERMVKYLINTQSGDLVESIDGSVGRWEEAVQDGLPSVTEDQKRWALNFEQSGRFQVYAPATGDDNSSSGQPLDTRVALKRRAKLE", "2026-02-01", 1, 156),
        ("5ENZ", "Lysozyme C", "Gallus gallus", "X-RAY DIFFRACTION", 1.7, "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL", "2025-12-12", 1, 129),
        ("6REC", "Rhodopsin", "Bos taurus", "ELECTRON MICROSCOPY", 3.2, "MNGTEGPNFYVPFSNATGVVRSPQYPGQAEIERYVFLVAMIFIFPILTLCGNGLVITVYTKLRTPTNYYFLSLNCADLAVGLFVMPSIATLALTDRHRYICQPLHYALVTSHTSMNMVSIAADRYVAITKPLRYLVTLTTRAKMVIVMVWIVSGLVSFLPQLVWRWY", "2026-03-05", 1, 348),
        ("7ANT", "Antibody IgG1", "Homo sapiens", "X-RAY DIFFRACTION", 2.0, "QVQLVQSGAEVKKPGASVKVSCKASGYTFTSYWMHWVRQAPGQGLEWMGRIDPANGNTKYAQKFQGRVTITADKSTSTAYMELSSLRSEDTAVYYCARSGYYYDSSLRFDYWGQGTLVTVSS", "2025-08-30", 2, 120),
        ("8CAT", "Catalase", "Aspergillus niger", "X-RAY DIFFRACTION", 2.3, "MSTAGKIVNKHNFAFFAKTLNGGGAMNIPGLSLETAVSLFKDGAGTAFRYRAHQGTVERFVDTAQGFLREQDVAQALKSLNVSRPQLEKIVKELLNKHPIKTHLSQHPQLEDPEAMASLLTDATLVKDPSQTAYPQDITYTDQFQPHAVASWHDNADGAKRPIMPHVGRQIEELNVTDFNNFFAKTLLASHFSKAVTKESDSDVIPCIDEYEPEDTRQVVQIASGNINKAGTYLHMGTDHPHAETLYQSADFVDTLKMAKADYVQVHNVFQNTFEQFKLMVTTFDRRHMPYVNTDPVNHFIDWTTTCEKDRVDGKGPVQDIQLFEIDQALQAEVYNSKEHDLVVQYNHTYHAQHLGDSSDRPIAQYHAAYVNFKAGYDVTTAFTNGIPKDGQPFTRDQLAGLGLVTPIQKRMHCQFSTPNIPDHVHQRGSFLAEALAQCNNLKVSVIGATGILAYSDNGCGRIMTVEGGLNDRAYHGTDKFVPDKPISQHAAYFSNVKA", "2026-01-22", 4, 498),
        ("9LAC", "Lactose Binding Protein", "Escherichia coli", "X-RAY DIFFRACTION", 1.8, "MKKTAIAIAVALAGFATVAQAAPKTDNTQELLVTIIGDELTAVQDSANIGISVADGTYQVPLGEREVLELADNEDFIPTQKVVSTGKTVEAMLAIGDYKGILKVATEEHPISLEELKAVKDGTLILHFTQDMKQVAENLFPFTIIGQLQAGADLVMLELMKGHEE", "2025-10-14", 1, 192),
        ("10MEM", "Aquaporin-1", "Homo sapiens", "ELECTRON MICROSCOPY", 3.8, "MARELNVTGHLLEGLVVTSLAFAVSRGTSWGHIQPAVTLVCLMGTQISIGRSLAAVQNLAQAGADWTLAPRILAVGVLAVGLGLLETGSGAMNPARGPAVTPLHIINPAVTQAFGISWQALNVFFSTGPIMMGANAMAFLQEQTTSGHFNPAVSLAQASVVGHIHGLVLGDVMTLTVAAQLLGAIPEEMRPFVSFADVPGLAALAVTLQLVISFVPEAMI", "2026-02-18", 4, 269),
        ("11VIR", "Capsid Protein", "Human rhinovirus 14", "X-RAY DIFFRACTION", 3.0, "MGQVEDLNAETVTGFLAMTDGSSGSGKPIQVPGTGHYRVPYNTVQAGPQDGNTGFTGLDLEDDVCKNGTILYPGTDYTVNNIQEGRDKCRLHITLTQPGTDIIEIPNMQGEQACRYSNPPGTICDWDNTKTITYTNDGCSTVGAGLYTGDNVTIDPDSRPSVTLTPEDVFI", "2025-11-05", 1, 211),
        ("12TOX", "Botulinum Toxin", "Clostridium botulinum", "X-RAY DIFFRACTION", 2.6, "MKFSTLKDFNEMLDPNKEMKLNTGFIPLSAGNLEPQLEKILDKLAEYYPEIRIGEKKNRVDFKVIKIYDGSNQYIETKFDGKPVFTDLNVVDEAIKYATEENYFNKIKYNVRDYIAEITKENFRSTLAEIENVARKIWYYKNLGVEVVTQNPKDGTFYDGFNFDNLSSMDEMKQIENELNDITVSADYNKGNQISQNYLMKYKNSWYNKMWKCKDR", "2026-03-10", 1, 298),
        ("13STR", "Streptavidin", "Streptomyces avidinii", "X-RAY DIFFRACTION", 1.6, "MSSAIYDIGGTLSREENLLVLEGSRHLAGFNPFCEYIYSGTYGDGTTATVSTQTDVNVTAAYNVTGQTGEFSVPSSGLFEFKNKHPGDFTDIHGTAVEAVQNAQIDAVEAGQYNVAFN", "2025-07-19", 4, 139),
        ("14FER", "Ferritin", "Homo sapiens", "X-RAY DIFFRACTION", 2.2, "MSLHFILQKNWAKISKRQESEEERLLDKFLKDGATITTEELFSECHTTQLSEFHSAKSKAEFQPDGLSEAFTQHLDKLVKEKLKADEETYFEKLAEHENAAFSIYHAERY", "2026-01-05", 24, 183),
        ("15COL", "Collagen Type I Alpha 1", "Homo sapiens", "X-RAY DIFFRACTION", 1.9, "MFSFVDLRLLLLLAATALLTHGQEAQPGADGRDGPAGPPGPQGPRGDAGPPGAPGPPGPPGPPGPPGLAGNPGADGQPGAKGEPGDAGAKGDAGPPGAPGPPGPPGPPGPPGLQGPPGPPGPPGPP", "2025-12-25", 3, 101),
        ("16KER", "Keratin Type I", "Homo sapiens", "X-RAY DIFFRACTION", 2.4, "MSSMSTFGGVGGFVGGGCSSSCGGGGCGRGGGGCGLGGGGCGRGSSCSTSCGSCWYGGGGC", "2026-02-28", 1, 68),
        ("17ACT", "Actin", "Oryza sativa", "X-RAY DIFFRACTION", 2.1, "MDCDEIALTLGGSTMCKAGFAGDDAPRAVFPSIVGRPRHQGVMVGMGQKDSYVGDEAQSKRGILTLKYPIEHGIVTNWDDMEKIWHHTFYNELRVAPEEHPVLLTEAPLNPKANREKMTQIMFETFNTPAMYVAIQAVLSLYASGRTTIVLDSGDGSGTHVPPYEHGIALTDLAVRMFPAFPKAVFPPSISGHRIFDVAVMEVRGKKEFAPSLYVSVLI", "2025-09-29", 1, 377),
        ("18TUB", "Tubulin Alpha", "Sus scrofa", "X-RAY DIFFRACTION", 3.5, "MREIVHIQAGQCGNQIGAKFWEVISDEHGIDPTGSYHDSQLQEISINTEIETPSERQKKLVFFQYFQATINAKINTNDDARFFLVCALCPPFDHDRQLLVMASTIRIADNIAKFLTQQRTGVPKWFVETWTGVDGVPFIPNSLLSPDSSVCSSIVEYLPETLEDKCKIYEAFDVDNASSGLKESQGVTPEEMTEECEQIEGFFEAIVDANTVLVSLFLN", "2026-03-15", 2, 356),
        ("19MYO", "Myosin Motor Domain", "Dictyostelium discoideum", "ELECTRON MICROSCOPY", 4.0, "MSELEDLQELFEKYVNEKLQKYKEEIEELEEKIKELESELRELEQKLEKELAELEEKIEELEEKFEQLESKLEEKIAELEEKKQELLEEKLEKLAEELEEKVAKLEEELEELLEKKLAELEEELEERLEERLEELKKKQEELEEKLEEREEKLEEKLEEKLEQKLEELEEKRLEELQEKLEQKKEELEE", "2025-10-30", 1, 200),
        ("20CAL", "Calmodulin", "Homo sapiens", "X-RAY DIFFRACTION", 1.7, "MADQLTEEQIAEFKEAFSLFDKDGDGTITTKELGTVMRSLGQNPTEAELQDMINEVDADGNGTIDFPEFLTMMARKMKDTDSEEEIREAFRVFDKDGNGYISAAELRHVMTNLGEKLTDEEVDEMIREADIDGDGQVNYEEFVQMMTAK*", "2026-01-12", 1, 149),
    ]
    await db.executemany("INSERT INTO proteins VALUES (?,?,?,?,?,?,?,?,?,?)", proteins)

@app.on_event("startup")
async def startup():
    await init_db()

# ==================== WEB PAGES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, search: Optional[str] = Query(None)):
    db = await get_db()
    if search:
        query = """SELECT * FROM proteins 
                   WHERE id LIKE ? OR name LIKE ? OR organism LIKE ? 
                   ORDER BY id LIMIT 100"""
        pattern = f"%{search}%"
        async with db.execute(query, (pattern, pattern, pattern)) as cursor:
            proteins = await cursor.fetchall()
    else:
        async with db.execute("SELECT * FROM proteins ORDER BY date DESC LIMIT 20") as cursor:
            proteins = await cursor.fetchall()
    await db.close()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "proteins": proteins,
        "search": search or ""
    })

@app.get("/pdb/{pdb_id}", response_class=HTMLResponse)
async def detail(request: Request, pdb_id: str):
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    return templates.TemplateResponse("detail.html", {
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
    async with db.execute("SELECT AVG(resolution) as avg_res FROM proteins") as cursor:
        avg_res = (await cursor.fetchone())["avg_res"]
    async with db.execute("SELECT method, COUNT(*) as count FROM proteins GROUP BY method ORDER BY count DESC") as cursor:
        method_dist = await cursor.fetchall()
    async with db.execute("SELECT organism, COUNT(*) as count FROM proteins GROUP BY organism ORDER BY count DESC LIMIT 10") as cursor:
        organism_dist = await cursor.fetchall()
    await db.close()
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "total": total,
        "methods": methods,
        "avg_res": round(avg_res, 2) if avg_res else 0,
        "method_dist": method_dist,
        "organism_dist": organism_dist
    })

# ==================== REST API ====================

@app.get("/api/v1/proteins", response_class=JSONResponse)
async def api_list_proteins(
    search: Optional[str] = Query(None, description="Search by ID, name, or organism"),
    method: Optional[str] = Query(None, description="Filter by experimental method"),
    min_resolution: Optional[float] = Query(None, description="Minimum resolution in Angstroms"),
    max_resolution: Optional[float] = Query(None, description="Maximum resolution in Angstroms"),
    organism: Optional[str] = Query(None, description="Filter by organism"),
    limit: int = Query(50, ge=1, le=500, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    db = await get_db()
    conditions = []
    params = []
    
    if search:
        conditions.append("(id LIKE ? OR name LIKE ? OR organism LIKE ?)")
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern])
    
    if method:
        conditions.append("method = ?")
        params.append(method)
    
    if organism:
        conditions.append("organism LIKE ?")
        params.append(f"%{organism}%")
    
    if min_resolution is not None:
        conditions.append("resolution >= ?")
        params.append(min_resolution)
    
    if max_resolution is not None:
        conditions.append("resolution <= ?")
        params.append(max_resolution)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT * FROM proteins WHERE {where_clause} ORDER BY id LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with db.execute(query, params) as cursor:
        proteins = [dict(row) async for row in cursor]
    
    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM proteins WHERE {where_clause}"
    async with db.execute(count_query, params[:-2]) as cursor:
        total = (await cursor.fetchone())["total"]
    
    await db.close()
    
    return {
        "data": proteins,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    }

@app.get("/api/v1/proteins/search", response_class=JSONResponse)
async def api_search(q: str = Query(..., min_length=1, description="Search query")):
    """Full-text search across all protein fields"""
    db = await get_db()
    query = """SELECT *, 
               (CASE 
                   WHEN id LIKE ? THEN 3
                   WHEN name LIKE ? THEN 2
                   WHEN organism LIKE ? THEN 1
                   ELSE 0
               END) as relevance
               FROM proteins 
               WHERE id LIKE ? OR name LIKE ? OR organism LIKE ? OR sequence LIKE ?
               ORDER BY relevance DESC, id
               LIMIT 50"""
    pattern = f"%{q}%"
    async with db.execute(query, (pattern, pattern, pattern, pattern, pattern, pattern, pattern)) as cursor:
        proteins = [dict(row) async for row in cursor]
        # Remove relevance field from results
        for p in proteins:
            p.pop("relevance", None)
    await db.close()
    return {"results": proteins, "count": len(proteins)}

@app.get("/api/v1/proteins/{pdb_id}", response_class=JSONResponse)
async def api_get_protein(pdb_id: str):
    """Get detailed information for a specific protein"""
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    return dict(protein)

@app.get("/api/v1/proteins/{pdb_id}/fasta", response_class=JSONResponse)
async def api_get_fasta(pdb_id: str):
    """Get protein sequence in FASTA format"""
    db = await get_db()
    async with db.execute("SELECT * FROM proteins WHERE id = ?", (pdb_id.upper(),)) as cursor:
        protein = await cursor.fetchone()
    await db.close()
    if not protein:
        raise HTTPException(status_code=404, detail=f"Protein {pdb_id} not found")
    protein = dict(protein)
    fasta = f">{protein['id']} {protein['name']}|{protein['organism']}\n{protein['sequence']}"
    return {"format": "FASTA", "data": fasta, "pdb_id": protein["id"]}

@app.get("/api/v1/stats", response_class=JSONResponse)
async def api_stats():
    """Get database statistics"""
    db = await get_db()
    
    # Total count
    async with db.execute("SELECT COUNT(*) as total FROM proteins") as cursor:
        total = (await cursor.fetchone())["total"]
    
    # Average resolution
    async with db.execute("SELECT AVG(resolution) as avg_res, MIN(resolution) as min_res, MAX(resolution) as max_res FROM proteins") as cursor:
        res_stats = await cursor.fetchone()
    
    # Method distribution
    async with db.execute("SELECT method, COUNT(*) as count FROM proteins GROUP BY method ORDER BY count DESC") as cursor:
        method_dist = [dict(row) async for row in cursor]
    
    # Organism distribution
    async with db.execute("SELECT organism, COUNT(*) as count FROM proteins GROUP BY organism ORDER BY count DESC LIMIT 10") as cursor:
        organism_dist = [dict(row) async for row in cursor]
    
    # Recent entries
    async with db.execute("SELECT id, name, date FROM proteins ORDER BY date DESC LIMIT 5") as cursor:
        recent = [dict(row) async for row in cursor]
    
    await db.close()
    
    return {
        "total_entries": total,
        "resolution": {
            "average": round(res_stats["avg_res"], 2) if res_stats["avg_res"] else 0,
            "min": res_stats["min_res"],
            "max": res_stats["max_res"]
        },
        "methods": method_dist,
        "top_organisms": organism_dist,
        "recent_entries": recent
    }

@app.get("/api/v1/download/fasta", response_class=JSONResponse)
async def api_download_all_fasta():
    """Download all protein sequences in FASTA format"""
    db = await get_db()
    async with db.execute("SELECT * FROM proteins ORDER BY id") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    
    fasta_entries = []
    for p in proteins:
        fasta_entries.append(f">{p['id']} {p['name']}|{p['organism']}\n{p['sequence']}")
    
    return {
        "format": "FASTA",
        "count": len(proteins),
        "data": "\n".join(fasta_entries)
    }

@app.get("/api/v1/download/json", response_class=JSONResponse)
async def api_download_all_json():
    """Download all protein data in JSON format"""
    db = await get_db()
    async with db.execute("SELECT * FROM proteins ORDER BY id") as cursor:
        proteins = [dict(row) async for row in cursor]
    await db.close()
    return {"proteins": proteins, "count": len(proteins), "exported_at": datetime.now().isoformat()}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}
