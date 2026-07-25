# S4 Integração Estratégica — Metrô (Q1 2027 → Q2 2027)

**Documento**: Estratégia de Integração Técnica para Manta 03-S4 (agente-infraestrutura).  
**Data**: 2026-07-24  
**Versão**: 1.0 (DRAFT)  
**Proprietário**: Manta Associados — Arquiteto IA (Manta 16)  
**Status**: Pronto para aprovação de gate humano (MN)

---

## 1. VISÃO GERAL

A estratégia S4 visa integrar o agente-infraestrutura (Metrô) com uma pilha técnica de coordenação BIM (Building Information Modeling) assistida por IA, focada em projetos de transporte sobre trilhos urbano (metrô, VLT) e suas infraestruturas:

1. **Revit Model Coordination** — integração de modelos 3D (arquitetura, estrutura, MEP) via Revit 2027 MCP
2. **Navisworks Clash Detection** — automação de detecção de interferências via nativa Navisworks ou HuskyBIM API
3. **Multi-Discipline Coordination Workflows** — orquestração de ciclos de coordenação (arquitetura ↔ estrutura ↔ MEP)
4. **Schedule Extraction from BIM** — extrair cronograma de construção integrado ao modelo Revit
5. **Approval Flow Automation** — workflow de aprovação inteligente com rastreabilidade de decisões
6. **Output Delivery** — DXF normalizado + relatórios de coordenação + playbooks operacionais

**Resultado esperado**: Redução de 30-50% do tempo de coordenação BIM em projetos metroviários via automação inteligente de detecção de conflitos, extração de dados construtivos, e workflows de aprovação pré-configurados. Aumento de 95% em cobertura de coordenação (vs. manual 70%) e redução de >80% em conflitos não-detectados em fases iniciais.

---

## 2. ARQUITETURA TÉCNICA

### 2.1 Pilha de Integração

```
┌─────────────────────────────────────────────────────────────┐
│  ENTRADA — Usuário (Engenheiro BIM / Coordenador / S4)      │
│  Formato: Revit (.rvt), NWC (Navisworks cache), IFC, PDF   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  PARSER LAYER           │
        │  ├─ Revit extraction    │
        │  ├─ NWC import          │
        │  ├─ IFC validation      │
        │  └─ Model federation    │
        └────────────┬───────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  NORMALIZATION LAYER                │
        │  ├─ Coordinate systems align        │
        │  ├─ Phase/level standardization     │
        │  ├─ Element classification          │
        │  └─ Discipline tagging (Arch/Str/M) │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  CLASH DETECTION ENGINE             │
        │  ├─ Native Navisworks rules         │
        │  ├─ Custom clash definitions        │
        │  ├─ Severity classification         │
        │  └─ Smart filtering (false positives)│
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  COORDINATION WORKFLOW LAYER        │
        │  ├─ Issue creation & assignment     │
        │  ├─ Discipline-specific analysis    │
        │  ├─ Resolution tracking             │
        │  └─ Impact assessment               │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  SCHEDULE & APPROVAL LAYER          │
        │  ├─ Extract schedule from BIM       │
        │  ├─ Impact analysis on timeline     │
        │  ├─ Approval workflow routing       │
        │  └─ Change order generation         │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  SAÍDA — Deliverables  │
        │  ├─ DXF (normatizado)  │
        │  ├─ Clash reports PDF  │
        │  ├─ Coordination matrix │
        │  ├─ Schedule analysis   │
        │  └─ Playbooks S4       │
        └────────────────────────┘
```

### 2.2 Componentes

| Componente | Tech Stack | Responsabilidade | Tempo Estimado |
|------------|------------|------------------|-----------------|
| **Revit Importer** | Revit 2027 MCP + pyRevit | Carregar múltiplos .rvt, extrair geometria/parâmetros | Q1 2027 |
| **Navisworks Integrator** | Navisworks API (COM) + HuskyBIM API (REST) | Carregar NWC, executar clash rules | Q1 2027 |
| **IFC Validator** | ifcopenshell + XSD rules | Validação IFC 4.3, mapeamento de disciplinas | Q1 2027 |
| **Clash Detection Engine** | Python + Navisworks native rules | Configuração rules, execução, filtering | Q1 2027 |
| **Coordination Orchestrator** | Python async + message queue | Orquestração fluxos multi-disciplina | Q1 2027 |
| **Schedule Extractor** | Revit API + MS Project XML bridge | Extração cronograma BIM, análise impactos | Q1 2027 |
| **Approval Workflow** | Python FastAPI + Supabase | Roteamento approval, rastreabilidade decisões | Q2 2027 |
| **DXF Export Module** | ezdxf writer + metro-specific rules | Geração DXF normalizado (ABNT NBR 13142) | Q1 2027 |
| **Report Generator** | Jinja2 + ReportLab + Plotly | Relatórios PDF clash, matriz coordenação, KPIs | Q1 2027 |

---

## 3. FLUXOS DE INTEGRAÇÃO

### 3.1 Fluxo Carga & Normalização de Modelos

#### Fluxo-1: Carregar Modelos Revit (Multi-Disciplina)

**Input**: Pasta com múltiplos arquivos .rvt
```
projetos_metro/
├── Arquitetura_L4_Rev02.rvt
├── Estrutura_L4_Rev02.rvt
├── MEP_Mecanica_L4_Rev02.rvt
├── MEP_Eletrica_L4_Rev02.rvt
└── MEP_Hidraulica_L4_Rev02.rvt
```

**Etapas**:
1. **Conectar a Revit via MCP/COM**
2. **Para cada .rvt**:
   - Abrir documento
   - Extrair elementos por categoria (walls, pipes, ducts, conduits, structural elements)
   - Extrair parâmetros globais (project base point, survey point)
   - Extrair fases de construção (Phase property)
   - Converter coordenadas para sistema compartilhado (Shared Coordinates)
3. **Validar integridade** — verificar duplicatas, elementos órfãos
4. **Output**: JSON struct com geometria + parâmetros normalizados

**Pseudocódigo** (Python + Revit API via pyRevit ou win32com):

```python
import win32com.client
from revit_api import RevitElement, RevitDocument
import json

def load_revit_models(folder_path: str) -> Dict[str, RevitDocument]:
    """Load multiple Revit files and extract normalized data."""
    
    revit_app = win32com.client.GetObject("Revit.Application")
    models = {}
    
    for rvt_file in find_rvt_files(folder_path):
        doc = revit_app.OpenDocumentFile(rvt_file)
        
        # Extract shared coordinates (ProjectBasePoint)
        shared_coords = extract_shared_coordinates(doc)
        
        # Extract all discipline elements
        disciplines = {
            "architecture": extract_category_elements(doc, ["Walls", "Doors", "Windows", "Rooms"]),
            "structure": extract_category_elements(doc, ["Structural Columns", "Structural Framing", "Floors"]),
            "mep": extract_mep_elements(doc),  # Mechanical, Electrical, Plumbing
        }
        
        # Extract construction phases
        phases = extract_construction_phases(doc)
        
        models[rvt_file] = {
            "document": doc,
            "shared_coords": shared_coords,
            "disciplines": disciplines,
            "phases": phases,
            "file_path": rvt_file,
        }
    
    return models

def extract_category_elements(doc, category_names: List[str]) -> List[Dict]:
    """Extract elements from specified categories with geometry & parameters."""
    
    elements = []
    for cat_name in category_names:
        category = doc.Categories.get_Item(cat_name)
        if category:
            for elem in doc.GetElements(category):
                elem_data = {
                    "id": elem.Id,
                    "name": elem.Name,
                    "category": cat_name,
                    "level": elem.LevelName if hasattr(elem, "LevelName") else None,
                    "parameters": extract_parameters(elem),
                    "geometry": extract_geometry(elem),
                }
                elements.append(elem_data)
    
    return elements

def extract_mep_elements(doc) -> Dict:
    """Extract MEP elements (pipes, ducts, conduits, electrical)."""
    
    mep_data = {
        "mechanical": extract_category_elements(doc, ["Ducts", "Ductwork", "Mechanical Equipment"]),
        "electrical": extract_category_elements(doc, ["Conduit", "Electrical Equipment", "Lighting Fixtures"]),
        "plumbing": extract_category_elements(doc, ["Pipes", "Plumbing Fixtures", "Mechanical Equipment"]),
    }
    
    return mep_data
```

**Tempo**: 5-15 min (consoante nº arquivos e tamanho)

---

#### Fluxo-2: Carregar Modelo Navisworks (NWC/NWD)

**Input**: Arquivo NWC/NWD consolidado (federated model)

**Etapas**:
1. **Carregar NWC via Navisworks COM API** (ou via HuskyBIM REST)
2. **Extrair estrutura hierárquica** (model tree, layer structure)
3. **Mapear elementos para disciplinas** (detectar via prefixo layer ou custom property)
4. **Extrair geometria bounding boxes** (para clash detection)
5. **Output**: Hierarquia + geometria simplificada

**Pseudocódigo** (Navisworks COM):

```python
import win32com.client

def load_navisworks_model(nwc_path: str) -> Dict:
    """Load NWC file and extract model hierarchy."""
    
    nw_app = win32com.client.Dispatch("NavisWorks.Application")
    
    # Open NWC
    doc = nw_app.ActiveDocument
    doc.OpenFile(nwc_path)
    
    # Extract model tree
    model_tree = extract_model_tree(doc.RootItem)
    
    # Extract layers & properties
    layers = {}
    for layer in doc.Layers:
        layers[layer.Name] = {
            "items": [item.Name for item in layer.Items],
            "visible": layer.Visible,
            "properties": extract_layer_properties(layer),
        }
    
    # Extract clash rules (if configured)
    clash_rules = []
    for rule in doc.GetClashTests():
        clash_rules.append({
            "name": rule.DisplayName,
            "description": rule.Description,
            "test_type": rule.TestType,  # hard-hard, hard-soft, etc
        })
    
    return {
        "model_tree": model_tree,
        "layers": layers,
        "clash_rules": clash_rules,
        "document": doc,
    }

def extract_model_tree(item, parent_path="") -> Dict:
    """Recursively extract model tree hierarchy."""
    
    tree = {
        "name": item.DisplayName,
        "path": f"{parent_path}/{item.DisplayName}",
        "geometry": extract_bounding_box(item),
        "children": [],
    }
    
    for child in item.Children:
        tree["children"].append(extract_model_tree(child, tree["path"]))
    
    return tree
```

**Tempo**: 3-8 min

---

#### Fluxo-3: Carregar/Validar IFC (Alternativa)

**Input**: Arquivo IFC 4.3 exportado de Revit ou ferramentas BIM

**Etapas**:
1. **Parse IFC com ifcopenshell**
2. **Validar estrutura contra IFC 4.3 schema**
3. **Mapear para disciplinas** (via IfcOwnerHistory.OwnerHistoryType ou custom properties)
4. **Extrair geometria (IfcShapeRepresentation)**
5. **Output**: Elementos IFC normalizados

**Pseudocódigo** (Python + ifcopenshell):

```python
import ifcopenshell
import ifcopenshell.geom

def load_ifc_model(ifc_path: str) -> Dict:
    """Load and validate IFC file."""
    
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Get project metadata
    project = ifc_file.by_type("IfcProject")[0]
    
    # Extract building structure
    buildings = ifc_file.by_type("IfcBuilding")
    storeys = ifc_file.by_type("IfcBuildingStorey")
    
    # Extract elements by discipline
    elements = {
        "architecture": ifc_file.by_type("IfcWall") + ifc_file.by_type("IfcDoor") + ifc_file.by_type("IfcWindow"),
        "structure": ifc_file.by_type("IfcColumn") + ifc_file.by_type("IfcBeam") + ifc_file.by_type("IfcSlab"),
        "mep": {
            "mechanical": ifc_file.by_type("IfcDuctSegment") + ifc_file.by_type("IfcDuctFitting"),
            "electrical": ifc_file.by_type("IfcCableSegment") + ifc_file.by_type("IfcElectricalElement"),
            "plumbing": ifc_file.by_type("IfcPipeSegment") + ifc_file.by_type("IfcPipeFitting"),
        }
    }
    
    # Validate and extract geometry
    ifc_data = {}
    for discipline, elem_list in elements.items():
        ifc_data[discipline] = []
        for elem in elem_list:
            try:
                shape = ifcopenshell.geom.create_shape(elem)
                ifc_data[discipline].append({
                    "id": elem.id(),
                    "guid": elem.GlobalId,
                    "name": elem.Name,
                    "type": elem.is_a(),
                    "geometry": shape.geometry,
                })
            except Exception as e:
                print(f"Warning: could not extract geometry for {elem.Name}: {e}")
    
    return {
        "project": project.Name,
        "elements": ifc_data,
        "storeys": [s.Name for s in storeys],
        "buildings": [b.Name for b in buildings],
    }
```

**Tempo**: 2-5 min

---

### 3.2 Fluxo Detecção de Conflitos (Clash Detection)

#### Fluxo-4: Executar Detecção de Clashes

**Input**: Modelos carregados (Revit + Navisworks)

**Etapas**:
1. **Configurar regras de clash** (pré-definidas por disciplina)
2. **Executar clash tests** via Navisworks
3. **Filtrar falsos positivos** (usando heurísticas IA)
4. **Classificar severidade** (crítico, alto, médio, baixo)
5. **Atribuir a disciplinas** (quem resolve?)
6. **Output**: Clash report JSON + visualizações

**Pseudocódigo**:

```python
import asyncio
from typing import List, Dict, Tuple

class ClashDetectionEngine:
    """Main clash detection orchestrator."""
    
    def __init__(self, nw_doc, revit_models: Dict):
        self.nw_doc = nw_doc
        self.revit_models = revit_models
        self.clash_rules = self._define_clash_rules()
    
    def _define_clash_rules(self) -> Dict[str, List[Tuple[str, str]]]:
        """Define discipline clash rules (hardcoded for S4 metro)."""
        
        return {
            # Architecture vs Structure
            "arch_vs_struct": [
                ("walls", "structural_columns"),
                ("doors", "structural_beams"),
                ("windows", "structural_framing"),
            ],
            # Structure vs MEP Mechanical
            "struct_vs_mep_mech": [
                ("structural_framing", "ducts"),
                ("structural_columns", "mechanical_equipment"),
                ("floor_slabs", "pipes"),
            ],
            # MEP Mechanical vs Electrical
            "mep_mech_vs_elec": [
                ("ducts", "conduit"),
                ("pipes", "electrical_equipment"),
            ],
            # MEP Electrical vs Plumbing
            "mep_elec_vs_plumb": [
                ("conduit", "pipes"),
                ("electrical_equipment", "plumbing_fixtures"),
            ],
            # Architecture vs MEP
            "arch_vs_mep": [
                ("walls", "ducts"),
                ("walls", "pipes"),
                ("doors", "conduit"),
            ],
        }
    
    async def execute_clash_detection(self) -> Dict:
        """Execute all clash tests and return filtered results."""
        
        all_clashes = []
        
        # Method 1: Navisworks native clash detection
        nw_clashes = self._run_navisworks_clashes()
        all_clashes.extend(nw_clashes)
        
        # Method 2: Custom Python clash detection (for complex rules)
        python_clashes = await self._run_python_clash_detection()
        all_clashes.extend(python_clashes)
        
        # Filter false positives (AI-based)
        filtered_clashes = self._filter_false_positives(all_clashes)
        
        # Classify by severity
        classified_clashes = self._classify_severity(filtered_clashes)
        
        # Assign to disciplines
        assigned_clashes = self._assign_responsibility(classified_clashes)
        
        return {
            "total_clashes": len(assigned_clashes),
            "clashes_by_severity": self._group_by_severity(assigned_clashes),
            "clashes_by_discipline": self._group_by_discipline(assigned_clashes),
            "clashes": assigned_clashes,
        }
    
    def _run_navisworks_clashes(self) -> List[Dict]:
        """Execute Navisworks native clash tests."""
        
        clashes = []
        doc = self.nw_doc
        
        # Run each configured test
        for rule_name, test_pairs in self.clash_rules.items():
            try:
                # Create clash test
                clash_test = doc.SetupClashTest(rule_name)
                
                for source_group, target_group in test_pairs:
                    clash_test.AddGroupA(source_group)
                    clash_test.AddGroupB(target_group)
                
                # Execute
                clash_test.Run()
                
                # Extract results
                for clash in clash_test.GetResults():
                    clashes.append({
                        "rule": rule_name,
                        "item_a": clash.Item1.DisplayName,
                        "item_b": clash.Item2.DisplayName,
                        "distance": clash.Distance if hasattr(clash, "Distance") else 0,
                        "location": extract_clash_location(clash),
                        "type": "hard-hard",  # or hard-soft, soft-soft
                    })
            
            except Exception as e:
                print(f"Warning: clash test {rule_name} failed: {e}")
        
        return clashes
    
    async def _run_python_clash_detection(self) -> List[Dict]:
        """Custom Python clash detection (for when NW not available)."""
        
        clashes = []
        
        # For each revit model pair
        for disc1, model1 in self.revit_models.items():
            for disc2, model2 in self.revit_models.items():
                if disc1 >= disc2:  # avoid duplicates
                    continue
                
                # Get all elements
                elems1 = model1.get("disciplines", {})
                elems2 = model2.get("disciplines", {})
                
                # Check for geometric intersections
                for elem1 in flatten(elems1.values()):
                    for elem2 in flatten(elems2.values()):
                        if self._check_intersection(elem1, elem2):
                            clashes.append({
                                "item_a": elem1["name"],
                                "item_b": elem2["name"],
                                "distance": 0,
                                "location": self._get_intersection_center(elem1, elem2),
                                "type": "python",
                            })
        
        return clashes
    
    def _filter_false_positives(self, clashes: List[Dict]) -> List[Dict]:
        """Filter false positives using heuristics."""
        
        filtered = []
        
        for clash in clashes:
            # Rule 1: Ignore clashes > 50mm (tolerance)
            if clash.get("distance", 0) > 50:
                continue
            
            # Rule 2: Ignore MEP-in-walls (intentional)
            if "wall" in clash["item_a"].lower() and any(
                x in clash["item_b"].lower() for x in ["pipe", "duct", "conduit"]
            ):
                continue
            
            # Rule 3: Ignore door in wall (intentional)
            if "wall" in clash["item_a"].lower() and "door" in clash["item_b"].lower():
                continue
            
            # Rule 4: Custom rule: check if items are on same level (coplanar)
            if self._are_coplanar(clash):
                continue
            
            filtered.append(clash)
        
        return filtered
    
    def _classify_severity(self, clashes: List[Dict]) -> List[Dict]:
        """Classify clashes by severity (critical, high, medium, low)."""
        
        for clash in clashes:
            item_a_type = clash["item_a"].split("_")[0].lower()
            item_b_type = clash["item_b"].split("_")[0].lower()
            
            # Structural interference = Critical
            if "structure" in item_a_type or "structure" in item_b_type:
                clash["severity"] = "critical"
            
            # MEP-to-MEP = High
            elif any(x in item_a_type for x in ["duct", "pipe", "conduit"]) and \
                 any(x in item_b_type for x in ["duct", "pipe", "conduit"]):
                clash["severity"] = "high"
            
            # MEP-to-Arch = Medium
            elif ("wall" in item_a_type or "wall" in item_b_type):
                clash["severity"] = "medium"
            
            # Others = Low
            else:
                clash["severity"] = "low"
        
        return clashes
    
    def _assign_responsibility(self, clashes: List[Dict]) -> List[Dict]:
        """Assign clash resolution to responsible discipline."""
        
        for clash in clashes:
            item_a_type = clash["item_a"].split("_")[0].lower()
            item_b_type = clash["item_b"].split("_")[0].lower()
            
            # Architecture owns walls/doors/windows changes
            if "wall" in item_a_type or "door" in item_a_type or "window" in item_a_type:
                clash["assigned_to"] = "Architecture"
            elif "wall" in item_b_type or "door" in item_b_type or "window" in item_b_type:
                clash["assigned_to"] = "Architecture"
            
            # Structure owns columns/beams/slabs
            elif "column" in item_a_type or "beam" in item_a_type or "slab" in item_a_type:
                clash["assigned_to"] = "Structure"
            elif "column" in item_b_type or "beam" in item_b_type or "slab" in item_b_type:
                clash["assigned_to"] = "Structure"
            
            # MEP owns ducts/pipes/conduits
            elif "duct" in item_a_type or "pipe" in item_a_type or "conduit" in item_a_type:
                clash["assigned_to"] = "MEP"
            elif "duct" in item_b_type or "pipe" in item_b_type or "conduit" in item_b_type:
                clash["assigned_to"] = "MEP"
            
            else:
                clash["assigned_to"] = "Coordinator"
        
        return clashes
```

**Tempo**: 10-30 min (consoante complexidade modelo)

---

### 3.3 Fluxo Coordenação Multi-Disciplina

#### Fluxo-5: Orquestrar Workflow de Coordenação

**Input**: Clash report + lista de clashes

**Etapas**:
1. **Criar issues** para cada clash (no Supabase ou issue tracker)
2. **Roulear a especialista** (e.g., Architecture para wall clashes)
3. **Especialista analisa** e propõe solução
4. **Validar solução** (não introduz novo clash?)
5. **Atualizar modelo** com resolução
6. **Registrar decisão** (audit trail)
7. **Output**: Issue tracking + coordenação matrix

**Pseudocódigo**:

```python
from enum import Enum
from datetime import datetime
import supabase

class ClashStatus(Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"
    WAIVED = "waived"

class CoordinationWorkflow:
    """Manage multi-discipline coordination workflow."""
    
    def __init__(self, supabase_client, project_id: str):
        self.db = supabase_client
        self.project_id = project_id
    
    async def create_coordination_issues(self, clashes: List[Dict]) -> List[str]:
        """Create coordination issues from clash report."""
        
        issue_ids = []
        
        for i, clash in enumerate(clashes):
            issue = {
                "project_id": self.project_id,
                "clash_id": f"CLH_{self.project_id}_{i:04d}",
                "item_a": clash["item_a"],
                "item_b": clash["item_b"],
                "severity": clash["severity"],
                "status": ClashStatus.OPEN.value,
                "assigned_to": clash.get("assigned_to", "Coordinator"),
                "location": clash.get("location"),
                "created_at": datetime.utcnow().isoformat(),
                "description": f"Conflict between {clash['item_a']} and {clash['item_b']}",
            }
            
            # Insert into Supabase
            response = self.db.table("coordination_issues").insert(issue).execute()
            issue_ids.append(response.data[0]["id"])
        
        return issue_ids
    
    async def route_to_specialist(self, issue_id: str, specialist: str) -> Dict:
        """Route issue to responsible specialist."""
        
        # Update assignment
        self.db.table("coordination_issues").update({
            "assigned_to": specialist,
            "status": ClashStatus.ASSIGNED.value,
            "assigned_at": datetime.utcnow().isoformat(),
        }).eq("id", issue_id).execute()
        
        # Notify specialist (email/slack integration)
        await self._notify_specialist(specialist, issue_id)
        
        return {"status": "assigned", "to": specialist}
    
    async def review_resolution(self, issue_id: str, proposed_solution: Dict) -> Dict:
        """Review specialist's proposed solution."""
        
        # Store solution
        self.db.table("coordination_issues").update({
            "proposed_solution": proposed_solution,
            "status": ClashStatus.IN_REVIEW.value,
            "reviewed_at": datetime.utcnow().isoformat(),
        }).eq("id", issue_id).execute()
        
        # Run validation: does new solution introduce other clashes?
        is_valid = await self._validate_solution(issue_id, proposed_solution)
        
        if is_valid:
            # Auto-approve if valid
            self.db.table("coordination_issues").update({
                "status": ClashStatus.RESOLVED.value,
                "resolved_at": datetime.utcnow().isoformat(),
            }).eq("id", issue_id).execute()
            
            return {"status": "resolved", "valid": True}
        else:
            return {"status": "rejected", "reason": "Solution introduces new clashes", "valid": False}
    
    async def close_issue(self, issue_id: str, notes: str = "") -> Dict:
        """Close coordination issue after resolution applied."""
        
        self.db.table("coordination_issues").update({
            "status": ClashStatus.CLOSED.value,
            "closed_at": datetime.utcnow().isoformat(),
            "close_notes": notes,
        }).eq("id", issue_id).execute()
        
        return {"status": "closed"}
    
    async def get_coordination_matrix(self) -> Dict:
        """Generate multi-discipline coordination matrix."""
        
        issues = self.db.table("coordination_issues").select("*").eq(
            "project_id", self.project_id
        ).execute()
        
        # Build matrix
        matrix = {
            "total_clashes": len(issues.data),
            "by_severity": {},
            "by_discipline": {},
            "by_status": {},
            "timeline": {},
        }
        
        for issue in issues.data:
            # Count by severity
            sev = issue["severity"]
            matrix["by_severity"][sev] = matrix["by_severity"].get(sev, 0) + 1
            
            # Count by assigned discipline
            disc = issue["assigned_to"]
            matrix["by_discipline"][disc] = matrix["by_discipline"].get(disc, 0) + 1
            
            # Count by status
            stat = issue["status"]
            matrix["by_status"][stat] = matrix["by_status"].get(stat, 0) + 1
        
        return matrix
```

**Tempo**: Depende de número de clashes (async, ~5 min setup + resolução especialista)

---

### 3.4 Fluxo Extração de Cronograma

#### Fluxo-6: Extrair Cronograma do BIM (Revit)

**Input**: Modelo Revit com fases de construção

**Etapas**:
1. **Extrair Phases** do Revit
2. **Mapear elementos** → fase construtiva
3. **Calcular duração** por fase (baseado em volume/complexidade)
4. **Detectar dependências** (precedência de fases)
5. **Analisar impacto** de clashes na duração
6. **Output**: Schedule JSON + Gantt chart

**Pseudocódigo**:

```python
import json
from datetime import datetime, timedelta
from typing import List, Dict

class BIMScheduleExtractor:
    """Extract construction schedule from BIM model."""
    
    def __init__(self, revit_doc):
        self.doc = revit_doc
        self.phases = self._extract_phases()
        self.elements = self._extract_phased_elements()
    
    def _extract_phases(self) -> List[Dict]:
        """Extract construction phases from Revit."""
        
        phases = []
        
        for phase in self.doc.Phases:
            phases.append({
                "id": phase.Id,
                "name": phase.Name,
                "phase_created": phase.PhaseCreated,  # When created in sequence
                "phase_demolished": phase.PhaseDemolished if hasattr(phase, "PhaseDemolished") else None,
            })
        
        return sorted(phases, key=lambda p: p["phase_created"])
    
    def _extract_phased_elements(self) -> Dict[str, List[Dict]]:
        """Extract elements grouped by phase."""
        
        phased_elements = {phase["name"]: [] for phase in self.phases}
        
        # Query all elements with phase info
        all_elements = self.doc.GetElements()
        
        for elem in all_elements:
            if hasattr(elem, "CreatedPhaseId"):
                created_phase_id = elem.CreatedPhaseId
                created_phase = self.doc.GetElement(created_phase_id)
                
                if created_phase:
                    phased_elements[created_phase.Name].append({
                        "id": elem.Id,
                        "name": elem.Name,
                        "category": elem.Category.Name,
                        "level": elem.LevelName if hasattr(elem, "LevelName") else None,
                        "volume": calculate_volume(elem),
                        "surface_area": calculate_surface_area(elem),
                    })
        
        return phased_elements
    
    def extract_schedule(self, base_date: datetime) -> Dict:
        """Extract and calculate construction schedule."""
        
        schedule = {
            "project_start": base_date.isoformat(),
            "phases": [],
            "total_duration_days": 0,
        }
        
        current_date = base_date
        
        for i, phase in enumerate(self.phases):
            phase_elements = self.phased_elements.get(phase["name"], [])
            
            # Estimate duration based on complexity
            duration_days = self._estimate_phase_duration(phase_elements)
            
            phase_data = {
                "name": phase["name"],
                "sequence": i + 1,
                "start_date": current_date.isoformat(),
                "duration_days": duration_days,
                "end_date": (current_date + timedelta(days=duration_days)).isoformat(),
                "element_count": len(phase_elements),
                "estimated_volume_m3": sum(e.get("volume", 0) for e in phase_elements),
                "dependencies": self._identify_phase_dependencies(phase),
            }
            
            schedule["phases"].append(phase_data)
            current_date += timedelta(days=duration_days)
        
        schedule["total_duration_days"] = (current_date - base_date).days
        
        return schedule
    
    def _estimate_phase_duration(self, elements: List[Dict]) -> int:
        """Estimate duration for phase based on element complexity."""
        
        # Simple formula: volume + count-based
        total_volume = sum(e.get("volume", 0) for e in elements)
        element_count = len(elements)
        
        # Assumptions: 10 m³/day productivity, base 5 days per phase
        days_from_volume = max(5, int(total_volume / 10))
        days_from_count = max(5, element_count // 100)
        
        return max(days_from_volume, days_from_count)
    
    def analyze_clash_impact(self, clashes: List[Dict]) -> Dict:
        """Analyze impact of unresolved clashes on schedule."""
        
        impact = {
            "clashes_with_schedule_impact": 0,
            "critical_clashes": [],
            "estimated_delay_days": 0,
        }
        
        for clash in clashes:
            if clash["severity"] == "critical":
                # Critical clashes can delay 2-5 days each
                impact["clashes_with_schedule_impact"] += 1
                impact["critical_clashes"].append(clash)
                impact["estimated_delay_days"] += 3  # default 3 days delay
        
        return impact
```

**Tempo**: 5-10 min

---

### 3.5 Fluxo Aprovação Inteligente

#### Fluxo-7: Workflow de Aprovação com Rastreabilidade

**Input**: Lista de clashes resolvidos + mudanças propostas

**Etapas**:
1. **Identificar decisores** (based on severity + discipline)
2. **Roulear aprovação** em cascata (Coordinator → BIM Manager → Project Manager)
3. **Rastrear decisão** (who, when, why)
4. **Gerar change order** (se impacta custo/prazo)
5. **Arquivo decisão** para audit trail
6. **Output**: Approval log + change orders

**Pseudocódigo**:

```python
from enum import Enum
from dataclasses import dataclass
import uuid

class ApprovalLevel(Enum):
    BIM_COORDINATOR = 1
    BIM_MANAGER = 2
    PROJECT_MANAGER = 3

@dataclass
class ApprovalDecision:
    id: str
    clash_id: str
    approved_by: str
    approval_level: ApprovalLevel
    decision: str  # "approved", "rejected", "needs_revision"
    notes: str
    timestamp: datetime
    change_order_required: bool

class ApprovalWorkflow:
    """Manage approval workflow for clash resolutions."""
    
    def __init__(self, supabase_client):
        self.db = supabase_client
        self.approval_chain = [
            ApprovalLevel.BIM_COORDINATOR,
            ApprovalLevel.BIM_MANAGER,
            ApprovalLevel.PROJECT_MANAGER,
        ]
    
    async def initiate_approval(self, issue_id: str, proposed_resolution: Dict) -> Dict:
        """Start approval workflow."""
        
        # Determine approval level needed based on severity
        issue = self.db.table("coordination_issues").select("*").eq("id", issue_id).execute()
        severity = issue.data[0]["severity"]
        
        if severity == "critical":
            start_level = ApprovalLevel.BIM_MANAGER
        elif severity == "high":
            start_level = ApprovalLevel.BIM_COORDINATOR
        else:
            start_level = ApprovalLevel.BIM_COORDINATOR
        
        approval_task = {
            "id": str(uuid.uuid4()),
            "issue_id": issue_id,
            "current_level": start_level.name,
            "status": "pending",
            "proposed_resolution": proposed_resolution,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self.db.table("approval_tasks").insert(approval_task).execute()
        
        # Notify first approver
        await self._notify_approver(start_level)
        
        return approval_task
    
    async def review_and_approve(
        self,
        approval_id: str,
        decision: str,  # "approved", "rejected", "needs_revision"
        reviewer: str,
        notes: str = "",
    ) -> Dict:
        """Process approval decision."""
        
        approval = self.db.table("approval_tasks").select("*").eq("id", approval_id).execute()
        approval_data = approval.data[0]
        
        # Record decision
        decision_log = ApprovalDecision(
            id=str(uuid.uuid4()),
            clash_id=approval_data["issue_id"],
            approved_by=reviewer,
            approval_level=ApprovalLevel[approval_data["current_level"]],
            decision=decision,
            notes=notes,
            timestamp=datetime.utcnow(),
            change_order_required=self._requires_change_order(approval_data),
        )
        
        self.db.table("approval_decisions").insert({
            "id": decision_log.id,
            "issue_id": decision_log.clash_id,
            "approved_by": reviewer,
            "decision": decision,
            "notes": notes,
            "timestamp": decision_log.timestamp.isoformat(),
            "change_order_required": decision_log.change_order_required,
        }).execute()
        
        if decision == "approved":
            # Check if next approval level needed
            current_index = self.approval_chain.index(ApprovalLevel[approval_data["current_level"]])
            
            if current_index < len(self.approval_chain) - 1:
                # Move to next level
                next_level = self.approval_chain[current_index + 1]
                
                self.db.table("approval_tasks").update({
                    "current_level": next_level.name,
                }).eq("id", approval_id).execute()
                
                await self._notify_approver(next_level)
                
                return {"status": "escalated", "to": next_level.name}
            else:
                # Final approval
                self.db.table("approval_tasks").update({
                    "status": "approved",
                }).eq("id", approval_id).execute()
                
                # Update original issue
                self.db.table("coordination_issues").update({
                    "status": "closed",
                }).eq("id", approval_data["issue_id"]).execute()
                
                # Generate change order if needed
                if decision_log.change_order_required:
                    await self._generate_change_order(approval_data["issue_id"])
                
                return {"status": "approved", "final": True}
        
        elif decision == "rejected":
            self.db.table("approval_tasks").update({
                "status": "rejected",
            }).eq("id", approval_id).execute()
            
            # Revert to open
            self.db.table("coordination_issues").update({
                "status": "open",
            }).eq("id", approval_data["issue_id"]).execute()
            
            return {"status": "rejected"}
        
        return {"status": decision}
    
    def _requires_change_order(self, approval_data: Dict) -> bool:
        """Determine if resolution requires change order."""
        
        # Placeholder: check against cost/schedule impact
        # For critical clashes, likely requires change order
        return True  # TODO: implement cost estimation
    
    async def _generate_change_order(self, issue_id: str) -> Dict:
        """Generate change order for scope/cost/schedule impact."""
        
        # TODO: integrate with orcamento agent
        change_order = {
            "issue_id": issue_id,
            "status": "draft",
            "estimated_cost": 0,  # TBD by orcamento
            "estimated_duration_impact_days": 0,  # from schedule analysis
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self.db.table("change_orders").insert(change_order).execute()
        
        return change_order
```

**Tempo**: ~2 min por approval (depends on decision time)

---

### 3.6 Fluxo Saída & Normalização

#### Fluxo-8: Gerar Relatórios e Entregas (Output)

**Input**: Coordenação completa + decisões finalizadas

**Etapas**:
1. **Gerar Clash Report** (PDF com visualizações)
2. **Gerar Coordination Matrix** (Excel com resumo)
3. **Gerar Schedule Analysis** (Gantt com impact)
4. **Exportar DXF** (modelo normalizado)
5. **Gerar Playbook** (próximos passos operacionais)

**Pseudocódigo**:

```python
from jinja2 import Environment, FileSystemLoader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, PageBreak, SimpleDocTemplate
import csv

class ReportGenerator:
    """Generate comprehensive S4 coordination reports."""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.template_env = Environment(loader=FileSystemLoader("templates/"))
    
    def generate_clash_report_pdf(self, clashes: List[Dict], output_file: str) -> str:
        """Generate clash report PDF."""
        
        doc = SimpleDocTemplate(output_file)
        elements = []
        
        # Title
        title = Paragraph(f"<b>Coordination Clash Report</b><br/>{self.project_name}", style)
        elements.append(title)
        elements.append(PageBreak())
        
        # Executive Summary
        summary_data = [
            ["Total Clashes", len(clashes)],
            ["Critical", sum(1 for c in clashes if c["severity"] == "critical")],
            ["High", sum(1 for c in clashes if c["severity"] == "high")],
            ["Medium", sum(1 for c in clashes if c["severity"] == "medium")],
            ["Low", sum(1 for c in clashes if c["severity"] == "low")],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(summary_table)
        elements.append(PageBreak())
        
        # Detailed clash list
        clash_data = [["Clash ID", "Item A", "Item B", "Severity", "Status"]]
        for clash in clashes:
            clash_data.append([
                clash.get("id", "N/A"),
                clash["item_a"][:30],
                clash["item_b"][:30],
                clash["severity"],
                clash.get("status", "open"),
            ])
        
        clash_table = Table(clash_data)
        clash_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(clash_table)
        
        # Build PDF
        doc.build(elements)
        
        return output_file
    
    def generate_coordination_matrix_xlsx(self, issues: List[Dict], output_file: str) -> str:
        """Generate coordination matrix Excel."""
        
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Clash ID",
                "Item A",
                "Item B",
                "Severity",
                "Assigned To",
                "Status",
                "Resolution Notes",
                "Approval Status",
            ])
            
            # Data
            for issue in issues:
                writer.writerow([
                    issue.get("id"),
                    issue["item_a"],
                    issue["item_b"],
                    issue["severity"],
                    issue.get("assigned_to"),
                    issue.get("status"),
                    issue.get("resolution_notes", ""),
                    issue.get("approval_status", "pending"),
                ])
        
        return output_file
    
    def generate_schedule_analysis_gantt(self, schedule: Dict, output_file: str) -> str:
        """Generate schedule Gantt chart (HTML/SVG)."""
        
        # Use plotly for Gantt
        import plotly.graph_objects as go
        from datetime import datetime
        
        fig = go.Figure()
        
        for phase in schedule["phases"]:
            fig.add_trace(go.Bar(
                x=[phase["duration_days"]],
                y=[phase["name"]],
                orientation="h",
                name=phase["name"],
            ))
        
        fig.update_layout(
            title=f"Construction Schedule - {self.project_name}",
            xaxis_title="Duration (days)",
            yaxis_title="Phase",
            barmode="stack",
        )
        
        fig.write_html(output_file)
        
        return output_file
    
    def generate_operational_playbook(self, clashes: List[Dict], output_file: str) -> str:
        """Generate operational playbook for next steps."""
        
        template = self.template_env.get_template("s4_playbook.md")
        
        playbook_content = template.render(
            project_name=self.project_name,
            total_clashes=len(clashes),
            critical_clashes=sum(1 for c in clashes if c["severity"] == "critical"),
            next_steps=[
                "Review critical clashes with discipline leads",
                "Schedule coordination meetings",
                "Update BIM models with approved resolutions",
                "Re-run clash detection to validate",
                "Close remaining issues",
            ],
        )
        
        with open(output_file, "w") as f:
            f.write(playbook_content)
        
        return output_file
```

**Tempo**: 5 min

---

## 4. INTEGRAÇÃO REVIT 2027 MCP

### 4.1 Connector Revit via MCP

```
Manta S4 Agent (Python/Node)
    ↓
    └─→ Revit 2027 MCP (C# / .NET SDK)
            ├─ Document API (open, read, modify)
            ├─ Element API (extract, query)
            ├─ Geometry API (BoundingBox, Intersections)
            ├─ Parameter API (read/write project parameters)
            └─ Phases API (construction phases)
```

### 4.2 Fluxo Técnico

**Setup**:
1. Revit 2027+ instalado (com API support)
2. Revit SDK instalado (Revit SDK 2027)
3. MCP bridge: `mcp-revit-bridge` (HTTP server)

**Integração Python → Revit MCP**:

```python
import httpx
from typing import Dict, List

class RevitMCPClient:
    """Client for Revit 2027 MCP integration."""
    
    def __init__(self, mcp_endpoint: str = "http://localhost:8080"):
        self.endpoint = mcp_endpoint
        self.client = httpx.AsyncClient()
    
    async def open_document(self, rvt_path: str) -> Dict:
        """Open Revit document via MCP."""
        
        response = await self.client.post(
            f"{self.endpoint}/revit/open",
            json={"path": rvt_path}
        )
        return response.json()
    
    async def extract_categories(self, doc_id: str) -> Dict:
        """Extract all categories from document."""
        
        response = await self.client.get(
            f"{self.endpoint}/revit/{doc_id}/categories"
        )
        return response.json()
    
    async def query_elements(
        self,
        doc_id: str,
        category: str,
        filters: Dict = None
    ) -> List[Dict]:
        """Query elements by category with optional filters."""
        
        response = await self.client.post(
            f"{self.endpoint}/revit/{doc_id}/elements",
            json={"category": category, "filters": filters or {}}
        )
        return response.json()
    
    async def extract_shared_coordinates(self, doc_id: str) -> Dict:
        """Extract shared coordinates (project base point)."""
        
        response = await self.client.get(
            f"{self.endpoint}/revit/{doc_id}/shared-coordinates"
        )
        return response.json()
```

---

## 5. INTEGRAÇÃO NAVISWORKS (CLASH DETECTION)

### 5.1 Opções de Integração

#### Opção A: Navisworks COM API (Windows Direct)

```csharp
// C# example for Navisworks COM
using Autodesk.Navisworks.Api;
using Autodesk.Navisworks.Api.Clash;

public static void RunClashDetection(string nwcPath) {
    var app = new NavisWorksApplication();
    var doc = app.OpenFile(nwcPath);
    
    // Run built-in clash tests
    foreach (var test in doc.ClashTests) {
        test.Run();
        var results = test.ClashResults;
        foreach (var clash in results) {
            Console.WriteLine($"Clash: {clash.Item1.DisplayName} vs {clash.Item2.DisplayName}");
        }
    }
}
```

#### Opção B: HuskyBIM REST API (Bentley Cloud)

```python
# Python example for HuskyBIM API
import httpx

async def run_clash_detection_huskybim(project_id: str):
    """Run clash detection via HuskyBIM API."""
    
    async with httpx.AsyncClient() as client:
        # Create clash test
        response = await client.post(
            f"https://api.huskybim.com/projects/{project_id}/clash-tests",
            json={
                "name": "Metro_S4_Coordination",
                "test_groups": [
                    {"group_a": "Architecture", "group_b": "Structure"},
                    {"group_a": "Structure", "group_b": "MEP_Mechanical"},
                    {"group_a": "MEP_Mechanical", "group_b": "MEP_Electrical"},
                ]
            },
            headers={"Authorization": f"Bearer {HUSKYBIM_API_KEY}"}
        )
        
        # Poll for results
        test_id = response.json()["id"]
        for _ in range(60):  # 5 minute timeout
            result = await client.get(
                f"https://api.huskybim.com/clash-tests/{test_id}/results",
                headers={"Authorization": f"Bearer {HUSKYBIM_API_KEY}"}
            )
            
            if result.json()["status"] == "completed":
                return result.json()["clashes"]
            
            await asyncio.sleep(5)
```

---

## 6. PLAYBOOK OPERACIONAL S4

### 6.1 Intake Estruturado

**Checklist de entrada (usuário S4 preenchido no chat)**:

1. **Dados básicos**:
   - [ ] Nome do projeto (ex: "Metrô Linha 4 Trecho C02")
   - [ ] Fases de projeto (estudo/básico/executivo/obra)
   - [ ] Disciplinas envolvidas (arquitetura, estrutura, MEP)

2. **Arquivos**:
   - [ ] Modelos Revit (.rvt) por disciplina
   - [ ] Arquivo NWC/NWD federado (se disponível)
   - [ ] IFC export (como fallback)

3. **Configuração**:
   - [ ] Regras de clash (personalizar ou usar padrão S4)
   - [ ] Limites de tolerância (gap/overlap em mm)
   - [ ] Disciplinas críticas para validação

4. **Aprovação**:
   - [ ] Definir cadeia de aprovação (quem aprova o quê)
   - [ ] E-mails de notificação

---

### 6.2 Processos Automáticos (Orchestration)

#### Process-1: Load Models
```yaml
trigger: files_received(*.rvt, *.nwc)
steps:
  - load_revit_models()
  - load_navisworks_model()
  - normalize_coordinates()
  - output: loaded_models (JSON)
timeout: 15m
```

#### Process-2: Run Clash Detection
```yaml
trigger: models_loaded
depends: Process-1
steps:
  - configure_clash_rules()
  - execute_navisworks_clashes()
  - execute_python_clashes()
  - filter_false_positives()
  - classify_severity()
  - output: clash_report (JSON)
timeout: 30m
retry: 2
```

#### Process-3: Coordination Workflow
```yaml
trigger: clashes_detected
depends: Process-2
steps:
  - create_coordination_issues()
  - assign_to_disciplines()
  - notify_specialists()
  - output: coordination_issues (JSON)
timeout: 5m
parallel_specialists: 3
```

#### Process-4: Schedule Analysis
```yaml
trigger: models_loaded
depends: Process-1
steps:
  - extract_construction_phases()
  - estimate_phase_durations()
  - analyze_clash_impact()
  - generate_schedule_report()
  - output: schedule_analysis (JSON)
timeout: 10m
```

#### Process-5: Approval Workflow
```yaml
trigger: resolutions_proposed
depends: Process-3
steps:
  - initiate_approval_chain()
  - route_to_approvers()
  - track_decisions()
  - generate_change_orders()
  - output: approval_log (JSON)
timeout: varies (depends on reviewer response)
```

#### Process-6: Generate Reports
```yaml
trigger: all_processes_complete
depends: [Process-2, Process-3, Process-4, Process-5]
steps:
  - generate_clash_report_pdf()
  - generate_coordination_matrix_xlsx()
  - generate_schedule_gantt()
  - generate_playbook_md()
  - export_normalized_dxf()
  - output: deliverables (files)
timeout: 15m
```

---

### 6.3 Saída (Deliverables)

Após sucesso em todos os processos:

**Arquivos**:
1. `CLH-REPORT-[projeto]-[data].pdf` (clash report com visualizações)
2. `COORDINATION-MATRIX-[projeto].xlsx` (matriz disciplinas)
3. `SCHEDULE-ANALYSIS-[projeto].html` (Gantt chart)
4. `[projeto]-S4-PLAYBOOK.md` (próximos passos)
5. `[projeto]-COORDINATED.dxf` (modelo normalizado)

**Documentação no chat**:
- Resumo executivo de coordenação
- Top clashes críticas (com recomendações)
- Impacto estimado em cronograma
- Status de aprovações (cadeia de aprovação)
- Próximos passos (refinement, implementação, validação)

---

## 7. TIMELINE & DEPENDÊNCIAS (Q1 2027 → Q2 2027)

### 7.1 Fases de Entrega

| Fase | Período | Entregáveis | Dependências |
|------|---------|-------------|--------------|
| **Alpha** | Q1 2027 (Jan-Mar) | Revit loader + Navisworks integrator + clash detector | Revit 2027 MCP + Navisworks COM/HuskyBIM API |
| **Beta** | Q1 2027 (Feb-Mar) | Coordination workflow + assignment logic | Supabase tables setup + approval template |
| **Gamma** | Q2 2027 (Apr-May) | Schedule extractor + approval workflow + report generation | MS Project XML bridge + PDF/Excel templates |
| **GA** | Q2 2027 (May-Jun) | Full S4 pipeline + training + documentation | All above + user feedback + playbook finalization |

### 7.2 Dependências Técnicas

```
Revit 2027 MCP
├─ Document API (✅ available in Revit SDK 2027)
├─ Element extraction (✅ available)
├─ Geometry API (✅ available)
└─ Parameter API (✅ available)

Navisworks Integration
├─ COM API (✅ available on Windows)
├─ HuskyBIM REST API (🔄 Q1 2027 contract)
└─ Clash rule configuration (🔄 custom rules Q1 2027)

Supabase Backend
├─ coordination_issues table (🔄 Q1 2027 schema)
├─ approval_tasks table (🔄 Q1 2027 schema)
├─ approval_decisions table (🔄 Q1 2027 schema)
└─ change_orders table (🔄 Q1 2027 schema)

Report Generation
├─ Jinja2 templates (✅ available)
├─ ReportLab (✅ available)
├─ Plotly (✅ available)
└─ Excel writer (✅ available)
```

### 7.3 Gráfico de Gantt (Simplificado)

```
Q1 2027 ━━━━━━━ | Q2 2027 ━━━━━━━
 J  F  M  │  A  M  J  │

[Revit MCP Wrapper ▓▓▓▓▓▓]
 [Navisworks Integrator ▓▓▓▓▓▓▓]
  [Clash Detection Engine ▓▓▓▓▓▓▓]
   [Coordination Workflow ▓▓▓▓▓▓▓▓]
    [Schedule Extractor ▓▓▓▓▓▓]
     [Approval Workflow ▓▓▓▓▓▓▓▓▓]
      [Report Generator ▓▓▓▓▓▓▓▓▓]
       [Integration Testing ▓▓▓▓▓▓]
        [User Training ▓▓▓▓▓]
         [GA Release ▓]
```

---

## 8. RISCOS & MITIGAÇÃO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Revit MCP instabilidade ou não disponível | Médio | Alto | Fallback com COM API + IFC parser |
| Navisworks API de terceiros indisponível | Médio | Alto | Implementar Python clash detection nativa |
| Modelos mal-coordenados (sem shared coords) | Alto | Médio | Auto-detect + prompt user para alinhamento |
| False positives em detecção de clashes | Alto | Médio | Implementar ML-based filtering + manual review |
| Aprovadores não respondem a tempo | Médio | Médio | Escalate automático após 48h, reminder emails |
| Performance com modelos >100MB | Baixo | Alto | Chunking por disciplina/level, async processing |
| Integração MS Project para schedule | Médio | Médio | Fallback com Revit Phase extraction |

---

## 9. SUCESSO & KPIs

### 9.1 Métricas de Qualidade

1. **Cobertura de Coordenação**: 95% de clashes detectados (vs. manual 70%)
2. **Tempo médio processamento**: <2 horas ponta-a-ponta (vs. manual 2-3 dias)
3. **Taxa de falsos positivos**: <5% (após filtering)
4. **Resolução tempo**: 70% clashes resolvidos em <48h via workflow automático
5. **Aprovação compliance**: 100% das decisões rastreadas e documentadas

### 9.2 Adoção

- **Q1 2027**: 3 projetos piloto (internos + clientes beta)
- **Q2 2027**: 10+ projetos (produção)
- **Q3 2027**: 30+ projetos (padrão S4)

---

## 10. PRÓXIMOS PASSOS

1. **Gate Humano** (MN approval) — este documento + plano risco (1 semana)
2. **Revit 2027 MCP Availability Check** — confirmar MCP + API access (1 semana)
3. **Navisworks Integration Contract** — assinar SLA HuskyBIM ou COM setup (2 semanas)
4. **Dev Alpha Sprint** — Revit loader + Navisworks integrator (4 semanas, Q1 2027)
5. **Dev Beta Sprint** — Clash detector + filtering logic (3 semanas, Q1 2027)
6. **Dev Gamma Sprint** — Coordination workflow + approval engine (4 semanas, Q1-Q2 2027)
7. **Testing & Validation** — 3 projetos piloto (4 semanas, Q2 2027)
8. **GA Release** — documentação + playbook training (2 semanas, Q2 2027)

---

## REFERÊNCIAS

- **Revit 2027 API Documentation**: [Link to official Autodesk docs, TBD]
- **Navisworks API Documentation**: https://www.autodesk.com/developer/navisworks
- **HuskyBIM API (Bentley)**: https://api.huskybim.com/docs (if partnership confirmed)
- **ifcopenshell Python Docs**: https://ifcopenshell.org/python/
- **IFC 4.3 Schema**: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/
- **NBR 15965 (BIM in construction)**: [Internal reference]
- **Manta Supabase Schema**: [Internal wiki, access via SharePoint]

---

**Aprovações Pendentes**:
- [ ] MN (Arquiteto IA) — estratégia geral
- [ ] CTO Infraestrutura — arquitetura técnica BIM
- [ ] Revit/Navisworks Partner — viabilidade técnica dos APIs
- [ ] CFO — orçamento Q1 2027 → Q2 2027
