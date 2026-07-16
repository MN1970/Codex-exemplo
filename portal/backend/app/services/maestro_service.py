"""
Maestro routing service — intelligent agent dispatcher
Routes user queries to appropriate agents based on keywords and patterns
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from app.models.maestro import (
    RoutingIntent,
    AgentProfile,
    RuleMatch,
    RoutingConfidence,
)

logger = logging.getLogger(__name__)


@dataclass
class RoutingRule:
    """Single routing rule for agent detection"""
    agent_code: str
    agent_id: str
    agent_name: str
    keywords: List[str]
    pattern: str
    eixo: str
    tier: str
    status: str = "Operacional"
    service_url: Optional[str] = None
    segment: Optional[str] = None
    aliases: Optional[List[str]] = None
    description: Optional[str] = None


class MaestroRouter:
    """
    Maestro Router — central agent dispatcher for Manta Maestro v4.2
    Detects user intent and routes to appropriate agent (horizontal or vertical)
    """

    # Routing rules for all 20 agents
    ROUTING_RULES: Dict[str, RoutingRule] = {
        # === HORIZONTAL AGENTS (11) ===
        "maestro": RoutingRule(
            agent_code="Manta 00",
            agent_id="manta-00",
            agent_name="maestro (router)",
            keywords=["maestro", "router", "routing", "qual agente", "qual serviço", "direcionamento"],
            pattern=r"(maestro|router|roteamento|qual\s+agente|qual\s+serviço|me\s+direcione)",
            eixo="Horizontal",
            tier="Haiku→Sonnet",
            aliases=["maestro", "manta-router"],
        ),
        "claims": RoutingRule(
            agent_code="Manta 01",
            agent_id="manta-01",
            agent_name="claims",
            keywords=["claims", "sinistro", "indenização", "reclamação", "disputa", "litígio"],
            pattern=r"(claims?|sinistro|indenização|reclamação|disputa|litígio)",
            eixo="Horizontal",
            tier="Opus",
            aliases=["02-C", "manta-claims"],
        ),
        "contratual": RoutingRule(
            agent_code="Manta 02",
            agent_id="manta-02",
            agent_name="contratual",
            keywords=["contrato", "cláusula", "condição", "obrigação", "direito", "dever"],
            pattern=r"(contrat|cláusul|condição|obrigação|direito|dever)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-02", "contratual"],
        ),
        "imobiliario": RoutingRule(
            agent_code="Manta 04",
            agent_id="manta-04",
            agent_name="imobiliário",
            keywords=["imóvel", "propriedade", "terreno", "direito real", "registro", "hipoteca"],
            pattern=r"(imóvel|propriedade|terreno|direito\s+real|registro|hipoteca)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-04"],
        ),
        "orcamento": RoutingRule(
            agent_code="Manta 05",
            agent_id="manta-05",
            agent_name="orçamento",
            keywords=["orçamento", "preço", "custo", "valor", "estimativa", "cotação"],
            pattern=r"(orçamento|preço|custo|valor|estimativa|cotação)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-05"],
        ),
        "modelagem": RoutingRule(
            agent_code="Manta 06",
            agent_id="manta-06",
            agent_name="modelagem",
            keywords=["modelo", "simulação", "análise", "cenário", "previsão", "matemático"],
            pattern=r"(modelagem|modelo|simulação|análise|cenário|previsão|matemático)",
            eixo="Horizontal",
            tier="Sonnet/Opus",
            aliases=["manta-06"],
        ),
        "cronograma": RoutingRule(
            agent_code="Manta 07",
            agent_id="manta-07",
            agent_name="cronograma",
            keywords=["cronograma", "prazo", "agenda", "marco", "fase", "etapa"],
            pattern=r"(cronograma|prazo|agenda|marco|etapa|fase)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-07"],
        ),
        "bd": RoutingRule(
            agent_code="Manta 13",
            agent_id="manta-13",
            agent_name="business-dev",
            keywords=["negócio", "oportunidade", "parceria", "cliente", "mercado", "viabilidade"],
            pattern=r"(negócio|oportunidade|parceria|cliente|mercado|viabilidade|business)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-13", "business-dev"],
        ),
        "apresentacoes": RoutingRule(
            agent_code="Manta 14",
            agent_id="manta-14",
            agent_name="apresentações",
            keywords=["apresentação", "slides", "pptx", "deck", "visual", "pitch"],
            pattern=r"(apresentação|slides?|pptx|deck|visual|pitch)",
            eixo="Horizontal",
            tier="Sonnet",
            aliases=["manta-14-pptx"],
        ),
        "advisory": RoutingRule(
            agent_code="Manta 15",
            agent_id="manta-15",
            agent_name="advisory",
            keywords=["consultoria", "conselho", "recomendação", "estratégia", "parecer", "opinião"],
            pattern=r"(consultoria|conselho|recomendação|estratégia|parecer|opinião|advisory)",
            eixo="Horizontal",
            tier="Sonnet/Opus",
            aliases=["manta-15", "advisory"],
        ),
        "arquiteto_ia": RoutingRule(
            agent_code="Manta 16",
            agent_id="manta-16",
            agent_name="arquiteto-ia",
            keywords=["arquitetura", "design", "padrão", "framework", "estrutura", "implementação"],
            pattern=r"(arquitetura|design|padrão|framework|estrutura|implementação)",
            eixo="Horizontal",
            tier="Opus",
            aliases=["manta-15-arq"],
        ),

        # === VERTICAL AGENTS — INFRASTRUCTURE (S1-S5) ===
        "infraestrutura_s1": RoutingRule(
            agent_code="Manta 03-S1",
            agent_id="manta-03-s1",
            agent_name="agente-infraestrutura (S1)",
            keywords=["rodovia", "pavimento", "CBUQ", "BGS", "terraplenagem", "SICRO", "DNIT"],
            pattern=r"(rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT|asfalto|base)",
            eixo="Vertical",
            segment="Rodovias",
            tier="Sonnet",
            aliases=["agente-s1"],
        ),
        "infraestrutura_s2": RoutingRule(
            agent_code="Manta 03-S2",
            agent_id="manta-03-s2",
            agent_name="agente-infraestrutura (S2)",
            keywords=["ponte", "viaduto", "OAE", "NBR 7187", "túnel", "estrutura"],
            pattern=r"(ponte|viaduto|OAE|NBR\s*7187|túnel\s+rod|estrutura\s+especial)",
            eixo="Vertical",
            segment="OAE (pontes, viadutos)",
            tier="Sonnet",
            aliases=["agente-s2"],
        ),
        "infraestrutura_s3": RoutingRule(
            agent_code="Manta 03-S3",
            agent_id="manta-03-s3",
            agent_name="agente-infraestrutura (S3)",
            keywords=["ferrovia", "trilho", "AMV", "dormente", "via permanente", "trem"],
            pattern=r"(ferrovia|trilho|AMV|dormente|via\s+permanente|ferroviário|trem)",
            eixo="Vertical",
            segment="Ferrovia",
            tier="Sonnet",
            aliases=["agente-s3"],
        ),
        "infraestrutura_s4": RoutingRule(
            agent_code="Manta 03-S4",
            agent_id="manta-03-s4",
            agent_name="agente-infraestrutura (S4)",
            keywords=["metrô", "estação", "NATM", "PSD", "VLT", "linha", "túnel urbano"],
            pattern=r"(metrô|estação|NATM|PSD|VLT|linha\s*\d|túnel\s+urb)",
            eixo="Vertical",
            segment="Metrô",
            tier="Sonnet",
            aliases=["agente-s4"],
        ),

        # === VERTICAL AGENTS — NEW SEGMENTS (S6-S10) ===
        "portos": RoutingRule(
            agent_code="Manta 03-S6",
            agent_id="manta-03-s6",
            agent_name="agente-portos",
            keywords=["porto", "terminal", "ANTAQ", "dragagem", "molhe", "berço", "calado", "contêiner", "granel"],
            pattern=r"(porto|terminal|ANTAQ|dragagem|molhe|quebra-mar|berço|calado|contêiner|granel|cais|píer|hidrovia|TUP|TPS|PIANC)",
            eixo="Vertical",
            segment="Portos",
            tier="Sonnet",
            status="Operacional",
            aliases=["agente-s6"],
        ),
        "aeroportos": RoutingRule(
            agent_code="Manta 03-S7",
            agent_id="manta-03-s7",
            agent_name="agente-aeroportos",
            keywords=["aeroporto", "pista", "ANAC", "ICAO", "TPS", "TECA", "balizamento", "taxiway"],
            pattern=r"(aeroporto|pista\s+pouso|ANAC|RBAC|ICAO|TPS|TECA|balizamento|PAPI|ILS|taxiway|TWY|RWY|jetway|aviação)",
            eixo="Vertical",
            segment="Aeroportos",
            tier="Sonnet",
            status="Operacional",
            aliases=["agente-s7"],
        ),
        "saneamento": RoutingRule(
            agent_code="Manta 03-S8",
            agent_id="manta-03-s8",
            agent_name="agente-saneamento",
            keywords=["saneamento", "ETA", "ETE", "adutora", "esgoto", "AySA", "drenagem", "SNIS"],
            pattern=r"(saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem\s+urb|água\s+tratada|SNIS|PMSB|elevatória|reservatório|UASB|lodo|digestor)",
            eixo="Vertical",
            segment="Saneamento",
            tier="Sonnet",
            status="Operacional",
            aliases=["agente-s8"],
        ),
        "energia": RoutingRule(
            agent_code="Manta 03-S9",
            agent_id="manta-03-s9",
            agent_name="agente-energia",
            keywords=["transmissão", "LT", "subestação", "ANEEL", "RAP", "leilão", "ONS", "EPE"],
            pattern=r"(transmissão|LT\s|subestação|ANEEL|RAP|leilão\s+transmissão|ONS|EPE|PDE|torre\s+estaiada|cabo\s+condutor|ACSR|geração|eólica|hidráulica|solar)",
            eixo="Vertical",
            segment="Energia",
            tier="Sonnet",
            status="Operacional",
            aliases=["agente-s9"],
        ),
        "barragens": RoutingRule(
            agent_code="Manta 03-S10",
            agent_id="manta-03-s10",
            agent_name="agente-barragens",
            keywords=["barragem", "vertedouro", "CFRD", "CCR", "rejeitos", "PNSB", "ICOLD", "CBDB"],
            pattern=r"(barragem|vertedouro|CFRD|CCR|RCC|rejeitos|TSF|PNSB|ICOLD|CBDB|dique|ANM|descomissionamento|alteamento)",
            eixo="Vertical",
            segment="Barragens",
            tier="Sonnet",
            status="Operacional",
            aliases=["agente-s10"],
        ),
    }

    def __init__(self):
        """Initialize router with pre-compiled patterns"""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance"""
        self._compiled_patterns = {}
        for rule_key, rule in self.ROUTING_RULES.items():
            try:
                # Case-insensitive pattern matching
                self._compiled_patterns[rule_key] = re.compile(
                    rule.pattern,
                    re.IGNORECASE | re.MULTILINE
                )
            except re.error as e:
                logger.error(f"Failed to compile pattern for {rule_key}: {e}")

    def detect_intent(self, user_input: str) -> RoutingIntent:
        """
        Detect user intent and identify target agent

        Args:
            user_input: User query or message

        Returns:
            RoutingIntent with detected agent and confidence
        """
        if not user_input or not user_input.strip():
            return self._route_to_maestro("empty_input")

        user_input_lower = user_input.lower()

        # Find all matching rules with confidence scores
        matches: List[Tuple[str, RuleMatch]] = []

        for rule_key, rule in self.ROUTING_RULES.items():
            match_result = self._match_rule(
                rule_key,
                rule,
                user_input_lower,
                user_input
            )
            if match_result:
                matches.append((rule_key, match_result))

        # Sort by confidence (descending) and match count
        matches.sort(
            key=lambda x: (x[1].confidence, x[1].match_count),
            reverse=True
        )

        if matches:
            best_match_key, best_match = matches[0]
            best_rule = self.ROUTING_RULES[best_match_key]
            return self._create_routing_intent(best_rule, best_match)
        else:
            # Fallback to Maestro if no match found
            return self._route_to_maestro("no_match")

    def _match_rule(
        self,
        rule_key: str,
        rule: RoutingRule,
        user_input_lower: str,
        user_input_original: str
    ) -> Optional[RuleMatch]:
        """
        Match a single rule against user input

        Returns:
            RuleMatch if matched, None otherwise
        """
        # Pattern matching using compiled regex
        compiled_pattern = self._compiled_patterns.get(rule_key)
        if not compiled_pattern:
            return None

        pattern_match = compiled_pattern.search(user_input_lower)
        keyword_matches = []

        # Keyword matching (exact word boundaries)
        for keyword in rule.keywords:
            # Create word boundary pattern
            kw_pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(kw_pattern, user_input_lower, re.IGNORECASE):
                keyword_matches.append(keyword)

        # Calculate confidence
        if pattern_match and keyword_matches:
            match_count = len(keyword_matches)
            if match_count >= 2:
                confidence = 0.95  # Multiple exact keyword matches
            elif match_count == 1 and pattern_match:
                confidence = 0.85  # Pattern + keyword match
            else:
                confidence = 0.75
        elif pattern_match:
            confidence = 0.70  # Only pattern match
        elif keyword_matches:
            confidence = 0.60  # Only keyword match
        else:
            return None

        return RuleMatch(
            agent_code=rule.agent_code,
            matched_keywords=keyword_matches,
            match_count=len(keyword_matches),
            confidence=confidence,
            rule_pattern=rule.pattern,
        )

    def _create_routing_intent(
        self,
        rule: RoutingRule,
        match: RuleMatch
    ) -> RoutingIntent:
        """Create RoutingIntent from matched rule"""
        confidence_level = self._get_confidence_level(match.confidence)

        return RoutingIntent(
            agent_code=rule.agent_code,
            agent_name=rule.agent_name,
            agent_id=rule.agent_id,
            confidence=match.confidence,
            confidence_level=confidence_level,
            matched_keywords=match.matched_keywords,
            eixo=rule.eixo,
            segment=rule.segment,
            service_url=rule.service_url,
            aliases=rule.aliases or [],
            tier=rule.tier,
            status=rule.status,
        )

    def _route_to_maestro(self, reason: str) -> RoutingIntent:
        """Route to Maestro (fallback router)"""
        rule = self.ROUTING_RULES["maestro"]
        match = RuleMatch(
            agent_code=rule.agent_code,
            matched_keywords=[],
            match_count=0,
            confidence=0.0,
            rule_pattern="<fallback>",
        )
        return self._create_routing_intent(rule, match)

    def _get_confidence_level(self, confidence: float) -> RoutingConfidence:
        """Map confidence score to RoutingConfidence level"""
        if confidence >= 0.95:
            return RoutingConfidence.EXACT
        elif confidence >= 0.75:
            return RoutingConfidence.HIGH
        elif confidence >= 0.5:
            return RoutingConfidence.MEDIUM
        elif confidence > 0.0:
            return RoutingConfidence.LOW
        else:
            return RoutingConfidence.FALLBACK

    def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get complete profile for a specific agent"""
        for rule in self.ROUTING_RULES.values():
            if rule.agent_id.lower() == agent_id.lower():
                return AgentProfile(
                    id=rule.agent_id,
                    code=rule.agent_code,
                    name=rule.agent_name,
                    aliases=rule.aliases or [],
                    description=rule.description,
                    eixo=rule.eixo,
                    segment=rule.segment,
                    tier=rule.tier,
                    status=rule.status,
                    service_url=rule.service_url,
                    routing_keywords=rule.keywords,
                    routing_pattern=rule.pattern,
                )
        return None

    def list_agents(self) -> List[AgentProfile]:
        """List all available agents"""
        profiles = []
        for rule in self.ROUTING_RULES.values():
            profiles.append(AgentProfile(
                id=rule.agent_id,
                code=rule.agent_code,
                name=rule.agent_name,
                aliases=rule.aliases or [],
                description=rule.description,
                eixo=rule.eixo,
                segment=rule.segment,
                tier=rule.tier,
                status=rule.status,
                service_url=rule.service_url,
                routing_keywords=rule.keywords,
                routing_pattern=rule.pattern,
            ))
        return profiles

    def list_agents_by_eixo(self, eixo: str) -> List[AgentProfile]:
        """List agents filtered by Eixo (Horizontal/Vertical/Lifecycle)"""
        return [a for a in self.list_agents() if a.eixo.lower() == eixo.lower()]

    def search_agents(self, query: str) -> List[AgentProfile]:
        """Search agents by name, code, or keywords"""
        query_lower = query.lower()
        results = []

        for rule in self.ROUTING_RULES.values():
            profile = AgentProfile(
                id=rule.agent_id,
                code=rule.agent_code,
                name=rule.agent_name,
                aliases=rule.aliases or [],
                description=rule.description,
                eixo=rule.eixo,
                segment=rule.segment,
                tier=rule.tier,
                status=rule.status,
                service_url=rule.service_url,
                routing_keywords=rule.keywords,
                routing_pattern=rule.pattern,
            )

            # Check multiple fields for match
            if (query_lower in rule.agent_id.lower() or
                query_lower in rule.agent_name.lower() or
                query_lower in rule.agent_code.lower() or
                any(query_lower in k.lower() for k in rule.keywords) or
                any(query_lower in a.lower() for a in (rule.aliases or []))):
                results.append(profile)

        return results
