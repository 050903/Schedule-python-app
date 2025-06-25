# EpiMap X - Advanced EWAS Platform

## 🧬 Tầm nhìn chiến lược
EpiMap X là nền tảng phân tích EWAS (Epigenome-Wide Association Studies) tiên tiến, được thiết kế để biến đổi dữ liệu biểu sinh khổng lồ thành những hiểu biết y học có thể hành động.

## 🚀 Tính năng chính

### Phase 1: MVP ✅
- ✅ **Core EWAS Engine**: Linear regression analysis
- ✅ **File Management**: Upload/storage system
- ✅ **Background Processing**: Async analysis jobs
- ✅ **Visualization API**: Manhattan & QQ plot data
- ✅ **Results Management**: FDR correction, results table

### Phase 2: Advanced Features ✅
- ✅ **Mixed Linear Models**: Population structure correction
- ✅ **Robust Statistics**: HC3 standard errors, effect sizes
- ✅ **Gene Annotation**: Automatic CpG-to-gene mapping
- ✅ **Pathway Enrichment**: Functional analysis
- ✅ **Batch Analysis**: Multiple analyses workflow
- ✅ **Results Comparison**: Cross-analysis comparison
- ✅ **Advanced Corrections**: Bonferroni, FDR methods

### Phase 3: Enterprise Features 🔄
- 🔄 **Multi-omics Integration**: RNA-seq, genotype data
- 🔄 **Collaboration Tools**: User management, sharing
- 🔄 **Advanced Visualization**: Interactive plots
- 🔄 **Performance Optimization**: GPU acceleration
- 🔄 **Security**: HIPAA compliance

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React + MUI   │◄──►│   FastAPI       │◄──►│   SQLite/       │
│   Plotly.js     │    │   SQLModel      │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  File Storage   │
                       │  Local/MinIO    │
                       └─────────────────┘
```

## 📊 API Endpoints

### Core Analysis
- `POST /api/v1/files/upload/{type}` - Upload data files
- `POST /api/v1/analysis/ewas` - Submit basic EWAS
- `GET /api/v1/results/{id}/manhattan` - Manhattan plot data
- `GET /api/v1/results/{id}/qqplot_data` - QQ plot data

### Advanced Analysis
- `POST /api/v1/advanced/ewas-advanced` - Mixed model EWAS
- `POST /api/v1/advanced/annotate/{id}` - Gene annotation
- `GET /api/v1/advanced/pathway-enrichment/{id}` - Pathway analysis

### Batch Operations
- `POST /api/v1/batch/batch` - Submit batch analyses
- `GET /api/v1/batch/batch/{name}/status` - Batch status
- `GET /api/v1/batch/compare/{id1}/{id2}` - Compare results

## 🛠️ Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.11+
- Node.js 18+ (cho frontend)
- Docker (optional)

### Chạy Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Chạy Frontend
```bash
cd frontend-new
npm install
npm start
```

### Với Docker
```bash
docker-compose up -d
```

## 📈 Định dạng dữ liệu

### Epigenome Data (.tsv)
```
CpG_ID          Sample1    Sample2    Sample3
chr1:12345      0.45       0.67       0.23
chr2:67890      0.78       0.34       0.89
```

### Phenotype Data (.csv)
```
Sample_ID,disease_status,age,sex,batch
Sample1,1,45,M,batch1
Sample2,0,38,F,batch1
```

## 🧪 Test hệ thống

### Quick Test
```bash
cd epimap-x
python test_api.py
```

### Advanced Test
```bash
# Test batch analysis
curl -X POST "http://localhost:8000/api/v1/batch/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_name": "test_batch",
    "analyses": [
      {
        "epigenome_file_id": 1,
        "phenotype_file_id": 2,
        "phenotype_column": "disease_status",
        "covariates": ["age", "sex"]
      }
    ]
  }'
```

## 📊 Phân tích thống kê

### Supported Models
- **Linear Regression**: Basic EWAS analysis
- **Mixed Linear Models**: Population structure correction
- **Robust Regression**: HC3 standard errors

### Multiple Testing Corrections
- **FDR**: Benjamini-Hochberg procedure
- **Bonferroni**: Conservative correction
- **Custom**: User-defined thresholds

### Effect Size Metrics
- **Beta coefficients**: Methylation effect size
- **Cohen's d**: Standardized effect size
- **Confidence intervals**: Statistical precision

## 🔬 Use Cases

### Clinical Research
- Disease biomarker discovery
- Treatment response prediction
- Population health studies

### Pharmaceutical
- Drug target identification
- Toxicity assessment
- Personalized medicine

### Academic Research
- Aging studies
- Environmental epigenetics
- Developmental biology

## 🤝 Đóng góp

### Development Workflow
1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

### Code Standards
- Python: Black formatting, type hints
- JavaScript: ESLint, Prettier
- Documentation: Comprehensive docstrings

## 📄 License
MIT License - See LICENSE file for details

## 📞 Hỗ trợ
- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Email: support@epimap-x.com

---

**EpiMap X** - Transforming epigenomic data into actionable medical insights 🧬✨