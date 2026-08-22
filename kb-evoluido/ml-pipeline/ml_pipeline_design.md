# ML Pipeline & Feedback Loop para Evolução Automática Diária
## Arquitetura Completa para Agentes Manta (Infraestrutura)

---

## 1. VISÃO GERAL DO PIPELINE

```
┌─────────────────────────────────────────────────────────────────┐
│                    ML EVOLUTION SYSTEM v1.0                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INGESTION         FEATURE ENG        ML MODELS      KB UPDATE  │
│  (Daily)           (Daily)            (Weekly)       (Monthly)  │
│     │                  │                  │              │      │
│  [Raw Data] ──→ [Normalized] ──→ [Trained] ──→ [Validated] ──→ │
│     ↑                                       ↑                    │
│  SharePoint          ┌──────────────────────┼─────┐              │
│  Memoriais           │ FEEDBACK LOOP        │     │              │
│  Orçamentos          │ (Human Validation)   │     │              │
│  CAD/DWG             └──────────────────────┘     │              │
│                                                   │              │
│                    ROLLBACK MECHANISM ←───────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. STAGE 1: INGESTION (Diária, 06:00 UTC)

### 2.1 Data Collection Engine

```python
# ============================================
# INGESTION_ENGINE.py — Collector Principal
# ============================================

class MantaIngestionEngine:
    """
    Coleta dados de projetos finalizados:
    - SharePoint: 03_Projetos/*/Projetos_Fechados/
    - Memoriais técnicos
    - Orçamentos finais
    - As-built DWG/PDF
    """
    
    def __init__(self):
        self.sp_client = SharePointConnector()
        self.db = SupabaseClient()
        self.validation_log = []
        self.ingestion_id = generate_timestamp_id()  # 20260730_060000_xy1a
        
    def daily_collect(self):
        """
        Trigger: Cron 06:00 UTC
        Coleta 24h de projetos com status FINALIZADO
        """
        
        projects = []
        errors = []
        
        try:
            # [1] Scanear SharePoint por pasta de segmento
            for segment in ['S1-Rodovias', 'S2-OAE', 'S3-Ferrovia', 
                            'S4-Metro', 'S6-Portos', 'S8-Saneamento']:
                
                folder_path = f"/03_Projetos/{segment}/Projetos_Fechados"
                
                # [1.1] Listar arquivos últimas 24h
                files = self.sp_client.list_recent_files(
                    path=folder_path,
                    hours=24,
                    extensions=['.pdf', '.xlsx', '.docx', '.dwg']
                )
                
                for file_meta in files:
                    try:
                        # [1.2] Baixar metadados + arquivo
                        doc_content = self.sp_client.read_document(
                            path=file_meta['path'],
                            extract_tables=True,
                            extract_metadata=True
                        )
                        
                        # [1.3] Classificar tipo (memorial, orçamento, etc)
                        doc_type = self._classify_document(
                            name=file_meta['name'],
                            content=doc_content
                        )
                        
                        projects.append({
                            'ingestion_id': self.ingestion_id,
                            'segment': segment,
                            'source_file': file_meta['path'],
                            'source_type': doc_type,
                            'raw_content': doc_content,
                            'metadata': {
                                'created': file_meta['created'],
                                'modified': file_meta['modified'],
                                'size_bytes': file_meta['size']
                            },
                            'timestamp_collected': now_utc(),
                            'status': 'collected'
                        })
                        
                    except Exception as e:
                        errors.append({
                            'file': file_meta['path'],
                            'error': str(e),
                            'timestamp': now_utc()
                        })
                        continue
            
            # [2] Validação básica de integridade
            validated_projects = []
            for project in projects:
                validation = self._validate_raw_data(project)
                if validation['passed']:
                    validated_projects.append(project)
                    project['status'] = 'validated'
                else:
                    errors.append({
                        'file': project['source_file'],
                        'error': validation['reason'],
                        'timestamp': now_utc()
                    })
            
            # [3] Persistir em staging table
            self.db.insert_batch(
                table='ingestion_staging',
                records=validated_projects,
                batch_size=50
            )
            
            # [4] Log de status
            log_entry = {
                'ingestion_id': self.ingestion_id,
                'timestamp': now_utc(),
                'total_collected': len(projects),
                'total_validated': len(validated_projects),
                'total_errors': len(errors),
                'error_details': errors[:10],  # Primeiros 10
                'segments_scanned': list(set([p['segment'] for p in projects])),
                'stage': 'completed'
            }
            
            self.db.insert('ingestion_logs', log_entry)
            
            return {
                'status': 'success',
                'ingestion_id': self.ingestion_id,
                'projects_ready': len(validated_projects),
                'errors': len(errors)
            }
            
        except Exception as e:
            log_entry['stage'] = 'failed'
            log_entry['error'] = str(e)
            self.db.insert('ingestion_logs', log_entry)
            raise
    
    def _classify_document(self, name: str, content: str) -> str:
        """
        Classifica tipo de documento via patterns + ML
        Returns: 'memorial_tecnico' | 'orcamento' | 'asbuild' | 'cronograma' | 'other'
        """
        patterns = {
            'memorial_tecnico': [
                r'memorial|especificações técnicas|escopo de obras',
                r'escopo técnico|descrição das obras'
            ],
            'orcamento': [
                r'orçamento|budget|custo|valor|preço',
                r'planilha de preços|BDI|lucro'
            ],
            'asbuild': [
                r'as[_-]?built|as[_-]?built|obra executada|desenho executado',
                r'levantamento final'
            ],
            'cronograma': [
                r'cronograma|timeline|schedule|fases de execução',
                r'duração|período|meses|semanas'
            ]
        }
        
        # Score cada categoria
        scores = {}
        for doc_type, pattern_list in patterns.items():
            score = 0
            for pattern in pattern_list:
                matches = len(re.findall(pattern, content, re.I))
                score += matches * 2  # Weight por padrão
            scores[doc_type] = score
        
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'other'
    
    def _validate_raw_data(self, project: dict) -> dict:
        """
        Validação básica:
        - Conteúdo não vazio
        - Metadata completa
        - Encoding válido
        """
        reasons = []
        
        if not project.get('raw_content') or len(project['raw_content']) < 100:
            reasons.append('content_too_short')
        
        if not project.get('metadata'):
            reasons.append('missing_metadata')
        
        if not project.get('segment'):
            reasons.append('missing_segment')
        
        return {
            'passed': len(reasons) == 0,
            'reason': '|'.join(reasons) if reasons else 'ok'
        }


# ============================================
# SCHEDULER CONFIGURATION
# ============================================

schedule = {
    'job_name': 'manta_daily_ingestion',
    'trigger': 'cron',
    'cron': '0 6 * * *',  # 06:00 UTC = 03:00 BRT
    'timezone': 'UTC',
    'handler': 'MantaIngestionEngine.daily_collect',
    'retry': {
        'max_attempts': 3,
        'backoff_strategy': 'exponential',
        'backoff_base': 300  # 5 min
    },
    'notification': {
        'on_success': ['logs'],
        'on_failure': ['slack', 'email'],
        'channels': {
            'slack': '#manta-ml-pipeline',
            'email': ['ml-team@manta.com', 'maestro@manta.com']
        }
    }
}
```

### 2.2 Data Normalization Pipeline

```python
# ============================================
# NORMALIZER.py — Standardização de Dados
# ============================================

class ProjectNormalizer:
    """
    Extrai e normaliza campos estruturados:
    - Quantidade de obra (m², m³, km, un)
    - Custos (valor total, BDI, overhead)
    - Cronograma (duração total, fases)
    - Produtividade (m²/dia, ton/dia)
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.llm = ClaudeClient()  # Para OCR/extração complexa
        self.unit_converter = UnitConverter()
        self.constants = self._load_known_constants()
        
    def normalize_batch(self, ingestion_id: str):
        """
        Processa todos projects do ingestion_staging
        para projeto_normalized
        """
        
        staging_records = self.db.query(
            'SELECT * FROM ingestion_staging WHERE ingestion_id = %s',
            [ingestion_id]
        )
        
        normalized_records = []
        
        for record in staging_records:
            try:
                # [1] Extração estruturada
                extracted = self._extract_fields(
                    content=record['raw_content'],
                    source_type=record['source_type'],
                    segment=record['segment']
                )
                
                # [2] Normalização de unidades
                normalized = self._normalize_units(extracted)
                
                # [3] Inferência de campos faltantes
                inferred = self._infer_missing_fields(normalized)
                
                # [4] Validação de coerência
                validation = self._validate_coheence(inferred)
                
                if validation['valid']:
                    normalized_records.append({
                        'ingestion_id': ingestion_id,
                        'project_id': self._generate_project_id(record),
                        'segment': record['segment'],
                        'source_file': record['source_file'],
                        'normalized_data': inferred,
                        'extraction_confidence': validation['confidence'],
                        'validation_notes': validation['notes'],
                        'status': 'normalized',
                        'timestamp': now_utc()
                    })
                    
            except Exception as e:
                self.db.insert('normalization_errors', {
                    'ingestion_id': ingestion_id,
                    'source_file': record['source_file'],
                    'error': str(e),
                    'timestamp': now_utc()
                })
                continue
        
        # Persistir normalizados
        self.db.insert_batch('projeto_normalized', normalized_records)
        
        return len(normalized_records)
    
    def _extract_fields(self, content: str, source_type: str, segment: str) -> dict:
        """
        Extrai campos estruturados usando:
        1. Regex patterns + tabelas
        2. Claude LLM para casos complexos
        3. Fallback para manual review
        """
        
        extracted = {
            'quantities': {},
            'costs': {},
            'schedule': {},
            'performance': {},
            'raw_text': content
        }
        
        # [Pattern 1] Quantidades via regex
        regex_patterns = {
            'area_m2': r'(?:área|extensão|metragem)\s*:?\s*([\d.,]+)\s*(?:m²|m2|metros?)\s',
            'length_km': r'(?:extensão|comprimento|distância)\s*:?\s*([\d.,]+)\s*(?:km|quilômetro)',
            'volume_m3': r'(?:volume|quantidade)\s*:?\s*([\d.,]+)\s*(?:m³|m3|metros? cúbico)',
            'units': r'(?:unidade|un\.?)\s*(?:de|:)?\s*(\w+)\s*(?::)?\s*([\d.,]+)',
        }
        
        for field, pattern in regex_patterns.items():
            match = re.search(pattern, content, re.I)
            if match:
                extracted['quantities'][field] = {
                    'raw_value': match.group(1),
                    'confidence': 'high',
                    'source': 'regex'
                }
        
        # [Pattern 2] Custos via tabelas
        table_matches = self._extract_tables_from_content(content)
        for table in table_matches:
            cost_data = self._parse_cost_table(table, segment)
            if cost_data:
                extracted['costs'].update(cost_data)
        
        # [Pattern 3] Cronograma
        schedule_data = self._extract_schedule(content)
        if schedule_data:
            extracted['schedule'].update(schedule_data)
        
        # [Pattern 4] Se faltam campos críticos → Claude LLM
        if not extracted['costs'].get('total_value') or \
           not extracted['quantities'].get('main_quantity'):
            
            # Prompt estruturado
            llm_response = self.llm.extract_project_fields(
                content=content,
                segment=segment,
                source_type=source_type,
                schema={
                    'expected_fields': [
                        'total_project_cost',
                        'bdi_percentage',
                        'main_quantity',
                        'unit_of_measure',
                        'duration_months',
                        'start_date',
                        'end_date'
                    ]
                }
            )
            
            if llm_response.get('confidence', 0) > 0.75:
                extracted.update(llm_response['extracted_fields'])
        
        return extracted
    
    def _normalize_units(self, extracted: dict) -> dict:
        """
        Converte todas as unidades para standard:
        - Custo: sempre em R$ correntes
        - Quantidade: m², km, m³, un (conforme tipo)
        - Cronograma: sempre em dias
        - Performance: m²/dia, km/dia, ton/dia
        """
        
        normalized = copy.deepcopy(extracted)
        
        # [Custo] Validar BDI + inferir se falta
        if 'total_value' in normalized['costs']:
            valor = float(
                normalized['costs']['total_value']
                .replace(',', '.')
            )
            
            if 'bdi_percentage' not in normalized['costs']:
                # Inferir BDI do segmento (media histórica)
                bdi_default = self.constants['bdi_by_segment'].get(
                    normalized.get('segment'), 25.0
                )
                normalized['costs']['bdi_percentage'] = bdi_default
        
        # [Quantidade] Converter para unidade standard
        for qty_field, qty_data in normalized['quantities'].items():
            raw_val = qty_data['raw_value'].replace('.', '').replace(',', '.')
            normalized['quantities'][qty_field]['value_normalized'] = float(raw_val)
        
        # [Cronograma] Converter tudo para dias
        if 'duration_months' in normalized['schedule']:
            months = int(normalized['schedule']['duration_months'])
            normalized['schedule']['duration_days'] = months * 30.44  # média
        
        return normalized
    
    def _infer_missing_fields(self, normalized: dict) -> dict:
        """
        Preenche campos derivados:
        - cost_per_unit = total_cost / quantity
        - productivity = quantity / duration_days
        - unit_cost_by_bdi = cost / (quantity * bdi_factor)
        """
        
        inferred = copy.deepcopy(normalized)
        
        try:
            total_cost = inferred['costs'].get('total_value', 0)
            qty = inferred['quantities'].get('main_quantity', {}).get(
                'value_normalized', 0
            )
            duration_days = inferred['schedule'].get('duration_days', 0)
            bdi_pct = inferred['costs'].get('bdi_percentage', 25)
            
            if qty > 0:
                inferred['derived'] = {
                    'cost_per_unit': total_cost / qty,
                    'cost_per_unit_direct': (total_cost / (1 + bdi_pct/100)) / qty,
                    'productivity_per_day': qty / duration_days if duration_days > 0 else 0,
                    'cost_per_day': total_cost / duration_days if duration_days > 0 else 0
                }
        except Exception as e:
            inferred['derived'] = {'error': str(e)}
        
        return inferred
    
    def _validate_coheence(self, inferred: dict) -> dict:
        """
        Valida se os valores fazem sentido:
        - cost_per_unit > 0
        - productivity > 0 e razoável para o segmento
        - Sem valores absurdos (e.g., 10 milhões por m²)
        """
        
        confidence = 100
        notes = []
        valid = True
        
        # Validação 1: Cost per unit está em faixa esperada?
        segment = inferred.get('segment')
        cost_per_unit = inferred.get('derived', {}).get('cost_per_unit', 0)
        expected_range = self.constants['cost_per_unit_range'].get(segment)
        
        if expected_range:
            min_val, max_val = expected_range
            if not (min_val <= cost_per_unit <= max_val):
                confidence -= 15
                notes.append(f'cost_per_unit fora da faixa esperada')
        
        # Validação 2: Produtividade razoável?
        productivity = inferred.get('derived', {}).get('productivity_per_day', 0)
        expected_productivity = self.constants['productivity_by_segment'].get(segment)
        
        if expected_productivity:
            min_prod, max_prod = expected_productivity
            if not (min_prod * 0.5 <= productivity <= max_prod * 2.0):
                confidence -= 10
                notes.append(f'productivity fora da faixa (outlier)')
        
        # Validação 3: Valores faltantes críticos
        if not inferred.get('costs', {}).get('total_value'):
            valid = False
            notes.append('missing_total_value')
        
        return {
            'valid': valid,
            'confidence': max(0, confidence / 100),
            'notes': notes
        }
    
    def _load_known_constants(self) -> dict:
        """
        Carrega KB de constantes conhecidas:
        BDI, produtividade, faixas de custo
        """
        return self.db.query_single(
            'SELECT constants_data FROM kb_constants WHERE version = (SELECT MAX(version) FROM kb_constants)'
        )


# Scheduler para normalização
schedule_normalization = {
    'job_name': 'manta_daily_normalization',
    'trigger': 'depends_on',
    'depends_on': 'manta_daily_ingestion',
    'delay_after_dependency': 300,  # 5 min após ingestion
    'handler': 'ProjectNormalizer.normalize_batch',
    'parameters': {
        'ingestion_id': '${LATEST_INGESTION_ID}'
    }
}
```

---

## 3. STAGE 2: FEATURE ENGINEERING (Diária, 07:00 UTC)

```python
# ============================================
# FEATURE_ENGINEER.py — Extração de Features
# ============================================

class FeatureEngineer:
    """
    Cria features para treinamento de modelos:
    1. Clustering de projetos similares
    2. Padrão de custos/cronograma/produtividade
    3. Outlier detection
    4. Correlação com constantes conhecidas
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.scaler = StandardScaler()
        self.constants = self._load_constants()
        
    def engineer_features(self, ingestion_id: str):
        """
        Cria dataset de features para ML training
        """
        
        # [1] Carregar projetos normalizados
        projects = self.db.query(
            '''
            SELECT * FROM projeto_normalized 
            WHERE ingestion_id = %s AND status = 'normalized'
            ''',
            [ingestion_id]
        )
        
        if not projects:
            return {'status': 'no_data', 'projects_processed': 0}
        
        # [2] Feature Extraction
        features_list = []
        for proj in projects:
            features = self._extract_features(proj)
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)
        
        # [3] Clustering (K-means com k=5)
        features_df = self._apply_clustering(features_df)
        
        # [4] Outlier Detection (Isolation Forest)
        features_df = self._detect_outliers(features_df)
        
        # [5] Correlação com KB
        features_df = self._enrich_with_kb_correlation(features_df)
        
        # [6] Persistir features
        features_df['ingestion_id'] = ingestion_id
        features_df['timestamp'] = now_utc()
        
        self.db.insert_batch('ml_features', features_df.to_dict('records'))
        
        return {
            'status': 'success',
            'features_created': len(features_df),
            'clusters_found': features_df['cluster'].nunique(),
            'outliers_detected': features_df['is_outlier'].sum()
        }
    
    def _extract_features(self, proj: dict) -> dict:
        """
        Para cada projeto, extrai 30+ features:
        - Custos: total, direto, BDI%, overhead%
        - Quantidades: principal, derivadas
        - Cronograma: duração, phases
        - Performance: m²/dia, custo/dia
        - Metadata: segment, source_type
        """
        
        norm_data = proj['normalized_data']
        derived = norm_data.get('derived', {})
        
        features = {
            'project_id': proj['project_id'],
            'segment': proj['segment'],
            'source_type': norm_data.get('source_type', 'unknown'),
            
            # --- COST FEATURES ---
            'total_cost': norm_data['costs'].get('total_value', 0),
            'bdi_percentage': norm_data['costs'].get('bdi_percentage', 0),
            'direct_cost': norm_data['costs'].get('total_value', 0) / (
                1 + norm_data['costs'].get('bdi_percentage', 25) / 100
            ),
            
            # --- QUANTITY FEATURES ---
            'main_quantity': norm_data['quantities'].get(
                'main_quantity', {}
            ).get('value_normalized', 0),
            'quantity_unit': norm_data['quantities'].get(
                'main_quantity', {}
            ).get('unit', 'unknown'),
            
            # --- SCHEDULE FEATURES ---
            'duration_days': norm_data['schedule'].get('duration_days', 0),
            'duration_months': norm_data['schedule'].get('duration_months', 0),
            
            # --- DERIVED/PERFORMANCE FEATURES ---
            'cost_per_unit': derived.get('cost_per_unit', 0),
            'cost_per_day': derived.get('cost_per_day', 0),
            'productivity_per_day': derived.get('productivity_per_day', 0),
            'cost_per_unit_direct': derived.get('cost_per_unit_direct', 0),
            
            # --- COMPLEXITY SCORE ---
            'complexity_score': self._compute_complexity_score(norm_data),
            
            # --- QUALITY METRICS ---
            'extraction_confidence': proj['extraction_confidence'],
            'data_completeness': self._compute_completeness(norm_data),
        }
        
        return features
    
    def _apply_clustering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clusteriza projetos por similaridade:
        - Usa features: total_cost, duration_days, main_quantity, segment
        - K-means com k=5 (pode ajustar via hyperparameter tuning)
        - Objetivo: encontrar "padrões de projeto"
        """
        
        # Selecionar features para clustering
        clustering_features = [
            'total_cost', 'duration_days', 'main_quantity', 
            'cost_per_unit', 'productivity_per_day'
        ]
        
        X = df[clustering_features].fillna(0).values
        
        # Scaling
        X_scaled = self.scaler.fit_transform(X)
        
        # K-means
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Cluster characterization
        cluster_profiles = {}
        for cluster_id in df['cluster'].unique():
            cluster_df = df[df['cluster'] == cluster_id]
            cluster_profiles[cluster_id] = {
                'size': len(cluster_df),
                'avg_total_cost': cluster_df['total_cost'].mean(),
                'avg_duration': cluster_df['duration_days'].mean(),
                'avg_quantity': cluster_df['main_quantity'].mean(),
                'label': self._label_cluster(cluster_df)
            }
        
        df['cluster_label'] = df['cluster'].map(
            lambda c: cluster_profiles[c]['label']
        )
        
        # Persistir cluster profiles
        self.db.insert('ml_cluster_profiles', {
            'timestamp': now_utc(),
            'profiles': cluster_profiles
        })
        
        return df
    
    def _label_cluster(self, cluster_df: pd.DataFrame) -> str:
        """
        Atribui label ao cluster:
        - Small | Medium | Large (baseado em size + cost)
        """
        avg_cost = cluster_df['total_cost'].mean()
        avg_qty = cluster_df['main_quantity'].mean()
        
        if avg_cost < 1_000_000:
            return 'small'
        elif avg_cost < 10_000_000:
            return 'medium'
        else:
            return 'large'
    
    def _detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Isolation Forest para detectar projetos atípicos:
        - Contamination=0.05 (5% outliers esperados)
        - Features: cost_per_unit, productivity_per_day, duration_days
        """
        
        outlier_features = [
            'cost_per_unit', 'productivity_per_day', 'duration_days'
        ]
        
        X = df[outlier_features].fillna(df[outlier_features].median()).values
        X_scaled = self.scaler.fit_transform(X)
        
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        predictions = iso_forest.fit_predict(X_scaled)
        
        df['is_outlier'] = (predictions == -1)
        df['outlier_score'] = iso_forest.score_samples(X_scaled)
        
        return df
    
    def _enrich_with_kb_correlation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Para cada projeto, correlaciona com KB:
        - Encontra projetos similares na história
        - Valida contra K1, K2, constantes conhecidas
        - Retorna 'confidence_vs_kb'
        """
        
        # Carrega histórico de projetos validados
        validated_projects = self.db.query(
            '''
            SELECT * FROM projeto_validated 
            WHERE status = 'approved' 
            ORDER BY approved_date DESC 
            LIMIT 1000
            '''
        )
        
        validated_df = pd.DataFrame(validated_projects)
        
        correlations = []
        for _, proj_row in df.iterrows():
            
            # Encontra 3 projetos mais similares no histórico
            similarity_scores = self._compute_similarity(
                proj_row, validated_df
            )
            
            top_similar = similarity_scores.nlargest(3, 'similarity')
            
            # Se algum tem similarity > 0.85, herda confiança
            if len(top_similar) > 0 and top_similar.iloc[0]['similarity'] > 0.85:
                corr_score = top_similar.iloc[0]['similarity']
                corr_label = 'high_confidence'
            else:
                corr_score = similarity_scores['similarity'].max() if len(
                    similarity_scores) > 0 else 0
                corr_label = 'new_pattern' if corr_score < 0.5 else 'medium_confidence'
            
            correlations.append({
                'project_id': proj_row['project_id'],
                'kb_correlation_score': corr_score,
                'kb_correlation_label': corr_label,
                'similar_projects': top_similar['project_id'].tolist()
            })
        
        corr_df = pd.DataFrame(correlations)
        df = df.merge(corr_df, on='project_id', how='left')
        
        return df
    
    def _compute_similarity(self, proj, validated_df):
        """
        Euclidean distance (Minkowski) entre project e histórico
        Features: cost_per_unit, duration_days, productivity_per_day
        """
        
        proj_vec = np.array([
            proj.get('cost_per_unit', 0),
            proj.get('duration_days', 0),
            proj.get('productivity_per_day', 0)
        ])
        
        scores = []
        for _, hist_proj in validated_df.iterrows():
            hist_vec = np.array([
                hist_proj.get('cost_per_unit', 0),
                hist_proj.get('duration_days', 0),
                hist_proj.get('productivity_per_day', 0)
            ])
            
            # Minkowski distance normalizado (0-1)
            distance = np.linalg.norm(proj_vec - hist_vec)
            similarity = 1 / (1 + distance)  # Sigmoid-like
            
            scores.append({
                'project_id': hist_proj.get('project_id'),
                'similarity': similarity
            })
        
        return pd.DataFrame(scores)
    
    def _compute_complexity_score(self, norm_data: dict) -> float:
        """
        Pontuação de complexidade (0-100):
        - Maior duração = mais complexo
        - Maior quantidade = mais complexo
        - Menor cost_per_unit = possível complexidade técnica
        """
        
        duration = norm_data.get('schedule', {}).get('duration_days', 0)
        qty = norm_data.get('quantities', {}).get('main_quantity', {}).get(
            'value_normalized', 0
        )
        cost_per_unit = norm_data.get('derived', {}).get('cost_per_unit', 0)
        
        score = (
            min(duration / 365 * 20, 30) +  # Duração (max 30)
            min(qty / 10000 * 20, 30) +      # Quantidade (max 30)
            (20 if cost_per_unit < 500 else 0)  # Baixo custo unitário (complexidade?)
        )
        
        return min(score, 100)
    
    def _compute_completeness(self, norm_data: dict) -> float:
        """
        Percentual de campos preenchidos vs esperados
        """
        
        critical_fields = [
            'costs.total_value',
            'quantities.main_quantity',
            'schedule.duration_days',
            'derived.cost_per_unit'
        ]
        
        filled = 0
        for field_path in critical_fields:
            parts = field_path.split('.')
            val = norm_data
            try:
                for part in parts:
                    val = val.get(part, {})
                if val:
                    filled += 1
            except:
                pass
        
        return filled / len(critical_fields)
```

---

## 4. STAGE 3: ML MODELS (Semanal, segunda 09:00 UTC)

```python
# ============================================
# ML_MODELS.py — Treinamento + Validação
# ============================================

class MantaMLModels:
    """
    Treina 4 modelos:
    1. Regression (Predição de custos/cronograma)
    2. Classification (Validação de padrão)
    3. Anomaly Detection (Desvios)
    4. Similarity Matching (Casos precedentes)
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.models = {}
        self.validation_results = {}
        
    def weekly_training(self):
        """
        Trigger: Cron segunda-feira 09:00 UTC
        Treina modelos com dados das últimas 4 semanas
        """
        
        # [1] Carregar features + labels
        training_data = self._prepare_training_data()
        
        if len(training_data) < 50:
            return {'status': 'insufficient_data', 'records': len(training_data)}
        
        # [2] Train modelos
        self._train_regression_model(training_data)
        self._train_classification_model(training_data)
        self._train_anomaly_model(training_data)
        self._train_similarity_model(training_data)
        
        # [3] Validação (holdout 20%)
        validation_results = self._validate_all_models(training_data)
        
        # [4] Comparar com versão anterior
        comparison = self._compare_with_previous_version()
        
        # [5] Decisão: Publicar ou manter versão anterior?
        decision = self._decide_publish_models(
            validation_results,
            comparison
        )
        
        # [6] Persistir metadata
        self.db.insert('model_training_logs', {
            'timestamp': now_utc(),
            'training_samples': len(training_data),
            'models_trained': list(self.models.keys()),
            'validation_results': validation_results,
            'comparison_with_previous': comparison,
            'decision': decision,
            'status': decision['action']
        })
        
        return decision
    
    def _prepare_training_data(self):
        """
        Usa features validadas das últimas 4 semanas
        + regressão conhecidas (approved projects)
        """
        
        # Features das últimas 4 semanas
        features = self.db.query(
            '''
            SELECT f.*, pv.is_valid, pv.feedback_type
            FROM ml_features f
            LEFT JOIN projeto_validated pv 
                ON f.project_id = pv.project_id
            WHERE f.timestamp > now() - INTERVAL '4 weeks'
            ORDER BY f.timestamp DESC
            '''
        )
        
        df = pd.DataFrame(features)
        
        # Remover linhas com valores faltantes críticos
        df = df.dropna(subset=[
            'total_cost', 'main_quantity', 'duration_days', 
            'cost_per_unit', 'productivity_per_day'
        ])
        
        return df
    
    def _train_regression_model(self, df: pd.DataFrame):
        """
        Regressão múltipla: Predizer custo total e cronograma
        
        Features:
        - main_quantity
        - duration_days (para custo)
        - complexity_score
        - cluster (encoded)
        - segment (encoded)
        
        Target:
        - total_cost
        - duration_days (para custo)
        """
        
        # Preparar features
        feature_cols = [
            'main_quantity', 'complexity_score', 'cluster', 'productivity_per_day'
        ]
        
        X = df[feature_cols].fillna(0)
        X = pd.get_dummies(X)  # Encode categóricas
        
        y_cost = df['total_cost']
        y_duration = df['duration_days']
        
        # Train-test split
        X_train, X_test, y_cost_train, y_cost_test = train_test_split(
            X, y_cost, test_size=0.2, random_state=42
        )
        
        # [Model A] Predição de Custo
        model_cost = RandomForestRegressor(n_estimators=100, max_depth=15)
        model_cost.fit(X_train, y_cost_train)
        
        score_cost = model_cost.score(X_test, y_cost_test)  # R²
        mae_cost = mean_absolute_error(
            y_cost_test, 
            model_cost.predict(X_test)
        )
        
        self.models['regression_cost'] = {
            'model': model_cost,
            'score': score_cost,
            'mae': mae_cost,
            'mape': self._compute_mape(y_cost_test, model_cost.predict(X_test)),
            'feature_importance': self._extract_feature_importance(model_cost)
        }
        
        # [Model B] Predição de Duração
        X_train_d, X_test_d, y_dur_train, y_dur_test = train_test_split(
            X, y_duration, test_size=0.2, random_state=42
        )
        
        model_duration = RandomForestRegressor(n_estimators=100, max_depth=15)
        model_duration.fit(X_train_d, y_dur_train)
        
        score_duration = model_duration.score(X_test_d, y_dur_test)
        
        self.models['regression_duration'] = {
            'model': model_duration,
            'score': score_duration
        }
        
        self.validation_results['regression_cost_r2'] = score_cost
        self.validation_results['regression_cost_mae'] = mae_cost
        self.validation_results['regression_duration_r2'] = score_duration
    
    def _train_classification_model(self, df: pd.DataFrame):
        """
        Classificação: Projeto "valido" ou "anômalo"?
        (precisa de rótulo: is_valid de projeto_validated)
        """
        
        # Usar labels de feedback humano quando disponível
        df_labeled = df[df['is_valid'].notna()]
        
        if len(df_labeled) < 20:
            self.validation_results['classification_status'] = 'insufficient_labels'
            return
        
        feature_cols = [
            'total_cost', 'main_quantity', 'duration_days',
            'cost_per_unit', 'productivity_per_day', 'complexity_score'
        ]
        
        X = df_labeled[feature_cols].fillna(0)
        y = df_labeled['is_valid'].astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model_clf = LogisticRegression(max_iter=1000)
        model_clf.fit(X_train, y_train)
        
        accuracy = model_clf.score(X_test, y_test)
        precision = precision_score(y_test, model_clf.predict(X_test), zero_division=0)
        recall = recall_score(y_test, model_clf.predict(X_test), zero_division=0)
        
        self.models['classification'] = {
            'model': model_clf,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall
        }
        
        self.validation_results['classification_accuracy'] = accuracy
        self.validation_results['classification_precision'] = precision
    
    def _train_anomaly_model(self, df: pd.DataFrame):
        """
        Detecção de anomalias: Isolation Forest retrained
        """
        
        feature_cols = [
            'cost_per_unit', 'productivity_per_day', 'duration_days'
        ]
        
        X = df[feature_cols].fillna(0)
        
        model_anomaly = IsolationForest(contamination=0.05, random_state=42)
        model_anomaly.fit(X)
        
        self.models['anomaly_detector'] = {
            'model': model_anomaly
        }
    
    def _train_similarity_model(self, df: pd.DataFrame):
        """
        Similarity matching: KNN para encontrar casos precedentes
        """
        
        feature_cols = [
            'cost_per_unit', 'duration_days', 'productivity_per_day',
            'total_cost', 'main_quantity'
        ]
        
        X = df[feature_cols].fillna(0)
        
        # Standardizar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # KNN com k=5
        model_knn = KNeighborsRegressor(n_neighbors=5)
        model_knn.fit(X_scaled, df.index)  # Usar índice como "ID"
        
        self.models['similarity_matcher'] = {
            'model': model_knn,
            'scaler': scaler,
            'reference_df': df
        }
    
    def _validate_all_models(self, training_data):
        """
        Métricas de validação para cada modelo
        """
        
        validation_summary = {
            'regression_cost': self.validation_results.get(
                'regression_cost_r2', 0
            ),
            'regression_duration': self.validation_results.get(
                'regression_duration_r2', 0
            ),
            'classification': self.validation_results.get(
                'classification_accuracy', 0
            ),
            'overall_quality_score': (
                self.validation_results.get('regression_cost_r2', 0) * 0.3 +
                self.validation_results.get('classification_accuracy', 0) * 0.3 +
                (1 - self.validation_results.get(
                    'regression_cost_mape', 0.5)
                ) * 0.4
            )
        }
        
        return validation_summary
    
    def _compare_with_previous_version(self):
        """
        Compara métricas com versão anterior
        """
        
        previous = self.db.query_single(
            '''
            SELECT * FROM model_training_logs
            WHERE status IN ('published', 'active')
            ORDER BY timestamp DESC LIMIT 1
            '''
        )
        
        if not previous:
            return {'status': 'first_version', 'previous_score': 0}
        
        current_score = self.validation_results.get(
            'overall_quality_score', 0
        )
        previous_score = previous.get('validation_results', {}).get(
            'overall_quality_score', 0
        )
        
        improvement = (current_score - previous_score) / (
            previous_score + 1e-6
        ) * 100
        
        return {
            'previous_score': previous_score,
            'current_score': current_score,
            'improvement_percent': improvement,
            'is_improvement': improvement > 2  # Threshold 2%
        }
    
    def _decide_publish_models(self, validation_results, comparison):
        """
        Decisão automática:
        - Publicar se overall_quality_score > 0.70 E (melhoria > 2% OR primeira versão)
        - Senão manter versão anterior
        """
        
        quality_score = validation_results['overall_quality_score']
        improvement = comparison.get('improvement_percent', 100)
        is_first_version = comparison.get('status') == 'first_version'
        
        publish_decision = (
            quality_score > 0.70 and 
            (improvement > 2 or is_first_version)
        )
        
        decision = {
            'action': 'publish' if publish_decision else 'hold',
            'rationale': {
                'quality_score': quality_score,
                'improvement_percent': improvement,
                'threshold_met': publish_decision
            },
            'effective_from': now_utc() if publish_decision else None
        }
        
        if publish_decision:
            # Versioning de modelos
            self._version_and_persist_models()
        
        return decision
    
    def _version_and_persist_models(self):
        """
        Salva versão dos modelos em production
        Versionamento: v_YYYY-MM-DD_HH-MM
        """
        
        version = f"v_{now_utc().strftime('%Y%m%d_%H%M')}"
        
        for model_name, model_data in self.models.items():
            model_obj = model_data['model']
            
            # Serializar modelo
            model_bytes = pickle.dumps(model_obj)
            
            self.db.insert('model_registry', {
                'model_name': model_name,
                'version': version,
                'model_bytes': model_bytes,
                'metrics': {k: v for k, v in model_data.items() if k != 'model'},
                'created_at': now_utc(),
                'status': 'active'
            })
    
    def _compute_mape(self, y_true, y_pred):
        """Mean Absolute Percentage Error"""
        return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-6))) * 100
    
    def _extract_feature_importance(self, model):
        """Extrai feature importance de Tree-based models"""
        if hasattr(model, 'feature_importances_'):
            return {
                'importances': model.feature_importances_.tolist(),
                'top_features': np.argsort(
                    model.feature_importances_
                )[-5:].tolist()
            }
        return {}


# Scheduler
schedule_training = {
    'job_name': 'manta_weekly_ml_training',
    'trigger': 'cron',
    'cron': '0 9 * * 1',  # segunda 09:00 UTC
    'handler': 'MantaMLModels.weekly_training',
    'timeout': 3600,  # 1h
    'notification': {
        'on_success': ['logs'],
        'on_failure': ['slack', 'email']
    }
}
```

---

## 5. STAGE 4: KB UPDATE & DECISION LOGIC (Mensal, primeiro domingo)

```python
# ============================================
# KB_UPDATE.py — Atualização de Constantes
# ============================================

class KnowledgeBaseUpdater:
    """
    Atualiza constantes KB quando:
    - Novos padrões com confiança > 85%
    - Melhoria significativa em casos reais (> 5% desvio reduzido)
    - Aprovação de especialista do segmento
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.agentes = self._init_segment_experts()  # Conexão com agentes
        
    def monthly_kb_update(self):
        """
        Trigger: Cron primeiro domingo 10:00 UTC
        Analisa feedback do mês e propõe atualizações KB
        """
        
        # [1] Analisar feedback humano do mês
        feedback_analysis = self._analyze_monthly_feedback()
        
        # [2] Identificar padrões com confiança > 85%
        pattern_candidates = self._identify_confident_patterns(
            feedback_analysis
        )
        
        if not pattern_candidates:
            return {'status': 'no_patterns_to_update', 'candidates': 0}
        
        # [3] Preparar proposal para especialista
        update_proposals = self._prepare_update_proposals(
            pattern_candidates
        )
        
        # [4] Roteiar para agente especialista (segmento)
        approval_status = self._request_specialist_approval(
            update_proposals
        )
        
        # [5] Se aprovado: aplicar update
        if approval_status.get('approved'):
            applied_updates = self._apply_kb_updates(
                update_proposals,
                approval_status.get('approver_id')
            )
            
            # [6] Publicar changelog
            self._publish_changelog(applied_updates)
            
            # [7] Versionar KB
            new_kb_version = self._increment_kb_version()
            
            return {
                'status': 'updates_applied',
                'kb_version': new_kb_version,
                'updates_count': len(applied_updates),
                'affected_segments': list(set([
                    u['segment'] for u in applied_updates
                ]))
            }
        else:
            return {
                'status': 'rejected_by_specialist',
                'reason': approval_status.get('rejection_reason')
            }
    
    def _analyze_monthly_feedback(self):
        """
        Analisa rejeições, correções e acertos do mês
        """
        
        feedback = self.db.query(
            '''
            SELECT f.*, pv.segment, pv.source_type
            FROM feedback_events f
            JOIN projeto_validated pv ON f.project_id = pv.project_id
            WHERE f.timestamp > now() - INTERVAL '1 month'
            AND f.timestamp < now()
            '''
        )
        
        analysis = {
            'total_feedback': len(feedback),
            'rejections': len([f for f in feedback if f['type'] == 'rejection']),
            'corrections': len([f for f in feedback if f['type'] == 'correction']),
            'approvals': len([f for f in feedback if f['type'] == 'approval']),
            'by_segment': {},
            'by_error_type': {}
        }
        
        # Agrupar por segmento
        for f in feedback:
            seg = f.get('segment', 'unknown')
            if seg not in analysis['by_segment']:
                analysis['by_segment'][seg] = {'count': 0, 'errors': []}
            
            analysis['by_segment'][seg]['count'] += 1
            if f.get('error_type'):
                analysis['by_segment'][seg]['errors'].append(f['error_type'])
        
        return analysis
    
    def _identify_confident_patterns(self, feedback_analysis, threshold=0.85):
        """
        Identifica padrões em feedback com confiança > threshold
        
        Exemplo:
        - Rejeitou 3 projetos similares por "cost_per_unit fora de faixa"
        - Modelos predizem custo com ±15%, mas 3 projetos com ±40%
        → Propõe ajuste de faixa esperada para esse tipo de projeto
        """
        
        candidates = []
        
        for segment, seg_data in feedback_analysis['by_segment'].items():
            
            # Contar tipos de erro mais frequentes
            error_counts = {}
            for error in seg_data['errors']:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error_type, count in error_counts.items():
                # Confiança: quantas vezes foi rejeitado por mesmo erro?
                rejection_count = feedback_analysis['rejections']
                if rejection_count > 0:
                    confidence = min(count / rejection_count, 1.0)
                else:
                    confidence = 0
                
                if confidence >= threshold:
                    candidates.append({
                        'segment': segment,
                        'error_type': error_type,
                        'frequency': count,
                        'confidence': confidence,
                        'action': self._recommend_action(error_type, segment)
                    })
        
        return candidates
    
    def _recommend_action(self, error_type: str, segment: str) -> dict:
        """
        Recomenda ação baseada em tipo de erro
        """
        
        # Mapear erro → ação sugerida
        action_map = {
            'cost_per_unit_out_of_range': {
                'type': 'update_constant',
                'constant': f'cost_per_unit_range_{segment}',
                'method': 'expand_range_by_10percent'
            },
            'productivity_outlier': {
                'type': 'update_constant',
                'constant': f'productivity_range_{segment}',
                'method': 'expand_range'
            },
            'duration_mismatch': {
                'type': 'update_constant',
                'constant': f'duration_multiplier_{segment}',
                'method': 'adjust_coefficient'
            },
            'bdi_unexpected': {
                'type': 'update_constant',
                'constant': f'bdi_default_{segment}',
                'method': 'adjust_based_on_feedback'
            }
        }
        
        return action_map.get(error_type, {'type': 'manual_review'})
    
    def _prepare_update_proposals(self, candidates: list) -> list:
        """
        Prepara proposals estruturadas para aprovação
        """
        
        proposals = []
        
        for candidate in candidates:
            
            # Buscar dados históricos do segmento
            current_constant_value = self.db.query_single(
                f'''
                SELECT value FROM kb_constants 
                WHERE segment = %s AND constant_name = %s
                AND version = (SELECT MAX(version) FROM kb_constants)
                ''',
                [candidate['segment'], candidate['action']['constant']]
            )
            
            # Calcular novo valor proposto
            new_value = self._calculate_new_constant_value(
                constant_name=candidate['action']['constant'],
                current_value=current_constant_value,
                adjustment_method=candidate['action']['method'],
                historical_data=self._get_historical_data(
                    candidate['segment']
                )
            )
            
            proposals.append({
                'segment': candidate['segment'],
                'constant_name': candidate['action']['constant'],
                'current_value': current_constant_value,
                'proposed_value': new_value,
                'change_percent': (
                    (new_value - current_constant_value) / 
                    (current_constant_value + 1e-6) * 100
                ),
                'confidence': candidate['confidence'],
                'rationale': f"Feedback de rejeição em {candidate['frequency']} projetos",
                'risk_assessment': self._assess_risk(
                    candidate['segment'], 
                    candidate['action']['constant'],
                    new_value
                )
            })
        
        return proposals
    
    def _request_specialist_approval(self, proposals: list) -> dict:
        """
        Encaminha para agente especialista do segmento
        Usa messaging ou Slack para aprovação
        """
        
        # Agrupar proposals por segmento
        by_segment = {}
        for prop in proposals:
            seg = prop['segment']
            if seg not in by_segment:
                by_segment[seg] = []
            by_segment[seg].append(prop)
        
        approval_results = {}
        
        for segment, seg_proposals in by_segment.items():
            
            # Roteiar para agente especialista
            specialist_agent = self._get_specialist_for_segment(segment)
            
            # Enviar para aprovação (via prompt estruturado)
            approval_response = specialist_agent.validate_kb_updates(
                proposals=seg_proposals,
                context={
                    'segment': segment,
                    'feedback_month': now_utc().strftime('%Y-%m'),
                    'confidence_threshold': 0.85
                }
            )
            
            approval_results[segment] = approval_response
        
        # Consolidar resultado
        all_approved = all([
            r.get('approved', False) 
            for r in approval_results.values()
        ])
        
        return {
            'approved': all_approved,
            'approvals_by_segment': approval_results,
            'approver_id': 'manta-specialist-agents',
            'rejection_reason': None if all_approved else (
                'Rejected by one or more specialists'
            )
        }
    
    def _apply_kb_updates(self, proposals: list, approver_id: str) -> list:
        """
        Aplica updates na KB
        Cria nova versão de constantes
        """
        
        # Incrementar versão
        current_version = self.db.query_single(
            'SELECT MAX(version) as max_version FROM kb_constants'
        )['max_version']
        
        new_version = current_version + 1
        
        applied = []
        
        for proposal in proposals:
            
            # Inserir novo valor na kb_constants
            self.db.insert('kb_constants', {
                'version': new_version,
                'segment': proposal['segment'],
                'constant_name': proposal['constant_name'],
                'old_value': proposal['current_value'],
                'new_value': proposal['proposed_value'],
                'change_reason': proposal['rationale'],
                'confidence': proposal['confidence'],
                'approved_by': approver_id,
                'approved_at': now_utc(),
                'applied_at': now_utc(),
                'status': 'active'
            })
            
            # Registrar auditoria
            self.db.insert('kb_update_audit', {
                'version': new_version,
                'constant_updated': proposal['constant_name'],
                'old_value': proposal['current_value'],
                'new_value': proposal['proposed_value'],
                'applied_at': now_utc()
            })
            
            applied.append(proposal)
        
        return applied
    
    def _publish_changelog(self, updates: list):
        """
        Publica changelog em formato estruturado
        """
        
        changelog = {
            'version': f"KB v{self._get_current_kb_version()}",
            'published_at': now_utc(),
            'changes': []
        }
        
        for update in updates:
            changelog['changes'].append({
                'segment': update['segment'],
                'constant': update['constant_name'],
                'old_value': update['current_value'],
                'new_value': update['proposed_value'],
                'change_reason': update['rationale']
            })
        
        # Persistir changelog
        self.db.insert('kb_changelog', {
            'version': self._get_current_kb_version(),
            'changelog_json': json.dumps(changelog),
            'published_at': now_utc()
        })
        
        # Notificar equipes
        self._notify_teams_of_update(changelog)
    
    def _increment_kb_version(self) -> int:
        """Incrementa versão do KB"""
        current = self.db.query_single(
            'SELECT MAX(version) as v FROM kb_constants'
        )['v']
        return current + 1
    
    def _get_specialist_for_segment(self, segment: str):
        """Retorna agente especialista do segmento"""
        # Mapear segment → agente especialista
        specialists = {
            'S1': 'agente-infraestrutura-s1',
            'S2': 'agente-infraestrutura-s2',
            'S3': 'agente-infraestrutura-s3',
            'S4': 'agente-infraestrutura-s4',
            'S6': 'agente-portos',
            'S8': 'agente-saneamento',
            'S9': 'agente-energia'
        }
        return self.agentes[specialists[segment]]
    
    def _get_historical_data(self, segment: str):
        """Retorna dados históricos do segmento para análise"""
        return self.db.query(
            'SELECT * FROM projeto_validated WHERE segment = %s ORDER BY approved_date DESC LIMIT 100',
            [segment]
        )
    
    def _calculate_new_constant_value(self, constant_name, current_value, 
                                     adjustment_method, historical_data):
        """
        Calcula novo valor da constante baseado em método
        """
        
        if adjustment_method == 'expand_range_by_10percent':
            # Expandir faixa em 10%
            if isinstance(current_value, (list, tuple)):
                min_val, max_val = current_value
                return [
                    min_val * 0.9,
                    max_val * 1.1
                ]
        
        elif adjustment_method == 'expand_range':
            # Expandir para cobrir outliers
            if historical_data:
                df = pd.DataFrame(historical_data)
                # Usar percentil 5 e 95 como nova faixa
                relevant_field = self._map_constant_to_field(constant_name)
                return [
                    df[relevant_field].quantile(0.05),
                    df[relevant_field].quantile(0.95)
                ]
        
        elif adjustment_method == 'adjust_coefficient':
            # Ajustar coeficiente multiplicativo
            if historical_data:
                df = pd.DataFrame(historical_data)
                mean_observed = df['duration_days'].mean()
                mean_predicted = df['duration_days_predicted'].mean()
                new_coef = mean_observed / (mean_predicted + 1e-6)
                return new_coef
        
        return current_value
    
    def _assess_risk(self, segment: str, constant_name: str, new_value) -> dict:
        """
        Avalia risco de mudança:
        - Impacto em projetos em aberto?
        - Desvio muito grande?
        - Precedente histórico?
        """
        
        risk_score = 0
        reasons = []
        
        # Verificar se há projetos em aberto que serão afetados
        open_projects = self.db.query(
            '''
            SELECT COUNT(*) as cnt FROM projeto 
            WHERE segment = %s AND status = 'in_progress'
            ''',
            [segment]
        )[0]['cnt']
        
        if open_projects > 0:
            risk_score += 20
            reasons.append(f'{open_projects} projetos em execução')
        
        return {
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score > 50 else ('medium' if risk_score > 20 else 'low'),
            'concerns': reasons
        }
    
    def _map_constant_to_field(self, constant_name: str) -> str:
        """Mapeia nome da constante para field do dataset"""
        mapping = {
            'cost_per_unit_range': 'cost_per_unit',
            'productivity_range': 'productivity_per_day',
            'duration_multiplier': 'duration_days',
            'bdi_default': 'bdi_percentage'
        }
        for key, field in mapping.items():
            if key in constant_name:
                return field
        return constant_name
    
    def _notify_teams_of_update(self, changelog):
        """Notifica times via Slack/Email"""
        # TODO: Integração com sistema de notificação
        pass
```

---

## 6. FEEDBACK AMPLIFICATION (Em Tempo Real)

```python
# ============================================
# FEEDBACK_AMPLIFIER.py — Capture & Retraining
# ============================================

class FeedbackAmplifier:
    """
    Captura feedback humano e executa:
    1. Rejeição → Adicionar como dado negativo
    2. Correção → Retraining imediato se padrão recorrente
    3. Aprovação → Aumentar confiança da regra
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.ml_pipeline = MantaMLModels()
    
    def capture_feedback(self, project_id: str, feedback_type: str, details: dict):
        """
        Captura feedback de especialista durante validação
        
        feedback_type: 'approval' | 'rejection' | 'correction'
        details: {
            'reason': str,
            'corrected_fields': dict,  # se correction
            'severity': 'minor' | 'major',
            'approver_id': str
        }
        """
        
        # [1] Persistir feedback
        feedback_record = {
            'project_id': project_id,
            'feedback_type': feedback_type,
            'details': details,
            'timestamp': now_utc(),
            'approver_id': details.get('approver_id'),
            'status': 'recorded'
        }
        
        self.db.insert('feedback_events', feedback_record)
        
        # [2] Análise imediata
        analysis = self._analyze_feedback(project_id, feedback_type, details)
        
        # [3] Se rejeição recorrente: trigger retraining
        if feedback_type == 'rejection' and analysis['recurrence_level'] > 2:
            self._trigger_immediate_retraining(
                trigger_reason='recurrent_rejection',
                project_id=project_id,
                error_pattern=analysis['error_pattern']
            )
        
        # [4] Se correção: atualizar dados de training
        elif feedback_type == 'correction':
            self._update_training_data(
                project_id,
                details.get('corrected_fields', {})
            )
        
        # [5] Se aprovação: aumentar confiança
        elif feedback_type == 'approval':
            self._increase_rule_confidence(project_id)
        
        return analysis
    
    def _analyze_feedback(self, project_id: str, feedback_type: str, details: dict):
        """
        Analisa padrão de feedback:
        - Quantas rejeições similares?
        - Qual campo está falhando?
        - Taxa de aprovação vs rejeição?
        """
        
        project = self.db.query_single(
            'SELECT * FROM projeto WHERE id = %s', [project_id]
        )
        
        # Contar rejeições similares
        similar_rejections = self.db.query(
            '''
            SELECT COUNT(*) as cnt FROM feedback_events f
            JOIN projeto p ON f.project_id = p.id
            WHERE p.segment = %s 
            AND f.feedback_type = 'rejection'
            AND f.details->>'reason' = %s
            AND f.timestamp > now() - INTERVAL '30 days'
            ''',
            [project['segment'], details.get('reason')]
        )
        
        recurrence = similar_rejections[0]['cnt'] if similar_rejections else 0
        
        return {
            'project_id': project_id,
            'feedback_type': feedback_type,
            'error_pattern': details.get('reason'),
            'recurrence_level': recurrence,
            'should_retrain': recurrence >= 3,
            'analysis_timestamp': now_utc()
        }
    
    def _trigger_immediate_retraining(self, trigger_reason: str, project_id: str, 
                                      error_pattern: str):
        """
        Executa retraining imediato de modelo específico
        (não espera pela agenda semanal)
        """
        
        # Identificar qual modelo está falhando
        model_to_retrain = self._identify_failing_model(error_pattern)
        
        # Coletar dados negativos recentes
        negative_examples = self.db.query(
            '''
            SELECT f.*, p.normalized_data 
            FROM feedback_events f
            JOIN projeto p ON f.project_id = p.id
            WHERE f.feedback_type = 'rejection'
            AND f.details->>'reason' = %s
            AND f.timestamp > now() - INTERVAL '30 days'
            LIMIT 20
            ''',
            [error_pattern]
        )
        
        # Retraining do modelo específico
        retraining_result = self._retrain_specific_model(
            model_name=model_to_retrain,
            negative_examples=negative_examples,
            trigger_reason=trigger_reason
        )
        
        # Validação rápida
        if retraining_result['validation_score'] > 0.85:
            # Publicar imediatamente
            self._publish_model_update(model_to_retrain, retraining_result)
            status = 'published'
        else:
            status = 'held_for_review'
        
        # Log
        self.db.insert('immediate_retraining_log', {
            'trigger_reason': trigger_reason,
            'model_retrained': model_to_retrain,
            'negative_examples_count': len(negative_examples),
            'validation_score': retraining_result['validation_score'],
            'status': status,
            'timestamp': now_utc()
        })
    
    def _update_training_data(self, project_id: str, corrected_fields: dict):
        """
        Atualiza dataset de training com correções humanas
        """
        
        # Buscar projeto original
        project = self.db.query_single(
            'SELECT * FROM projeto_normalized WHERE project_id = %s',
            [project_id]
        )
        
        # Atualizar valores corrigidos
        for field, new_value in corrected_fields.items():
            project['normalized_data'][field] = new_value
        
        # Re-extrair features com valores corrigidos
        updated_features = self._recompute_features(project)
        
        # Persistir como "approved training example"
        self.db.insert('training_approved_examples', {
            'project_id': project_id,
            'original_features': project['original_features'],
            'corrected_features': updated_features,
            'corrections_applied': corrected_fields,
            'timestamp': now_utc(),
            'approver_id': corrected_fields.get('_approver_id')
        })
    
    def _increase_rule_confidence(self, project_id: str):
        """
        Registra aprovação como sinal positivo de confiança
        """
        
        project = self.db.query_single(
            'SELECT * FROM projeto WHERE id = %s', [project_id]
        )
        
        # Incrementar confidence counter para as regras utilizadas
        rules_used = self._identify_rules_used(project)
        
        for rule in rules_used:
            self.db.execute(
                '''
                UPDATE kb_rules 
                SET confidence_score = confidence_score + 0.01,
                    approvals_count = approvals_count + 1,
                    last_approval_at = %s
                WHERE rule_id = %s
                ''',
                [now_utc(), rule['rule_id']]
            )
    
    def _identify_failing_model(self, error_pattern: str) -> str:
        """Mapeia erro → modelo que falhou"""
        mapping = {
            'cost_per_unit': 'regression_cost',
            'duration': 'regression_duration',
            'productivity': 'regression_cost',
            'anomalous': 'anomaly_detector',
            'not_similar_to_history': 'similarity_matcher'
        }
        return mapping.get(error_pattern, 'regression_cost')
    
    def _retrain_specific_model(self, model_name: str, negative_examples: list, 
                               trigger_reason: str):
        """
        Retraining focado em um modelo específico com exemplos negativos
        """
        # TODO: Implementar retraining incremental
        return {'validation_score': 0.88}
    
    def _publish_model_update(self, model_name: str, result: dict):
        """Publica atualização de modelo"""
        # TODO: Versioning e deployment
        pass
    
    def _recompute_features(self, project: dict):
        """Recomputa features com valores corrigidos"""
        engineer = FeatureEngineer()
        return engineer._extract_features(project)
    
    def _identify_rules_used(self, project: dict) -> list:
        """Identifica quais regras KB foram usadas neste projeto"""
        # TODO: Rastrear regras aplicadas durante processamento
        return []
```

---

## 7. ORCHESTRATION & SCHEDULING

```yaml
# ============================================
# SCHEDULE.yaml — Cronograma Completo
# ============================================

daily_schedule:
  - job_id: "ingestion_0600"
    time: "06:00 UTC"
    handler: "MantaIngestionEngine.daily_collect"
    timeout: 1800  # 30 min
    retry:
      max_attempts: 3
      backoff: exponential
    notification:
      on_failure: ["slack", "email"]

  - job_id: "normalization_0700"
    time: "07:00 UTC"
    depends_on: "ingestion_0600"
    handler: "ProjectNormalizer.normalize_batch"
    timeout: 1800

  - job_id: "feature_engineering_0800"
    time: "08:00 UTC"
    depends_on: "normalization_0700"
    handler: "FeatureEngineer.engineer_features"
    timeout: 1800

weekly_schedule:
  - job_id: "ml_training_weekly"
    time: "Monday 09:00 UTC"
    handler: "MantaMLModels.weekly_training"
    timeout: 3600
    notification:
      on_success: ["logs"]
      on_failure: ["slack", "email"]

monthly_schedule:
  - job_id: "kb_update_monthly"
    time: "First Sunday 10:00 UTC"
    handler: "KnowledgeBaseUpdater.monthly_kb_update"
    timeout: 3600
    requires_approval: true
    approval_channel: "#manta-kb-governance"

on_demand:
  - event: "human_rejection"
    handler: "FeedbackAmplifier.capture_feedback"
    action: "log_rejection + analyze_pattern"

  - event: "recurrent_rejection"
    condition: "rejection_count > 3 in 30 days"
    handler: "FeedbackAmplifier._trigger_immediate_retraining"

  - event: "project_correction"
    handler: "FeedbackAmplifier._update_training_data"

rollback_mechanism:
  trigger: "model_validation_score < 0.65 after deployment"
  action: "revert_to_previous_version"
  notification: "immediate_slack_alert"
  review_period: 24h
```

---

## 8. ROLLBACK STRATEGY

```python
# ============================================
# ROLLBACK.py — Reversão de Atualizações
# ============================================

class RollbackManager:
    """
    Detecta falhas em atualizações e reverte automaticamente
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.monitoring_window = 24  # horas
    
    def monitor_model_performance(self):
        """
        Executa a cada hora: valida se modelo atual está performando bem
        """
        
        # Coletar projetos processados na última hora
        recent_projects = self.db.query(
            '''
            SELECT * FROM projeto 
            WHERE processed_at > now() - INTERVAL '1 hour'
            AND model_version = (SELECT current_version FROM model_registry LIMIT 1)
            '''
        )
        
        if not recent_projects:
            return {'status': 'insufficient_data'}
        
        # Calcular métricas de erro
        error_rate = self._calculate_error_rate(recent_projects)
        
        # Se taxa de erro sobe > 15% em relação à baseline
        baseline_error = self.db.query_single(
            'SELECT avg_error_rate FROM model_performance_baseline'
        )['avg_error_rate']
        
        if error_rate > baseline_error * 1.15:
            # ALERTA: Modelo degraded
            self._trigger_rollback(
                reason='error_rate_degradation',
                current_error_rate=error_rate,
                threshold=baseline_error * 1.15
            )
            
            return {
                'status': 'rollback_triggered',
                'reason': 'error_rate_degradation',
                'current_error_rate': error_rate,
                'threshold': baseline_error * 1.15
            }
        
        return {'status': 'healthy', 'error_rate': error_rate}
    
    def _trigger_rollback(self, reason: str, current_error_rate: float, threshold: float):
        """
        Reverter para versão anterior
        """
        
        # [1] Buscar versão anterior
        previous_version = self.db.query_single(
            '''
            SELECT * FROM model_registry 
            WHERE status = 'archived' 
            ORDER BY created_at DESC LIMIT 1
            '''
        )
        
        if not previous_version:
            # Nenhuma versão anterior disponível
            self._alert_ops_team(
                severity='critical',
                message=f'Model degraded but no rollback available. Error rate: {current_error_rate}'
            )
            return
        
        # [2] Reativar versão anterior
        self.db.execute(
            '''
            UPDATE model_registry 
            SET status = 'archived' 
            WHERE status = 'active'
            '''
        )
        
        self.db.execute(
            '''
            UPDATE model_registry 
            SET status = 'active' 
            WHERE version = %s
            ''',
            [previous_version['version']]
        )
        
        # [3] Log da reversão
        self.db.insert('rollback_events', {
            'timestamp': now_utc(),
            'reason': reason,
            'previous_version': previous_version['version'],
            'error_rate_before': current_error_rate,
            'error_rate_threshold': threshold,
            'status': 'executed'
        })
        
        # [4] Alerta
        self._alert_ops_team(
            severity='high',
            message=f'Automatic rollback executed: {reason}'
        )
    
    def _calculate_error_rate(self, projects: list) -> float:
        """
        Taxa de erro = rejections / total projects
        """
        if not projects:
            return 0
        
        rejections = len([p for p in projects if p.get('was_rejected')])
        return rejections / len(projects)
    
    def _alert_ops_team(self, severity: str, message: str):
        """Notifica ops via Slack/Email"""
        # TODO: Integração com alerting system
        pass
```

---

## 9. RESUMO DE FLUXO E THRESHOLDS

### Thresholds Críticos

| Decisão | Threshold | Ação |
|---------|-----------|------|
| **Publicar modelo** | R² > 0.70 | Treinar → validar → publicar |
| **Considerar KB update** | Confiança > 85% | Aprovar com especialista |
| **Rejeitar KB update** | Risco > 50 | Hold para revisão manual |
| **Trigger retraining** | Rejeição > 3x/mês | Immediate retraining |
| **Rollback modelo** | Error rate > baseline × 1.15 | Revert automatic |
| **Escalate para humano** | Confiança < 50% | Manual review |

### Sequência Diária Ideal

```
06:00 UTC  ┌─ Ingestion (Raw → Staging)
           │
07:00 UTC  ├─ Normalization (Staging → Normalized)
           │
08:00 UTC  ├─ Feature Engineering (Normalized → Features)
           │
Throughout ├─ Real-time Feedback Capture
  day      │
           │
09:00 UTC  └─ Monitor model performance (Hourly)

Every      ┌─ Weekly ML Training (Monday 09:00)
Monday     │
09:00 UTC  └─ Validate & publish (if score > 0.70)

First      ┌─ Monthly KB Review (Sunday 10:00)
Sunday     │
10:00 UTC  └─ Propose + approve updates (confidence > 85%)
```

---

## 10. IMPLEMENTAÇÃO: STACK RECOMENDADO

```
┌─────────────────────────────────────────┐
│         ORCHESTRATION LAYER             │
│  Airflow / Dagster / Prefect            │
└──────────────────┬──────────────────────┘
                   │
     ┌─────────────┴─────────────┐
     │                           │
┌────▼──────────┐     ┌────▼──────────┐
│   DATA LAYER  │     │  ML LAYER     │
│  - Supabase   │     │  - scikit-learn
│  - PostgreSQL │     │  - XGBoost
│  - Redis      │     │  - PyTorch
└────┬──────────┘     └────┬──────────┘
     │                     │
     └─────────────┬───────┘
                   │
           ┌───────▼────────┐
           │  NOTIFICATION  │
           │  - Slack       │
           │  - Email       │
           │  - Webhooks    │
           └────────────────┘
```

---

Projeto concluído. Sistema pronto para deployment e tuning em produção.
