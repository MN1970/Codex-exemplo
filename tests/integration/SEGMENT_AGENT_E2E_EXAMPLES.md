# Exemplos E2E para Agentes de Segmentos (S1-S10)

Padrões de teste para validar cada agente vertical (Manta 03-S1 até S10)

---

## S1: Rodovias — E2E Test Pattern

### Padrão de Intent

```typescript
test('E2E S1: Rodovia agent processa intent de pavimentação', async () => {
  // Intent parsing
  const intent = await intentParser.parseCommitMessage(
    'create agent S1 rodovia CBUQ pavimentação DNIT'
  );
  
  expect(intent.params.segment).toBe('rodovia');
  expect(intent.params.agentCode).toBe('s1');
  
  // Code generation com templates S1
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('CBUQ'); // Concreto Asfáltico
  expect(code).toContain('DNIT'); // Departamento Nacional Infraestrutura
  
  // CI com validação S1 (SICRO, terraplenagem, BGS)
  const workflow = await ciOrchestrator.triggerCI(1001, 'feature/s1-rodovia');
  
  await new Promise(resolve => setTimeout(resolve, 150));
  const status = await ciOrchestrator.getBuildStatus(workflow);
  
  expect(status?.passed).toBe(true);
  expect(status?.testsPassed).toBeGreaterThan(30);
  
  // Sync com metadados S1
  await coworkSync.syncPRData(1001, {
    prNumber: 1001,
    status: PRAnalysisStatus.COMPLETED,
    buildStatus: status,
    agentMetadata: {
      segment: 'rodovia',
      standards: ['NBR 12264', 'DNIT 006/2003'],
      sicroItems: ['CBUQ', 'BGS', 'Terraplenagem'],
    },
  });
  
  const isConsistent = await coworkSync.verifyConsistency();
  expect(isConsistent).toBe(true);
});
```

---

## S2: OAE (Pontes/Viadutos) — E2E Test Pattern

### Padrão de Validação Estrutural

```typescript
test('E2E S2: OAE agent valida ponte com NBR 7187', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create bridge design agent S2 NBR 7187 verificação estrutural'
  );
  
  expect(intent.params.segment).toBe('oae');
  expect(intent.params.agentCode).toBe('s2');
  
  // Code gen com suporte a cálculos estruturais
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('NBR 7187'); // Ponte em concreto
  expect(code).toContain('StructuralAnalysis');
  
  // CI com testes de cálculo estrutural
  const workflowId = await ciOrchestrator.triggerCI(2001, 'feature/s2-bridge');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.coverage).toBeGreaterThanOrEqual(80);
  
  // Sync com validações estruturais
  await coworkSync.syncPRData(2001, {
    prNumber: 2001,
    agentMetadata: {
      segment: 'oae',
      structuralValidations: [
        'Momento fletor máximo',
        'Esforço cortante',
        'Deflexão máxima',
      ],
      norms: ['NBR 7187', 'NBR 8681', 'NBR 6118'],
    },
  });
  
  const consistent = await coworkSync.verifyConsistency();
  expect(consistent).toBe(true);
});
```

---

## S3: Ferrovia — E2E Test Pattern

### Padrão de Validação de Via Permanente

```typescript
test('E2E S3: Ferrovia agent processa trilho e dormente', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S3 ferrovia via permanente AMV dormente'
  );
  
  expect(intent.params.segment).toBe('ferrovia');
  expect(intent.params.agentCode).toBe('s3');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('ViaPermanente');
  expect(code).toContain('Dormente');
  expect(code).toContain('AMV'); // Aparelho de Mudança de Via
  
  const workflowId = await ciOrchestrator.triggerCI(3001, 'feature/s3-railway');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  
  // Validações específicas de ferrovia
  await coworkSync.syncPRData(3001, {
    prNumber: 3001,
    agentMetadata: {
      segment: 'ferrovia',
      railSpecifications: {
        type: 'UIC54',
        gauge: '1000mm',
        maxGradient: '2.5%',
      },
      sleepperSpacing: '0.6m',
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S4: Metrô — E2E Test Pattern

### Padrão de Validação de Estação

```typescript
test('E2E S4: Metrô agent valida construção de estação', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S4 metrô NATM estação PSD ventilação'
  );
  
  expect(intent.params.segment).toBe('metro');
  expect(intent.params.agentCode).toBe('s4');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('NATM'); // New Austrian Tunnelling Method
  expect(code).toContain('StationDesign');
  expect(code).toContain('VentilationSystem');
  
  const workflowId = await ciOrchestrator.triggerCI(4001, 'feature/s4-metro-l4');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  expect(status?.testsPassed).toBeGreaterThan(35);
  
  // Validações de metrô (linha 4, 5, VLT)
  await coworkSync.syncPRData(4001, {
    prNumber: 4001,
    agentMetadata: {
      segment: 'metro',
      line: 'Linha 4',
      stationSpacing: '800-1200m',
      ventilationRequirement: 'Pressurization',
      constructionMethod: 'NATM',
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S6: Portos — E2E Test Pattern (Novo)

### Padrão de Validação ANTAQ

```typescript
test('E2E S6: Porto agent valida operação portuária ANTAQ', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S6 porto ANTAQ terminal contêiner molhe dragagem'
  );
  
  expect(intent.params.segment).toBe('porto');
  expect(intent.params.agentCode).toBe('s6');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('PortOperations');
  expect(code).toContain('ANTAQ');
  expect(code).toContain('TerminalManagement');
  expect(code).toContain('DredgingOperations');
  
  // CI com validações portuárias
  const workflowId = await ciOrchestrator.triggerCI(6001, 'feature/s6-porto');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  
  // Sync com metadados portuários
  await coworkSync.syncPRData(6001, {
    prNumber: 6001,
    status: PRAnalysisStatus.COMPLETED,
    buildStatus: status,
    agentMetadata: {
      segment: 'porto',
      portType: 'Public Port',
      terminalTypes: ['Container', 'Bulk', 'General Cargo'],
      dockingFacilities: {
        numberOfBerths: 4,
        maxDraft: '14.5m',
        maxVesselSize: '5000 TEU',
      },
      regulatoryFramework: ['ANTAQ', 'PIANC Guidelines'],
      dredgingCapacity: '2M m³/year',
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S7: Aeroportos — E2E Test Pattern (Novo)

### Padrão de Validação ANAC

```typescript
test('E2E S7: Aeroporto agent valida operações aéreas ANAC', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S7 aeroporto ANAC pista ICAO balizamento TPS TECA'
  );
  
  expect(intent.params.segment).toBe('aeroporto');
  expect(intent.params.agentCode).toBe('s7');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('AirportOperations');
  expect(code).toContain('RunwayManagement');
  expect(code).toContain('NavigationAids');
  expect(code).toContain('GroundSupportEquipment');
  
  const workflowId = await ciOrchestrator.triggerCI(7001, 'feature/s7-airport');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  
  // Sync com metadados aeroportuários
  await coworkSync.syncPRData(7001, {
    prNumber: 7001,
    agentMetadata: {
      segment: 'aeroporto',
      airportCategory: 'International',
      runwayConfiguration: {
        numberOfRunways: 2,
        dimensions: ['3500m x 45m', '2500m x 40m'],
        pavementType: 'Concrete',
      },
      navigationAids: {
        ILS: 'Cat II/III',
        NDB: true,
        VOR: true,
      },
      capacity: {
        passengers: '12M/year',
        cargo: '150K tons/year',
        movements: '80K/year',
      },
      compliance: ['ANAC RBAC', 'ICAO Annex 14', 'FAA ACs'],
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S8: Saneamento — E2E Test Pattern (Novo - Prioridade AySA)

### Padrão de Validação SNIS

```typescript
test('E2E S8: Saneamento agent valida ETA/ETE com SNIS (PRIORITY)', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S8 saneamento ETA ETE adutora SNIS drenagem urbana'
  );
  
  expect(intent.params.segment).toBe('saneamento');
  expect(intent.params.agentCode).toBe('s8');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('WaterTreatment');
  expect(code).toContain('WastewaterTreatment');
  expect(code).toContain('PipelineDesign');
  expect(code).toContain('SNISReporting');
  
  // CI com testes de qualidade de água
  const workflowId = await ciOrchestrator.triggerCI(8001, 'feature/s8-saneamento');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  expect(status?.testsPassed).toBeGreaterThan(45); // Mais testes para saneamento
  
  // Sync com compliance SNIS/Lei 14.026
  await coworkSync.syncPRData(8001, {
    prNumber: 8001,
    status: PRAnalysisStatus.COMPLETED,
    buildStatus: status,
    agentMetadata: {
      segment: 'saneamento',
      services: {
        waterSupply: {
          capacity: '1500 L/s',
          treatmentProcess: 'Conventional',
          standards: ['NBR 12211', 'NBR 12212'],
        },
        wastewater: {
          capacity: '1200 L/s',
          treatmentLevel: 'Secondary',
          effluent: {
            BOD: '60 mg/L max',
            TSS: '80 mg/L max',
          },
        },
        drainageUrban: {
          coverage: '85%',
          floodMitigation: true,
        },
      },
      snisCompliance: {
        dataReporting: true,
        institutionalFramework: 'Lei 14.026',
        universalAccess2033: true,
      },
      aySAMetadata: { // AySA específico
        serviceArea: 'Buenos Aires',
        populationServed: '2.3M',
      },
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S9: Energia — E2E Test Pattern (Novo - ANEEL/State Grid)

### Padrão de Validação ANEEL

```typescript
test('E2E S9: Energia agent valida transmissão LT ANEEL RAP', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S9 energia transmissão LT subestação ANEEL RAP leilão'
  );
  
  expect(intent.params.segment).toBe('energia');
  expect(intent.params.agentCode).toBe('s9');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('TransmissionLine');
  expect(code).toContain('Substation');
  expect(code).toContain('ANEELCompliance');
  expect(code).toContain('AuctionManagement');
  
  // CI com validações de engenharia elétrica
  const workflowId = await ciOrchestrator.triggerCI(9001, 'feature/s9-energia');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  
  // Sync com compliance ANEEL
  await coworkSync.syncPRData(9001, {
    prNumber: 9001,
    agentMetadata: {
      segment: 'energia',
      powerTransmission: {
        type: 'High Voltage',
        voltage: '765 kV',
        length: '250 km',
        capacity: '3000 MVA',
      },
      substations: {
        primary: {
          type: 'Step-down',
          voltage: ['765 kV', '345 kV', '138 kV'],
        },
        secondary: {
          type: 'Step-up',
          voltage: ['345 kV', '138 kV'],
        },
      },
      regulatoryCompliance: {
        aneelApproval: true,
        rapStatus: 'Approved',
        auctionFramework: 'ACT 2024',
      },
      reliability: {
        expectedDowntime: '< 8 hours/year',
        redundancy: 'N+1',
      },
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## S10: Barragens — E2E Test Pattern (Novo)

### Padrão de Validação PNSB

```typescript
test('E2E S10: Barragem agent valida CFRD/CCR com ICOLD', async () => {
  const intent = await intentParser.parseCommitMessage(
    'create agent S10 barragem CFRD CCR vertedouro PNSB rejeitos'
  );
  
  expect(intent.params.segment).toBe('barragem');
  expect(intent.params.agentCode).toBe('s10');
  
  const code = await codeGenerator.generateCode(intent);
  expect(code).toContain('DamConstruction');
  expect(code).toContain('CFRD'); // Concrete Face Rockfill Dam
  expect(code).toContain('SlopeAnalysis');
  expect(code).toContain('SpillwayDesign');
  
  // CI com análises geotécnicas
  const workflowId = await ciOrchestrator.triggerCI(10001, 'feature/s10-barragem');
  await new Promise(resolve => setTimeout(resolve, 150));
  
  const status = await ciOrchestrator.getBuildStatus(workflowId);
  expect(status?.passed).toBe(true);
  
  // Sync com compliance PNSB/ICOLD
  await coworkSync.syncPRData(10001, {
    prNumber: 10001,
    agentMetadata: {
      segment: 'barragem',
      damType: 'CFRD',
      structure: {
        height: '120m',
        crestLength: '450m',
        crestElevation: '850 MASL',
        foundation: 'Gneiss Bedrock',
      },
      spillway: {
        type: 'Ogee Crest',
        capacity: '8000 m³/s',
        gates: 4,
      },
      tailingsFacility: {
        type: 'TSF',
        capacity: '250M tons',
        containment: 'Lined',
      },
      geotechnicalAnalysis: {
        foundationSlope: '1:0.8',
        upstreamSlope: '1:1.5',
        downstreamSlope: '1:2.0',
        seepageControl: 'Grout curtain',
      },
      regulatoryCompliance: {
        pnsb: 'Registered',
        icold: 'CBDB Listed',
        safetyClass: 'High Risk',
        inspectionFrequency: 'Bi-annual',
      },
      monitoring: {
        piezometers: 24,
        displacementSensors: 12,
        seismicMonitoring: true,
      },
    },
  });
  
  expect(await coworkSync.verifyConsistency()).toBe(true);
});
```

---

## Test Execution Checklist

Para rodar todos os testes de segmentos:

```bash
# Rodar todos
npm test -- tests/integration/e2e.test.ts

# Rodar apenas S1-S4 (infraestrutura)
npm test -- tests/integration/e2e.test.ts -t "S[1-4]"

# Rodar apenas S6-S10 (novos segmentos)
npm test -- tests/integration/e2e.test.ts -t "S[6-9]|S10"

# Rodar apenas S8 (saneamento - prioridade AySA)
npm test -- tests/integration/e2e.test.ts -t "S8"

# Com coverage
npm test -- tests/integration/e2e.test.ts --coverage
```

---

## Métricas Esperadas por Segmento

| Segmento | Tests | Coverage | Duration |
|----------|-------|----------|----------|
| S1 Rodovia | 1 | 85% | ~150ms |
| S2 OAE | 1 | 85% | ~150ms |
| S3 Ferrovia | 1 | 85% | ~150ms |
| S4 Metrô | 1 | 85% | ~150ms |
| S6 Portos | 1 | 90% | ~150ms |
| S7 Aeroportos | 1 | 90% | ~150ms |
| S8 Saneamento | 1 | 95% | ~150ms |
| S9 Energia | 1 | 90% | ~150ms |
| S10 Barragens | 1 | 90% | ~150ms |
| **Total** | **9** | **88%** | **~1.35s** |

---

## Adição Futura de Testes

Para adicionar novo teste de segmento:

1. Copie template acima
2. Substitua segmento específico (S1-S10)
3. Ajuste intent patterns e validações
4. Adicione metadados específicos
5. Update README e INTEGRATION_GUIDE
6. Run: `npm test -- tests/integration/e2e.test.ts`

---

**Versão**: 1.0.0  
**Compatível com**: CLAUDE.md v4.2 (S1-S10)  
**Data**: 2026-07-31
