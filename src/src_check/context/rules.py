"""Context-aware rule management for src-check.

This module provides functionality to adjust rules based on file context,
allowing for more intelligent and nuanced code checking.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src_check.context import FileType


@dataclass
class RuleContext:
    """Context information for rule application."""
    
    file_type: FileType
    file_path: str
    severity_multiplier: float
    rule_adjustments: Dict[str, Any]
    
    def adjust_severity(self, original_severity: str) -> str:
        """Adjust severity based on context.
        
        Args:
            original_severity: Original severity level
            
        Returns:
            Adjusted severity level
        """
        severity_levels = ['info', 'warning', 'error', 'critical']
        
        if self.severity_multiplier == 0.0:
            return 'info'
        elif self.severity_multiplier < 0.5:
            # Reduce severity
            current_index = severity_levels.index(original_severity.lower())
            new_index = max(0, current_index - 1)
            return severity_levels[new_index]
        elif self.severity_multiplier > 1.0:
            # Increase severity
            current_index = severity_levels.index(original_severity.lower())
            new_index = min(len(severity_levels) - 1, current_index + 1)
            return severity_levels[new_index]
        else:
            return original_severity
            
    def should_apply_rule(self, rule_name: str) -> bool:
        """Check if a rule should be applied in this context.
        
        Args:
            rule_name: Name of the rule to check
            
        Returns:
            True if the rule should be applied
        """
        # Check specific rule adjustments
        if rule_name in self.rule_adjustments:
            rule_config = self.rule_adjustments[rule_name]
            if isinstance(rule_config, dict) and 'enabled' in rule_config:
                return rule_config['enabled']
                
        # Check for 'all' rules setting
        if 'all' in self.rule_adjustments:
            all_config = self.rule_adjustments['all']
            if isinstance(all_config, dict) and 'enabled' in all_config:
                return all_config['enabled']
                
        # Default to enabled
        return True
        
    def get_threshold_multiplier(self, metric: str) -> float:
        """Get threshold multiplier for a metric.
        
        Args:
            metric: Name of the metric (e.g., 'complexity', 'coupling')
            
        Returns:
            Multiplier to apply to the threshold
        """
        if metric in self.rule_adjustments:
            rule_config = self.rule_adjustments[metric]
            if isinstance(rule_config, dict):
                return rule_config.get('threshold_multiplier', 1.0)
                
        return 1.0
        
    def get_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """Get configuration for a specific rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Configuration dictionary for the rule
        """
        return self.rule_adjustments.get(rule_name, {})


class ContextAwareRuleManager:
    """Manages rule application based on file context."""
    
    def __init__(self):
        """Initialize the rule manager."""
        self._default_thresholds = {
            'complexity': {
                'cyclomatic': 10,
                'cognitive': 15,
            },
            'coupling': {
                'max_dependencies': 10,
                'max_imports': 10,
            },
            'line_length': {
                'max_length': 100,
            },
            'function_length': {
                'max_lines': 50,
            },
        }
        
    def get_adjusted_threshold(
        self, 
        metric: str, 
        sub_metric: str,
        context: RuleContext
    ) -> float:
        """Get adjusted threshold for a metric based on context.
        
        Args:
            metric: Main metric category
            sub_metric: Specific metric within the category
            context: Rule context information
            
        Returns:
            Adjusted threshold value
        """
        base_threshold = self._default_thresholds.get(metric, {}).get(sub_metric, 0)
        multiplier = context.get_threshold_multiplier(metric)
        
        return base_threshold * multiplier
        
    def filter_issues(
        self,
        issues: list,
        context: RuleContext
    ) -> list:
        """Filter issues based on context.
        
        Args:
            issues: List of issues found
            context: Rule context information
            
        Returns:
            Filtered list of issues
        """
        filtered_issues = []
        
        for issue in issues:
            # Check if rule should be applied
            rule_name = issue.get('rule', '')
            if not context.should_apply_rule(rule_name):
                continue
                
            # Adjust severity
            original_severity = issue.get('severity', 'warning')
            adjusted_severity = context.adjust_severity(original_severity)
            
            # Skip if severity becomes too low
            if adjusted_severity == 'info' and context.file_type == FileType.GENERATED:
                continue
                
            # Create adjusted issue
            adjusted_issue = issue.copy()
            adjusted_issue['severity'] = adjusted_severity
            adjusted_issue['context'] = {
                'file_type': context.file_type.name,
                'original_severity': original_severity,
                'adjusted': original_severity != adjusted_severity,
            }
            
            filtered_issues.append(adjusted_issue)
            
        return filtered_issues
        
    def get_rule_explanation(
        self,
        rule_name: str,
        context: RuleContext
    ) -> Dict[str, str]:
        """Get context-aware explanation for a rule.
        
        Args:
            rule_name: Name of the rule
            context: Rule context information
            
        Returns:
            Dictionary with explanation details
        """
        base_explanations = {
            'print_statements': {
                'importance': 'Print statements can interfere with logging systems',
                'fix': 'Replace with proper logging (e.g., logging.info())',
                'best_practice': 'Use structured logging for production code',
            },
            'hardcoded_values': {
                'importance': 'Hardcoded values reduce flexibility and maintainability',
                'fix': 'Move to configuration files or environment variables',
                'best_practice': 'Use configuration management for all settings',
            },
            'complexity': {
                'importance': 'High complexity makes code hard to understand and test',
                'fix': 'Break down complex functions into smaller pieces',
                'best_practice': 'Keep cyclomatic complexity under 10',
            },
        }
        
        explanation = base_explanations.get(rule_name, {}).copy()
        
        # Add context-specific notes
        if context.file_type == FileType.EXAMPLE:
            explanation['context_note'] = 'Rules are relaxed for example code'
        elif context.file_type == FileType.TEST:
            explanation['context_note'] = 'Test code has different quality requirements'
        elif context.file_type == FileType.PRODUCTION:
            explanation['context_note'] = 'Production code requires strict quality standards'
            
        return explanation