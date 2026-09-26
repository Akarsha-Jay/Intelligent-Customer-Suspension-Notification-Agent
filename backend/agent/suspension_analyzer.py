"""
Suspension Remark Analysis Component.

Classifies customer suspension remarks into deterministic categories:
- BILL_OVERDUE
- PAYMENT_NOT_RECEIVED
- CUSTOMER_REQUESTED
- TECHNICAL_ISSUE
- ACCOUNT_ISSUE
- UNKNOWN

Designed with an extensible rule engine that can be supplemented with an LLM
classifier in the future if required.
"""

import re
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SuspensionCategory(str, Enum):
    BILL_OVERDUE = "BILL_OVERDUE"
    PAYMENT_NOT_RECEIVED = "PAYMENT_NOT_RECEIVED"
    CUSTOMER_REQUESTED = "CUSTOMER_REQUESTED"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    ACCOUNT_ISSUE = "ACCOUNT_ISSUE"
    UNKNOWN = "UNKNOWN"


class SuspensionAnalysisResult(BaseModel):
    """Result of analyzing a customer suspension remark."""
    category: SuspensionCategory
    normalized_remark: str
    matched_pattern: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explanation: str
    is_payment_related: bool


class SuspensionAnalyzer:
    """Analyzes customer suspension remarks using rule-based pattern matching."""

    # Priority-ordered pattern dictionary
    # Pattern matching is case-insensitive and supports regex patterns
    PATTERNS: Dict[SuspensionCategory, List[str]] = {
        SuspensionCategory.CUSTOMER_REQUESTED: [
            r"customer\s*requested",
            r"temporary\s*suspension\s*requested",
            r"requested\s*(?:by\s*customer|temporary\s*suspension|service\s*suspension)",
            r"client\s*requested",
            r"voluntary\s*suspension",
            r"user\s*requested",
        ],
        SuspensionCategory.PAYMENT_NOT_RECEIVED: [
            r"payment\s*(?:was\s*)?not\s*received",
            r"non[- ]payment",
            r"payment\s*pending",
            r"unpaid\s*balance",
            r"arrears",
        ],
        SuspensionCategory.BILL_OVERDUE: [
            r"bill\s*overdue",
            r"unpaid\s*bill",
            r"outstanding\s*payment",
            r"outstanding\s*bill",
            r"overdue\s*bill",
            r"overdue\s*payment",
            r"bill\s*pending",
            r"overdue",
        ],
        SuspensionCategory.TECHNICAL_ISSUE: [
            r"technical\s*issue",
            r"service\s*issue",
            r"line\s*(?:fault|maintenance|down)",
            r"network\s*(?:issue|maintenance|fault)",
            r"infrastructure",
            r"system\s*error",
        ],
        SuspensionCategory.ACCOUNT_ISSUE: [
            r"account\s*issue",
            r"verification\s*required",
            r"identity\s*verification",
            r"kyc",
            r"documentation\s*pending",
            r"compliance",
            r"security\s*check",
        ],
    }

    @classmethod
    def analyze(cls, remark: Optional[str]) -> SuspensionAnalysisResult:
        """
        Analyze a suspension remark string and return a structured classification.
        """
        if not remark or not remark.strip():
            return SuspensionAnalysisResult(
                category=SuspensionCategory.UNKNOWN,
                normalized_remark="",
                matched_pattern=None,
                confidence=0.5,
                explanation="No remark was provided for this suspended account.",
                is_payment_related=False,
            )

        clean_remark = remark.strip()
        lowered = clean_remark.lower()

        # Check rules in strict order
        for category, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, lowered):
                    is_payment = category in (
                        SuspensionCategory.BILL_OVERDUE,
                        SuspensionCategory.PAYMENT_NOT_RECEIVED,
                    )
                    return SuspensionAnalysisResult(
                        category=category,
                        normalized_remark=clean_remark,
                        matched_pattern=pattern,
                        confidence=1.0,
                        explanation=f"Matched pattern '{pattern}' under category {category.value}.",
                        is_payment_related=is_payment,
                    )

        # Fallback to UNKNOWN
        return SuspensionAnalysisResult(
            category=SuspensionCategory.UNKNOWN,
            normalized_remark=clean_remark,
            matched_pattern=None,
            confidence=0.6,
            explanation="Remark does not match standard categories; defaulting to generic suspension.",
            is_payment_related=False,
        )
