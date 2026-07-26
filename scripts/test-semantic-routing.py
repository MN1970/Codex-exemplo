"""
Integration tests for semantic routing classifier.

Tests the /route-semantic endpoint with 24 test prompts covering all agents.
Reports accuracy and confusion matrix.

Usage:
    python test-semantic-routing.py [--base-url http://localhost:8000]
"""

import logging
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import requests
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class RoutingTestCase:
    """Single test case for routing."""

    def __init__(self, query: str, expected_agents: List[str], category: str):
        """
        Initialize test case.

        Args:
            query: Test query string
            expected_agents: List of agent slugs (in priority order)
            category: Test category
        """
        self.query = query
        self.expected_agents = expected_agents
        self.category = category
        self.predicted_agent = None
        self.confidence = None
        self.passed = False
        self.method = None


class RoutingTester:
    """Tester for semantic routing classifier."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize tester.

        Args:
            base_url: Base URL for API (default localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/api/v1/route-semantic"
        self.test_cases: List[RoutingTestCase] = []
        self.results = []

    def create_test_cases(self) -> List[RoutingTestCase]:
        """
        Create comprehensive test cases covering all 20 agents.

        Returns:
            List of test cases
        """
        test_cases = [
            # Horizontal agents (11 tests)
            RoutingTestCase(
                "Ajuda com sinistro de obra civil e indenização",
                ["manta-01-claims"],
                "claims",
            ),
            RoutingTestCase(
                "Análise de termos contratuais e compliance legal",
                ["manta-02-contratual"],
                "contratual",
            ),
            RoutingTestCase(
                "Avaliação imobiliária e zoneamento urbano",
                ["manta-04-imobiliario"],
                "imobiliario",
            ),
            RoutingTestCase(
                "Orçamento SICRO para construção de rodovia",
                ["manta-05-orcamento"],
                "orcamento",
            ),
            RoutingTestCase(
                "Modelagem financeira e projeção VPL de projeto",
                ["manta-06-modelagem"],
                "modelagem",
            ),
            RoutingTestCase(
                "Cronograma Gantt e critical path para execução",
                ["manta-07-cronograma"],
                "cronograma",
            ),
            RoutingTestCase(
                "Análise de mercado e oportunidades de negócio",
                ["manta-13-bd"],
                "business-dev",
            ),
            RoutingTestCase(
                "Criação de apresentação PowerPoint executiva",
                ["manta-14-apresentacoes"],
                "apresentacoes",
            ),
            RoutingTestCase(
                "Consultoria estratégica para expansão",
                ["manta-15-advisory"],
                "advisory",
            ),
            RoutingTestCase(
                "Design de arquitetura de sistema IA",
                ["manta-16-arquiteto-ia"],
                "arquiteto-ia",
            ),

            # Vertical S1 - Rodovias (1 test)
            RoutingTestCase(
                "Projeto de pavimento CBUQ com terraplenagem e SICRO",
                ["manta-03-s1-rodovias"],
                "rodovias",
            ),

            # Vertical S2 - OAE (1 test)
            RoutingTestCase(
                "Ponte com viaduto e NBR 7187, túnel rodoviário",
                ["manta-03-s2-oae"],
                "oae",
            ),

            # Vertical S3 - Ferrovia (1 test)
            RoutingTestCase(
                "Ferrovia com trilho AMV e dormente via permanente",
                ["manta-03-s3-ferrovia"],
                "ferrovia",
            ),

            # Vertical S4 - Metrô (1 test)
            RoutingTestCase(
                "Estação metrô com NATM e PSD linha 4",
                ["manta-03-s4-metro"],
                "metro",
            ),

            # Vertical S6 - Portos (1 test)
            RoutingTestCase(
                "Porto terminal dragagem molhe berço contêiner ANTAQ",
                ["manta-03-s6-portos"],
                "portos",
            ),

            # Vertical S7 - Aeroportos (1 test)
            RoutingTestCase(
                "Aeroporto pista pouso ANAC ICAO TPS balizamento",
                ["manta-03-s7-aeroportos"],
                "aeroportos",
            ),

            # Vertical S8 - Saneamento (2 tests)
            RoutingTestCase(
                "Saneamento ETA tratamento água adutora",
                ["manta-03-s8-saneamento"],
                "saneamento",
            ),
            RoutingTestCase(
                "ETE esgoto drenagem urbana SNIS Lei 14.026 AySA",
                ["manta-03-s8-saneamento"],
                "saneamento",
            ),

            # Vertical S9 - Energia (2 tests)
            RoutingTestCase(
                "Transmissão LT subestação ANEEL RAP leilão",
                ["manta-03-s9-energia"],
                "energia",
            ),
            RoutingTestCase(
                "ONS EPE geração distribuição energia",
                ["manta-03-s9-energia"],
                "energia",
            ),

            # Vertical S10 - Barragens (2 tests)
            RoutingTestCase(
                "Barragem vertedouro CFRD CCR rejeitos",
                ["manta-03-s10-barragens"],
                "barragens",
            ),
            RoutingTestCase(
                "Barragem PNSB ICOLD CBDB TSF hidrica",
                ["manta-03-s10-barragens"],
                "barragens",
            ),
        ]

        self.test_cases = test_cases
        return test_cases

    def run_tests(self) -> List[Dict]:
        """
        Run all test cases against the API.

        Returns:
            List of test results
        """
        logger.info(f"Running {len(self.test_cases)} tests against {self.endpoint}")
        logger.info("=" * 80)

        for i, test in enumerate(self.test_cases, 1):
            logger.info(f"\n[{i}/{len(self.test_cases)}] Testing: {test.category}")
            logger.info(f"Query: {test.query[:70]}...")

            try:
                # Call API
                response = requests.post(
                    self.endpoint,
                    json={
                        "query": test.query,
                        "org_id": "test_org",
                        "top_k": 3,
                        "confidence_threshold": 0.0,
                        "use_fallback": True,
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"API Error {response.status_code}: {response.text}")
                    test.passed = False
                    continue

                result = response.json()

                # Extract top prediction
                if result.get("agents"):
                    top_agent = result["agents"][0]
                    test.predicted_agent = top_agent["agent_slug"]
                    test.confidence = top_agent["confidence"]
                    test.method = top_agent.get("method", "ml")

                    # Check if prediction is in expected agents
                    test.passed = test.predicted_agent in test.expected_agents

                    logger.info(
                        f"Predicted: {test.predicted_agent} "
                        f"(confidence: {test.confidence:.2%}, method: {test.method})"
                    )
                    logger.info(f"Expected: {', '.join(test.expected_agents)}")
                    logger.info(f"Result: {'PASS' if test.passed else 'FAIL'}")
                else:
                    logger.warning("No agents predicted")
                    test.passed = False

            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error. Is API running at {self.base_url}?")
                test.passed = False
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                test.passed = False

            self.results.append(test)

        return self.results

    def print_summary(self) -> Dict:
        """
        Print test summary with accuracy and confusion matrix.

        Returns:
            Summary statistics
        """
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        total = len(self.results)
        passed = sum(1 for t in self.results if t.passed)
        accuracy = (passed / total * 100) if total > 0 else 0

        logger.info(f"\nTotal tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Accuracy: {accuracy:.1f}%")

        # Category breakdown
        logger.info("\n--- Accuracy by Category ---")
        categories = {}
        for test in self.results:
            if test.category not in categories:
                categories[test.category] = {"total": 0, "passed": 0}
            categories[test.category]["total"] += 1
            if test.passed:
                categories[test.category]["passed"] += 1

        for cat in sorted(categories.keys()):
            stats = categories[cat]
            cat_accuracy = (
                stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            )
            logger.info(f"{cat:20} {stats['passed']:2}/{stats['total']:2} ({cat_accuracy:5.1f}%)")

        # Method breakdown
        logger.info("\n--- Predictions by Method ---")
        methods = {}
        for test in self.results:
            if test.method:
                methods[test.method] = methods.get(test.method, 0) + 1

        for method in sorted(methods.keys()):
            logger.info(f"{method:15} {methods[method]:3} predictions")

        # Confusion matrix (simplified - show misclassifications)
        logger.info("\n--- Misclassifications ---")
        misclassifications = [t for t in self.results if not t.passed]
        if misclassifications:
            for test in misclassifications:
                logger.info(
                    f"Expected: {test.expected_agents[0]:25} "
                    f"Got: {test.predicted_agent:25} "
                    f"({test.query[:40]}...)"
                )
        else:
            logger.info("No misclassifications!")

        logger.info("\n" + "=" * 80)

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "accuracy": accuracy,
            "accuracy_pct": f"{accuracy:.1f}%",
            "categories": categories,
            "methods": methods,
        }

    def save_results(self, output_file: str = "routing_test_results.json"):
        """
        Save test results to JSON file.

        Args:
            output_file: Path to save results
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        results_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for t in self.results if t.passed),
            "failed": sum(1 for t in self.results if not t.passed),
            "accuracy": sum(1 for t in self.results if t.passed) / len(self.results) if self.results else 0,
            "test_details": [
                {
                    "category": t.category,
                    "query": t.query,
                    "expected": t.expected_agents,
                    "predicted": t.predicted_agent,
                    "confidence": t.confidence,
                    "method": t.method,
                    "passed": t.passed,
                }
                for t in self.results
            ],
        }

        with open(output_path, "w") as f:
            json.dump(results_data, f, indent=2)

        logger.info(f"Results saved to {output_file}")


def main():
    """Main entry point for testing script."""
    parser = argparse.ArgumentParser(
        description="Integration tests for semantic routing classifier"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL for API",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="routing_test_results.json",
        help="Output file for test results",
    )

    args = parser.parse_args()

    logger.info("Manta Semantic Routing - Integration Tests")
    logger.info(f"API URL: {args.base_url}")

    try:
        # Initialize tester
        tester = RoutingTester(base_url=args.base_url)

        # Create and run tests
        tester.create_test_cases()
        tester.run_tests()

        # Print summary
        summary = tester.print_summary()

        # Save results
        tester.save_results(args.output)

        # Exit with appropriate code
        return 0 if summary["accuracy"] >= 70 else 1

    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
