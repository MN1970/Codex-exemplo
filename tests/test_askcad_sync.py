#!/usr/bin/env python3
"""
Test suite for AskCAD sync integration.

Phase 3.4 - AskCAD Persona Sync
Part 5: Testing Suite

Comprehensive tests for metadata extraction, sync client, monitoring,
and rollback functionality.

Usage:
    pytest tests/test_askcad_sync.py -v
    pytest tests/test_askcad_sync.py::TestMetadataExtraction -v
"""

import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys

# Import modules to test
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from extract_agent_metadata import AgentMetadataExtractor, AgentMetadata
from askcad_sync_client import AskCADSyncClient, SyncResult, SyncStatus
from monitoring_askcad_sync import SyncMonitor, SyncEvent, Alert, AlertSeverity


# Test fixtures
@pytest.fixture
def temp_agents_dir():
    """Create temporary agents directory with sample files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents_dir = Path(tmpdir) / '.claude' / 'agents'
        agents_dir.mkdir(parents=True)

        # Create sample agent files
        agent1 = agents_dir / 'agente-infraestrutura.md'
        agent1.write_text("""---
agent_code: manta-03-s1
agent_name: agente-infraestrutura
tier: Sonnet
status: Operacional
segment: S1
title: Agente de Infraestrutura - Rodovias
aliases:
  - "agente-rodovias"
  - "s1-agent"
version: 1.0.0
last_updated: 2026-07-26T10:00:00Z
capabilities:
  - "Análise de projetos rodoviários"
  - "Dimensionamento de pavimentos"
keywords:
  - "rodovia"
  - "DNIT"
  - "pavimento"
rag_collections:
  - "rod:"
contact: "s1@mantaassociados.com"
---

# Agente de Infraestrutura - Rodovias (S1)

Especializado em projetos de rodovias, pavimentos e infraestrutura viária.

## Capabilities
- Análise de projetos rodoviários
- Dimensionamento de pavimentos
- Cálculos SICRO
""")

        agent2 = agents_dir / 'agente-saneamento.md'
        agent2.write_text("""---
agent_code: manta-03-s8
agent_name: agente-saneamento
tier: Sonnet
status: Operacional
segment: S8
title: Agente de Saneamento
version: 1.0.0
last_updated: 2026-07-26T10:00:00Z
rag_collections:
  - "san:"
---

# Agente de Saneamento (S8)

Especializado em projetos de saneamento e água.
""")

        yield agents_dir


@pytest.fixture
def temp_askcad_dir():
    """Create temporary AskCAD config directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        askcad_dir = Path(tmpdir) / '.askcad'
        askcad_dir.mkdir(parents=True)
        yield askcad_dir


class TestMetadataExtraction:
    """Tests for agent metadata extraction"""

    def test_extract_single_file(self, temp_agents_dir):
        """Test extracting metadata from a single file"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        assert len(agents) >= 1
        assert 'manta-03-s1' in agents

        metadata = agents['manta-03-s1']
        assert metadata.agent_name == 'agente-infraestrutura'
        assert metadata.tier == 'Sonnet'
        assert metadata.status == 'Operacional'
        assert metadata.segment == 'S1'

    def test_extract_multiple_files(self, temp_agents_dir):
        """Test extracting metadata from multiple files"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        assert len(agents) >= 2
        assert 'manta-03-s1' in agents
        assert 'manta-03-s8' in agents

    def test_extract_keywords(self, temp_agents_dir):
        """Test keyword extraction"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        s1_metadata = agents['manta-03-s1']
        assert any('rodovia' in kw.lower() for kw in s1_metadata.keywords)

    def test_extract_capabilities(self, temp_agents_dir):
        """Test capability extraction"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        s1_metadata = agents['manta-03-s1']
        assert len(s1_metadata.capabilities) > 0

    def test_validate_required_fields(self, temp_agents_dir):
        """Test validation of required fields"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all(strict=True)

        for code, metadata in agents.items():
            assert metadata.agent_code
            assert metadata.agent_name
            assert metadata.tier
            assert metadata.status

    def test_validation_report(self, temp_agents_dir):
        """Test validation report generation"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        valid, report = extractor.validate()
        assert report['agents_count'] >= 2
        assert 'errors' in report
        assert 'warnings' in report

    def test_export_to_json(self, temp_agents_dir):
        """Test exporting metadata to JSON"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        json_output = extractor.to_json()
        data = json.loads(json_output)

        assert isinstance(data, dict)
        assert 'manta-03-s1' in data
        assert data['manta-03-s1']['agent_name'] == 'agente-infraestrutura'

    def test_report_generation(self, temp_agents_dir):
        """Test extraction report generation"""
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        report = extractor.report()
        assert 'AGENT METADATA EXTRACTION REPORT' in report
        assert 'manta-03-s1' in report


class TestAskCADSyncClient:
    """Tests for AskCAD sync client"""

    @pytest.fixture
    def sync_client(self, temp_askcad_dir):
        """Create sync client with temp directory"""
        return AskCADSyncClient(
            api_key='sk-test-key',
            api_url='https://api.test.askcad.com',
            version_history_file=str(temp_askcad_dir / 'version_history.json')
        )

    def test_normalize_to_persona(self, sync_client):
        """Test metadata normalization"""
        metadata = {
            'agent_code': 'manta-03-s1',
            'agent_name': 'agente-infraestrutura',
            'title': 'Agente de Infraestrutura',
            'tier': 'Sonnet',
            'status': 'Operacional',
            'description': 'Test description',
            'capabilities': ['cap1', 'cap2']
        }

        persona = sync_client._normalize_to_persona(metadata)

        assert persona['id'] == 'manta-03-s1'
        assert persona['name'] == 'agente-infraestrutura'
        assert persona['tier'] == 'Sonnet'
        assert 'metadata' in persona

    def test_calculate_hash(self, sync_client):
        """Test content hash calculation"""
        payload = {'key': 'value', 'nested': {'field': 'data'}}

        hash1 = sync_client._calculate_hash(payload)
        hash2 = sync_client._calculate_hash(payload)

        # Same payload should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_detect_changes_new_persona(self, sync_client):
        """Test change detection for new persona"""
        payload = {'name': 'test'}

        changes, prev = sync_client._detect_changes(
            'manta-new',
            'newhash123',
            payload
        )

        assert changes.get('type') == 'new_persona'
        assert prev is None

    @patch('askcad_sync_client.requests.Session.request')
    def test_sync_persona_dry_run(self, mock_request, sync_client):
        """Test dry-run sync"""
        metadata = {
            'agent_code': 'manta-03-s1',
            'agent_name': 'agente-infraestrutura',
            'tier': 'Sonnet',
            'status': 'Operacional',
            'version': '1.0.0'
        }

        result = sync_client.sync_persona(metadata, dry_run=True)

        assert result.agent_code == 'manta-03-s1'
        assert result.status == SyncStatus.PENDING
        assert 'dry run' in result.message.lower()

    @patch('askcad_sync_client.requests.Session.request')
    def test_sync_persona_success(self, mock_request, sync_client):
        """Test successful sync"""
        # Mock API responses
        mock_request.return_value = Mock(
            status_code=200,
            json=lambda: {'id': 'manta-03-s1'},
            raise_for_status=lambda: None
        )

        metadata = {
            'agent_code': 'manta-03-s1',
            'agent_name': 'agente-infraestrutura',
            'tier': 'Sonnet',
            'status': 'Operacional',
            'version': '1.0.0',
            'description': 'Test',
            'capabilities': [],
            'aliases': []
        }

        # Mock existing persona check to return 200
        mock_request.side_effect = [
            Mock(status_code=404, raise_for_status=lambda: None),  # GET (not found)
            Mock(status_code=201, json=lambda: {'id': 'manta-03-s1'}, raise_for_status=lambda: None),  # POST
            Mock(status_code=204, raise_for_status=lambda: None)   # PUT
        ]

        result = sync_client.sync_persona(metadata)

        assert result.status == SyncStatus.SUCCESS

    def test_version_history_persistence(self, sync_client, temp_askcad_dir):
        """Test version history is persisted"""
        from extract_agent_metadata import AgentMetadata

        metadata = AgentMetadata(
            agent_code='manta-03-s1',
            agent_name='test',
            title='Test',
            tier='Sonnet',
            status='Operacional',
            segment='S1',
            aliases=[],
            description='test',
            capabilities=[],
            rag_collections=[],
            input_formats=[],
            output_formats=[],
            keywords=[],
            version='1.0.0',
            last_updated=datetime.now().isoformat(),
            contact=None,
            sharepoint_folder=None,
            dependencies=[],
            metadata_source='test.md'
        )

        # Manually add to history
        sync_client._add_to_version_history(
            'manta-03-s1',
            '1.0.0',
            'hash123',
            {'test': 'change'},
            None,
            'Test change'
        )

        # Verify history was saved
        history = sync_client.get_version_history('manta-03-s1')
        assert len(history) >= 1
        assert history[0]['agent_code'] == 'manta-03-s1'


class TestMonitoring:
    """Tests for monitoring and alerting"""

    @pytest.fixture
    def monitor(self, temp_askcad_dir):
        """Create monitor with temp directory"""
        return SyncMonitor(
            db_path=str(temp_askcad_dir / 'sync_monitor.db'),
            audit_log_path=str(temp_askcad_dir / 'audit_trail.jsonl'),
            version_history_path=str(temp_askcad_dir / 'version_history.json')
        )

    def test_record_sync_event(self, monitor):
        """Test recording sync event"""
        event = SyncEvent(
            timestamp=datetime.now().isoformat(),
            agent_code='manta-03-s1',
            operation='sync',
            status='success',
            version='1.0.0',
            content_hash='hash123',
            message='Test sync',
            duration_ms=1500
        )

        audit_id = monitor.record_sync(event)
        assert audit_id
        assert len(audit_id) == 16  # SHA-256 truncated to 16 chars

    def test_check_health(self, monitor):
        """Test health check"""
        # Record some events
        for i in range(3):
            event = SyncEvent(
                timestamp=datetime.now().isoformat(),
                agent_code=f'manta-03-s{i}',
                operation='sync',
                status='success' if i < 2 else 'failed',
                version='1.0.0',
                content_hash=f'hash{i}',
                message='Test',
                duration_ms=1000
            )
            monitor.record_sync(event)

        metrics, alerts = monitor.check_health(time_window_hours=24)

        assert metrics.total_syncs == 3
        assert metrics.successful_syncs == 2
        assert metrics.failed_syncs == 1

    def test_health_alerts_generation(self, monitor):
        """Test alert generation for health issues"""
        # Record failures
        for _ in range(10):
            event = SyncEvent(
                timestamp=datetime.now().isoformat(),
                agent_code='manta-03-s1',
                operation='sync',
                status='failed',
                version='1.0.0',
                content_hash='hash123',
                message='Sync failed',
                duration_ms=500
            )
            monitor.record_sync(event)

        metrics, alerts = monitor.check_health()

        # Should generate alert for failures
        assert len(alerts) > 0
        assert any('failure' in a.title.lower() for a in alerts)

    def test_record_alert(self, monitor):
        """Test recording alerts"""
        alert = Alert(
            timestamp=datetime.now().isoformat(),
            severity=AlertSeverity.ERROR,
            agent_code='manta-03-s1',
            title='Test Alert',
            description='Test alert description',
            action_required=True
        )

        monitor.record_alert(alert)

        # Verify it's recorded
        conn = sqlite3.connect(monitor.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sync_alerts WHERE title = ?", ('Test Alert',))
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_sync_history_filtering(self, monitor):
        """Test filtering sync history"""
        # Record events for different agents
        for agent in ['manta-03-s1', 'manta-03-s2', 'manta-03-s1']:
            event = SyncEvent(
                timestamp=datetime.now().isoformat(),
                agent_code=agent,
                operation='sync',
                status='success',
                version='1.0.0',
                content_hash='hash123',
                message='Test',
                duration_ms=1000
            )
            monitor.record_sync(event)

        # Query for specific agent
        history = monitor.get_sync_history(agent_code='manta-03-s1')

        assert len(history) == 2
        assert all(h['agent_code'] == 'manta-03-s1' for h in history)

    def test_generate_report(self, monitor):
        """Test report generation"""
        # Record some events
        for i in range(5):
            event = SyncEvent(
                timestamp=datetime.now().isoformat(),
                agent_code=f'manta-03-s{i}',
                operation='sync',
                status='success',
                version='1.0.0',
                content_hash=f'hash{i}',
                message='Test',
                duration_ms=1000
            )
            monitor.record_sync(event)

        report = monitor.generate_report(hours=24)

        assert 'ASKCAD SYNC MONITORING REPORT' in report
        assert 'HEALTH METRICS' in report
        assert 'Total Syncs:' in report

    def test_export_metrics(self, monitor, temp_askcad_dir):
        """Test metrics export"""
        output_file = temp_askcad_dir / 'metrics.json'

        monitor.export_metrics(str(output_file))

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert 'timestamp' in data
        assert 'metrics' in data
        assert 'alerts' in data


class TestIntegration:
    """Integration tests"""

    def test_extract_and_sync_workflow(self, temp_agents_dir, temp_askcad_dir):
        """Test complete extract → sync workflow"""
        # Extract metadata
        extractor = AgentMetadataExtractor(str(temp_agents_dir))
        agents = extractor.extract_all()

        assert len(agents) >= 1

        # Create sync client
        client = AskCADSyncClient(
            api_key='sk-test',
            api_url='https://api.test.askcad.com',
            version_history_file=str(temp_askcad_dir / 'version_history.json')
        )

        # Normalize first agent
        first_agent = list(agents.values())[0]
        from dataclasses import asdict
        metadata_dict = asdict(first_agent)

        # Dry-run sync
        result = client.sync_persona(metadata_dict, dry_run=True)

        assert result.agent_code
        assert result.status == SyncStatus.PENDING

    def test_end_to_end_monitoring(self, temp_askcad_dir):
        """Test end-to-end monitoring workflow"""
        monitor = SyncMonitor(
            db_path=str(temp_askcad_dir / 'sync_monitor.db'),
            audit_log_path=str(temp_askcad_dir / 'audit_trail.jsonl')
        )

        # Record multiple events
        for i in range(15):
            event = SyncEvent(
                timestamp=(datetime.now() - timedelta(hours=i)).isoformat(),
                agent_code=f'manta-03-s{i%10}',
                operation='sync',
                status='success' if i % 3 != 0 else 'failed',
                version=f'1.{i}.0',
                content_hash=f'hash{i}',
                message='Test event',
                duration_ms=1000 + i * 100
            )
            monitor.record_sync(event)

        # Check health
        metrics, alerts = monitor.check_health()

        assert metrics.total_syncs == 15
        assert metrics.failed_syncs > 0

        # Get report
        report = monitor.generate_report()
        assert 'HEALTH METRICS' in report

        # Export metrics
        export_file = temp_askcad_dir / 'export.json'
        monitor.export_metrics(str(export_file))
        assert export_file.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
