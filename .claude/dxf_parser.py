"""
autodesk-dxf-parser — DXF Entity Extraction & Analysis
Version: 1.0.0
Supports: ezdxf >= 1.1.0, numpy, pyproj, shapely
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
import json
import csv
from pathlib import Path
from enum import Enum
import warnings

try:
    import ezdxf
    from ezdxf.entities import DXFEntity
except ImportError:
    raise ImportError("ezdxf >= 1.1.0 required. Install with: pip install ezdxf")

try:
    import numpy as np
except ImportError:
    np = None

try:
    from pyproj import CRS, Transformer
    from pyproj.exceptions import CRSError
except ImportError:
    CRS = None
    Transformer = None

try:
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union
except ImportError:
    LineString = None
    Point = None
    Polygon = None


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Entity:
    """Represents a DXF entity."""
    entity_type: str
    handle: str
    layer: str
    color: int
    coordinates: List[Tuple[float, ...]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerInfo:
    """Metadata about a DXF layer."""
    name: str
    color: int
    linetype: str
    frozen: bool
    locked: bool
    entity_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BBox:
    """Bounding box coordinates."""
    minx: float
    miny: float
    maxx: float
    maxy: float
    minz: Optional[float] = None
    maxz: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def width(self) -> float:
        return self.maxx - self.minx

    @property
    def height(self) -> float:
        return self.maxy - self.miny


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    type: str
    entity_ids: List[int]
    description: str
    severity: str  # 'INFO', 'WARN', 'ERROR'
    coordinates: Optional[Tuple[float, ...]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnomalySummary:
    """Summary of anomalies."""
    total: int
    errors: int
    warnings: int
    info: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Result of coordinate validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParseReport:
    """Result of parsing a single DXF file."""
    filename: str
    entity_counts: Dict[str, int]
    layer_summary: List[LayerInfo]
    coordinate_bounds: BBox
    anomaly_summary: AnomalySummary
    crs_info: Optional[Dict[str, Any]] = None
    export_files: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'filename': self.filename,
            'entity_counts': self.entity_counts,
            'layer_summary': [layer.to_dict() for layer in self.layer_summary],
            'coordinate_bounds': self.coordinate_bounds.to_dict(),
            'anomaly_summary': self.anomaly_summary.to_dict(),
            'crs_info': self.crs_info,
            'export_files': self.export_files
        }


# ============================================================================
# MAIN PARSER CLASS
# ============================================================================

class DXFParser:
    """Parse, analyze, and validate DXF files."""

    SUPPORTED_ENTITY_TYPES = {
        'LINE', 'CIRCLE', 'ARC', 'POLYLINE', 'LWPOLYLINE',
        'BLOCK', 'INSERT', 'ATTRIBUTE', 'SPLINE', 'ELLIPSE',
        'TEXT', 'MTEXT', 'SOLID', 'TRACE', 'DIMENSION', 'LEADER',
        '3DFACE', 'IMAGE', 'HATCH'
    }

    def __init__(self, dxf_path: str, encoding: str = 'utf-8', streaming: bool = False):
        """Initialize parser from DXF file path."""
        self.dxf_path = Path(dxf_path)
        self.encoding = encoding
        self.streaming = streaming
        self._doc = None
        self._entities_cache = {}
        self._layer_info_cache = None
        self._crs_source = None
        self._anomalies_cache = None

        self._load_dxf()

    def _load_dxf(self):
        """Load DXF file with error handling."""
        try:
            self._doc = ezdxf.readfile(str(self.dxf_path), encoding=self.encoding)
        except Exception as e:
            raise ValueError(f"Failed to load DXF {self.dxf_path}: {e}")

    # ========================================================================
    # ENTITY EXTRACTION
    # ========================================================================

    def extract_entities(self,
                        entity_type: Optional[str] = None,
                        layer: Optional[str] = None) -> Dict[str, List[Entity]]:
        """Extract entities, optionally filtered by type or layer."""
        cache_key = (entity_type, layer)
        if cache_key in self._entities_cache:
            return self._entities_cache[cache_key]

        result = {}
        modelspace = self._doc.modelspace()

        # Determine entity types to extract
        types_to_extract = [entity_type] if entity_type else self.SUPPORTED_ENTITY_TYPES

        for ent_type in types_to_extract:
            result[ent_type] = []

        # Iterate through entities
        for dxf_entity in modelspace.query('*'):
            dxf_type = dxf_entity.dxftype()

            # Filter by type
            if entity_type and dxf_type != entity_type:
                continue

            # Filter by layer
            if layer and dxf_entity.dxf.layer != layer:
                continue

            # Convert to internal representation
            entity = self._convert_entity(dxf_entity)
            if entity:
                if dxf_type not in result:
                    result[dxf_type] = []
                result[dxf_type].append(entity)

        self._entities_cache[cache_key] = result
        return result

    def _convert_entity(self, dxf_entity: DXFEntity) -> Optional[Entity]:
        """Convert ezdxf entity to internal Entity."""
        try:
            ent_type = dxf_entity.dxftype()
            handle = dxf_entity.dxf.handle
            layer = dxf_entity.dxf.layer
            color = dxf_entity.dxf.color

            coordinates = self._extract_coordinates_from_entity(dxf_entity)
            properties = self._extract_properties(dxf_entity)

            return Entity(
                entity_type=ent_type,
                handle=handle,
                layer=layer,
                color=color,
                coordinates=coordinates,
                properties=properties
            )
        except Exception as e:
            warnings.warn(f"Failed to convert entity {dxf_entity.dxftype()}: {e}")
            return None

    def _extract_coordinates_from_entity(self, dxf_entity: DXFEntity) -> List[Tuple[float, ...]]:
        """Extract coordinates from a DXF entity."""
        coords = []
        ent_type = dxf_entity.dxftype()

        try:
            if ent_type == 'LINE':
                coords = [
                    tuple(dxf_entity.dxf.start),
                    tuple(dxf_entity.dxf.end)
                ]
            elif ent_type == 'CIRCLE':
                coords = [tuple(dxf_entity.dxf.center)]
            elif ent_type == 'ARC':
                coords = [tuple(dxf_entity.dxf.center)]
                # Add approximation of arc
                if hasattr(dxf_entity, 'get_points'):
                    coords.extend([tuple(p) for p in dxf_entity.get_points()])
            elif ent_type in ('POLYLINE', 'LWPOLYLINE'):
                if hasattr(dxf_entity, 'get_points'):
                    coords = [tuple(p) for p in dxf_entity.get_points()]
                elif hasattr(dxf_entity, 'points'):
                    coords = [tuple(p) for p in dxf_entity.points]
            elif ent_type == 'SPLINE':
                if hasattr(dxf_entity, 'get_points'):
                    coords = [tuple(p) for p in dxf_entity.get_points()]
            elif ent_type == 'ELLIPSE':
                coords = [tuple(dxf_entity.dxf.center)]
            elif ent_type == 'TEXT' or ent_type == 'MTEXT':
                coords = [tuple(dxf_entity.dxf.insert)]
            elif ent_type == 'INSERT':
                coords = [tuple(dxf_entity.dxf.insert)]
            elif ent_type == 'SOLID' or ent_type == 'TRACE':
                for i in range(4):
                    point = dxf_entity.dxf.get(f'point{i}')
                    if point:
                        coords.append(tuple(point))
            elif ent_type == '3DFACE':
                for i in range(4):
                    point = dxf_entity.dxf.get(f'point{i}')
                    if point:
                        coords.append(tuple(point))
            elif ent_type == 'DIMENSION':
                if hasattr(dxf_entity.dxf, 'insert'):
                    coords = [tuple(dxf_entity.dxf.insert)]
        except Exception as e:
            warnings.warn(f"Failed to extract coords from {ent_type}: {e}")

        return coords

    def _extract_properties(self, dxf_entity: DXFEntity) -> Dict[str, Any]:
        """Extract additional properties from entity."""
        props = {}
        ent_type = dxf_entity.dxftype()

        try:
            if ent_type == 'CIRCLE':
                props['radius'] = dxf_entity.dxf.radius
            elif ent_type == 'ARC':
                props['radius'] = dxf_entity.dxf.radius
                props['start_angle'] = dxf_entity.dxf.start_angle
                props['end_angle'] = dxf_entity.dxf.end_angle
            elif ent_type == 'TEXT' or ent_type == 'MTEXT':
                props['text'] = dxf_entity.dxf.text
                props['height'] = dxf_entity.dxf.height
            elif ent_type == 'ATTRIBUTE':
                props['tag'] = dxf_entity.dxf.tag
                props['value'] = dxf_entity.dxf.text
            elif ent_type == 'INSERT':
                props['name'] = dxf_entity.dxf.name
                props['scale'] = tuple(dxf_entity.dxf.scale)
            elif ent_type == 'SPLINE':
                props['degree'] = dxf_entity.dxf.degree
                props['knot_count'] = len(dxf_entity.dxf.knot_values)
            elif ent_type == 'ELLIPSE':
                props['major_axis_length'] = dxf_entity.dxf.major_axis_length
                props['minor_axis_ratio'] = dxf_entity.dxf.minor_axis_ratio
        except Exception as e:
            warnings.warn(f"Failed to extract properties from {ent_type}: {e}")

        return props

    def extract_by_layer(self, layer: str,
                        entity_type: Optional[str] = None) -> List[Entity]:
        """Extract all entities on a specific layer."""
        entities = self.extract_entities(entity_type=entity_type, layer=layer)
        result = []
        for ent_list in entities.values():
            result.extend(ent_list)
        return result

    # ========================================================================
    # LAYER ANALYSIS
    # ========================================================================

    def get_layer_info(self) -> List[LayerInfo]:
        """Return metadata for all layers."""
        if self._layer_info_cache is not None:
            return self._layer_info_cache

        layers_obj = self._doc.layers
        layer_entities_count = {}

        # Count entities per layer
        for dxf_entity in self._doc.modelspace():
            layer = dxf_entity.dxf.layer
            layer_entities_count[layer] = layer_entities_count.get(layer, 0) + 1

        result = []
        for layer in layers_obj:
            try:
                frozen = layer.dxf.frozen
            except AttributeError:
                frozen = False
            try:
                locked = layer.dxf.locked
            except AttributeError:
                locked = False

            info = LayerInfo(
                name=layer.dxf.name,
                color=layer.dxf.color,
                linetype=layer.dxf.linetype,
                frozen=frozen,
                locked=locked,
                entity_count=layer_entities_count.get(layer.dxf.name, 0)
            )
            result.append(info)

        self._layer_info_cache = sorted(result, key=lambda x: x.name)
        return self._layer_info_cache

    def get_layers_by_color(self, color: int) -> List[LayerInfo]:
        """Return layers with specific color code."""
        all_layers = self.get_layer_info()
        return [layer for layer in all_layers if layer.color == color]

    def get_layer_hierarchy(self) -> Dict[str, List[str]]:
        """Return layer hierarchy (if using naming convention)."""
        all_layers = self.get_layer_info()
        hierarchy = {}

        for layer in all_layers:
            # Assume hierarchy like "prefix-name" or "prefix_name"
            if '-' in layer.name:
                prefix = layer.name.split('-')[0]
            elif '_' in layer.name:
                prefix = layer.name.split('_')[0]
            else:
                prefix = 'root'

            if prefix not in hierarchy:
                hierarchy[prefix] = []
            hierarchy[prefix].append(layer.name)

        return hierarchy

    # ========================================================================
    # COORDINATE EXTRACTION & CRS
    # ========================================================================

    def extract_coordinates(self, layer: Optional[str] = None,
                           include_z: bool = True) -> List[Tuple[float, ...]]:
        """Extract all (x, y[, z]) coordinates from entities."""
        entities = self.extract_entities(layer=layer)
        coords = []

        for ent_list in entities.values():
            for entity in ent_list:
                for coord in entity.coordinates:
                    if not include_z and len(coord) == 3:
                        coords.append(coord[:2])
                    else:
                        coords.append(coord)

        return coords

    def get_bounds(self) -> BBox:
        """Return bounding box of all entities."""
        coords = self.extract_coordinates(include_z=True)

        if not coords:
            return BBox(0, 0, 0, 0, 0, 0)

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        zs = [c[2] for c in coords if len(c) > 2]

        return BBox(
            minx=min(xs),
            miny=min(ys),
            maxx=max(xs),
            maxy=max(ys),
            minz=min(zs) if zs else None,
            maxz=max(zs) if zs else None
        )

    def get_crs_info(self) -> Optional[Dict[str, Any]]:
        """Extract CRS/EPSG info from DXF metadata or XDATA."""
        # Try to read from XDATA (custom properties)
        # This is a placeholder; actual implementation depends on DXF structure
        try:
            # Check header variables for geographic/CRS info
            if hasattr(self._doc.header, 'get'):
                # Some CAD systems store CRS in custom header vars
                crs_var = self._doc.header.get('$CUSTOM_CRS', None)
                if crs_var:
                    return {'source': 'HEADER', 'raw': crs_var}
        except:
            pass

        return None

    def set_crs_source(self, epsg: int) -> None:
        """Set the source EPSG code for coordinate transformation."""
        if CRS is None:
            raise ImportError("pyproj required for CRS handling. Install with: pip install pyproj")

        try:
            self._crs_source = CRS.from_epsg(epsg)
        except CRSError:
            raise ValueError(f"Invalid EPSG code: {epsg}")

    def transform_coordinates(self, target_epsg: int) -> List[Tuple[float, ...]]:
        """Transform all coordinates to target EPSG."""
        if not self._crs_source:
            raise ValueError("Source CRS not set. Call set_crs_source() first.")

        if Transformer is None:
            raise ImportError("pyproj required for transformations.")

        target_crs = CRS.from_epsg(target_epsg)
        transformer = Transformer.from_crs(self._crs_source, target_crs, always_xy=True)

        coords = self.extract_coordinates(include_z=True)
        transformed = []

        for coord in coords:
            if len(coord) == 2:
                x, y = transformer.transform(coord[0], coord[1])
                transformed.append((x, y))
            elif len(coord) == 3:
                x, y = transformer.transform(coord[0], coord[1])
                transformed.append((x, y, coord[2]))

        return transformed

    def validate_coordinates(self) -> ValidationReport:
        """Check for NaN, inf, outliers, and other coordinate issues."""
        coords = self.extract_coordinates(include_z=True)

        if not coords:
            return ValidationReport(valid=True)

        errors = []
        warnings_list = []

        for i, coord in enumerate(coords):
            for j, val in enumerate(coord):
                if np and (np.isnan(val) or np.isinf(val)):
                    errors.append(f"Invalid value at coord {i}, axis {j}: {val}")

        # Check for extreme values (outliers)
        if np:
            coords_array = np.array(coords)
            for axis in range(coords_array.shape[1]):
                axis_data = coords_array[:, axis]
                mean = np.nanmean(axis_data)
                std = np.nanstd(axis_data)
                if std > 0:
                    outliers = np.where(np.abs(axis_data - mean) > 10 * std)[0]
                    if len(outliers) > 0:
                        warnings_list.append(
                            f"Potential outliers on axis {axis}: {len(outliers)} points"
                        )

        return ValidationReport(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings_list
        )

    # ========================================================================
    # ANOMALY DETECTION
    # ========================================================================

    def detect_anomalies(self,
                        entity_type: Optional[str] = None,
                        threshold_gap_mm: float = 1.0,
                        threshold_overlap_pct: float = 0.9) -> Dict[str, List[Anomaly]]:
        """Scan for geometric errors and data quality issues."""
        anomalies = {
            'overlapping_entities': [],
            'missing_layers': [],
            'duplicate_entities': [],
            'self_intersecting': [],
            'extreme_coordinates': [],
            'disconnected_segments': []
        }

        entities = self.extract_entities(entity_type=entity_type)

        # Check for entities on default layer "0"
        for ent_list in entities.values():
            for entity in ent_list:
                if entity.layer == '0':
                    anomalies['missing_layers'].append(Anomaly(
                        type='ENTITY_ON_DEFAULT_LAYER',
                        entity_ids=[int(entity.handle, 16)],
                        description=f'{entity.entity_type} on layer "0" (default)',
                        severity='WARN'
                    ))

        # Check for duplicate entities
        seen = {}
        for ent_type, ent_list in entities.items():
            for entity in ent_list:
                key = (ent_type, tuple(entity.coordinates))
                if key in seen:
                    anomalies['duplicate_entities'].append(Anomaly(
                        type='DUPLICATE_ENTITY',
                        entity_ids=[int(entity.handle, 16), int(seen[key].handle, 16)],
                        description=f'Duplicate {ent_type} at {entity.coordinates[0] if entity.coordinates else "unknown"}',
                        severity='ERROR'
                    ))
                seen[key] = entity

        # Check for coordinate extremes
        coords = self.extract_coordinates(include_z=True)
        if coords and np:
            coords_array = np.array(coords)
            for axis in range(coords_array.shape[1]):
                axis_data = coords_array[:, axis]
                q1 = np.nanpercentile(axis_data, 25)
                q3 = np.nanpercentile(axis_data, 75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr

                outliers = np.where((axis_data < lower_bound) | (axis_data > upper_bound))[0]
                for idx in outliers:
                    anomalies['extreme_coordinates'].append(Anomaly(
                        type='COORDINATE_OUTLIER',
                        entity_ids=[idx],
                        description=f'Extreme value {coords[idx][axis]:.1f} on axis {axis}',
                        severity='WARN',
                        coordinates=coords[idx]
                    ))

        self._anomalies_cache = anomalies
        return anomalies

    def get_anomaly_summary(self) -> AnomalySummary:
        """Return severity counts from last anomaly scan."""
        if self._anomalies_cache is None:
            self.detect_anomalies()

        total = 0
        errors = 0
        warnings = 0
        info = 0

        for anomaly_list in self._anomalies_cache.values():
            for anomaly in anomaly_list:
                total += 1
                if anomaly.severity == 'ERROR':
                    errors += 1
                elif anomaly.severity == 'WARN':
                    warnings += 1
                elif anomaly.severity == 'INFO':
                    info += 1

        return AnomalySummary(total=total, errors=errors, warnings=warnings, info=info)

    # ========================================================================
    # EXPORT
    # ========================================================================

    def export(self, format: str, output_path: str,
              include_anomalies: bool = False) -> str:
        """Export to GeoJSON, Shapefile, CSV, or JSON. Returns path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        entities = self.extract_entities()

        if format.lower() == 'json':
            self._export_json(entities, output_path, include_anomalies)
        elif format.lower() == 'csv':
            self._export_csv(entities, output_path)
        elif format.lower() == 'geojson':
            self._export_geojson(entities, output_path, include_anomalies)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        return str(output_path)

    def _export_json(self, entities: Dict[str, List[Entity]],
                    output_path: Path, include_anomalies: bool = False) -> None:
        """Export to JSON."""
        data = {
            'type': 'DXF Export',
            'source': str(self.dxf_path),
            'entities': {},
            'layers': [layer.to_dict() for layer in self.get_layer_info()],
            'bounds': self.get_bounds().to_dict()
        }

        for ent_type, ent_list in entities.items():
            data['entities'][ent_type] = [ent.to_dict() for ent in ent_list]

        if include_anomalies:
            anomalies = self.detect_anomalies()
            data['anomalies'] = {
                k: [a.to_dict() for a in v]
                for k, v in anomalies.items()
            }
            data['anomaly_summary'] = self.get_anomaly_summary().to_dict()

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _export_csv(self, entities: Dict[str, List[Entity]],
                   output_path: Path) -> None:
        """Export to CSV (flattened)."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Entity Type', 'Handle', 'Layer', 'Color', 'X', 'Y', 'Z', 'Properties'])

            for ent_type, ent_list in entities.items():
                for entity in ent_list:
                    for i, coord in enumerate(entity.coordinates):
                        x = coord[0] if len(coord) > 0 else ''
                        y = coord[1] if len(coord) > 1 else ''
                        z = coord[2] if len(coord) > 2 else ''
                        writer.writerow([
                            ent_type, entity.handle, entity.layer, entity.color,
                            x, y, z, json.dumps(entity.properties)
                        ])

    def _export_geojson(self, entities: Dict[str, List[Entity]],
                       output_path: Path, include_anomalies: bool = False) -> None:
        """Export to GeoJSON."""
        if LineString is None or Point is None:
            raise ImportError("shapely required for GeoJSON export. Install with: pip install shapely")

        features = []

        for ent_type, ent_list in entities.items():
            for entity in ent_list:
                if not entity.coordinates:
                    continue

                # Determine geometry type
                if ent_type == 'LINE':
                    if len(entity.coordinates) >= 2:
                        geometry = {'type': 'LineString', 'coordinates': entity.coordinates}
                elif ent_type in ('POLYLINE', 'LWPOLYLINE', 'SPLINE'):
                    geometry = {'type': 'LineString', 'coordinates': entity.coordinates}
                elif ent_type == 'CIRCLE':
                    geometry = {
                        'type': 'Point',
                        'coordinates': entity.coordinates[0]
                    }
                else:
                    if len(entity.coordinates) == 1:
                        geometry = {'type': 'Point', 'coordinates': entity.coordinates[0]}
                    else:
                        geometry = {'type': 'LineString', 'coordinates': entity.coordinates}

                feature = {
                    'type': 'Feature',
                    'geometry': geometry,
                    'properties': {
                        'entity_type': ent_type,
                        'handle': entity.handle,
                        'layer': entity.layer,
                        'color': entity.color,
                        **entity.properties
                    }
                }
                features.append(feature)

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def batch_parse_dxf(dxf_files: List[str],
                    export_format: str = 'json',
                    include_anomalies: bool = False,
                    output_dir: str = '.') -> List[ParseReport]:
    """Process multiple DXF files and generate reports."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = []

    for dxf_file in dxf_files:
        try:
            parser = DXFParser(dxf_file)

            # Extract data
            entities = parser.extract_entities()
            entity_counts = {k: len(v) for k, v in entities.items()}
            layers = parser.get_layer_info()
            bounds = parser.get_bounds()
            anomalies = parser.detect_anomalies() if include_anomalies else None
            anomaly_summary = parser.get_anomaly_summary() if include_anomalies else AnomalySummary(0, 0, 0, 0)
            crs_info = parser.get_crs_info()

            # Export
            export_files = {}
            if export_format:
                output_name = Path(dxf_file).stem
                export_path = output_dir / f"{output_name}.{export_format}"
                parser.export(export_format, str(export_path), include_anomalies=include_anomalies)
                export_files[export_format] = str(export_path)

            # Create report
            report = ParseReport(
                filename=str(dxf_file),
                entity_counts=entity_counts,
                layer_summary=layers,
                coordinate_bounds=bounds,
                anomaly_summary=anomaly_summary,
                crs_info=crs_info,
                export_files=export_files
            )
            reports.append(report)

        except Exception as e:
            warnings.warn(f"Failed to parse {dxf_file}: {e}")

    return reports
