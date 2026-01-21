from typing import Dict, List

from .models import StrategyPreset, StrategyTypeEnum


def get_strategy_presets() -> List[StrategyPreset]:
    """Get all available strategy presets"""
    return [
        StrategyPreset(
            name="Conservative Cash",
            description="Low-risk cash-only strategy with reinvestment",
            strategy_type=StrategyTypeEnum.CASH_ONLY,
            config={
                "strategy_type": "cash_only",
                "reinvest_cashflow": True,
            },
        ),
        StrategyPreset(
            name="Moderate Leverage",
            description="Balanced leveraged strategy with 60% LTV",
            strategy_type=StrategyTypeEnum.LEVERAGED,
            config={
                "strategy_type": "leveraged",
                "ltv_ratio": 0.6,
                "interest_rate": 0.115,
                "loan_term_years": 20,
                "reinvest_cashflow": True,
                "enable_refinancing": True,
                "refinance_frequency": "annually",
                "target_refinance_ltv": 0.5,
            },
        ),
        StrategyPreset(
            name="Aggressive Leverage",
            description="High-growth strategy with 80% LTV",
            strategy_type=StrategyTypeEnum.LEVERAGED,
            config={
                "strategy_type": "leveraged",
                "ltv_ratio": 0.8,
                "interest_rate": 0.125,
                "loan_term_years": 20,
                "reinvest_cashflow": True,
                "enable_refinancing": True,
                "refinance_frequency": "annually",
                "target_refinance_ltv": 0.6,
            },
        ),
        StrategyPreset(
            name="Balanced Mixed",
            description="60% leveraged, 40% cash properties",
            strategy_type=StrategyTypeEnum.MIXED,
            config={
                "strategy_type": "mixed",
                "leveraged_property_ratio": 0.6,
                "cash_property_ratio": 0.4,
                "ltv_ratio": 0.7,
                "interest_rate": 0.118,
                "loan_term_years": 20,
                "reinvest_cashflow": True,
                "enable_refinancing": True,
                "refinance_frequency": "annually",
                "target_refinance_ltv": 0.5,
            },
        ),
        StrategyPreset(
            name="Conservative Mixed",
            description="30% leveraged, 70% cash properties",
            strategy_type=StrategyTypeEnum.MIXED,
            config={
                "strategy_type": "mixed",
                "leveraged_property_ratio": 0.3,
                "cash_property_ratio": 0.7,
                "ltv_ratio": 0.5,
                "interest_rate": 0.112,
                "loan_term_years": 25,
                "reinvest_cashflow": True,
                "enable_refinancing": False,
                "refinance_frequency": "never",
            },
        ),
    ]


def get_preset_by_name(name: str) -> StrategyPreset:
    """Get a specific preset by name"""
    presets = get_strategy_presets()
    for preset in presets:
        if preset.name == name:
            return preset
    raise ValueError(f"Preset '{name}' not found")
