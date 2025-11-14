"""
Compliance Checker Service
Checks axe-core results against 10 specific compliance requirements
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AxeCoreResult(BaseModel):
    """Model for axe-core scan results"""
    violations: List[Dict[str, Any]] = []
    incomplete: List[Dict[str, Any]] = []
    passes: List[Dict[str, Any]] = []
    url: Optional[str] = None


class ComplianceChecker:
    """Checks compliance against 10 specific requirements"""
    
    COMPLIANCE_CHECKS = {
        "meaningful_sequence": {
            "name": "Meaningful Sequence",
            "description": "Ensure reading order makes logical sense for screen readers"
        },
        "sensory_characteristics": {
            "name": "Sensory Characteristics",
            "description": "Do not rely solely on colour, shape, or sound to convey meaning"
        },
        "use_of_colour": {
            "name": "Use of Colour",
            "description": "Information should not depend only on colour differences"
        },
        "keyboard_accessible": {
            "name": "Keyboard Accessible",
            "description": "All functionality should be usable via keyboard only"
        },
        "no_keyboard_trap": {
            "name": "No Keyboard Trap",
            "description": "Ensure users can navigate in and out of components using the keyboard"
        },
        "pointer_cancellation": {
            "name": "Pointer Cancellation",
            "description": "Click or drag actions should be cancellable or undoable"
        },
        "label_in_name": {
            "name": "Label in Name",
            "description": "Visible label should match the accessible name"
        },
        "timing_adjustable": {
            "name": "Timing Adjustable",
            "description": "Allow users to extend or disable time limits where applicable"
        },
        "seizures": {
            "name": "Seizures",
            "description": "Avoid flashing content exceeding 3 flashes per second"
        },
        "bypass_blocks": {
            "name": "Bypass Blocks",
            "description": "Provide skip links or navigation mechanisms to bypass repetitive content"
        }
    }
    
    def check_all(self, axe_results: AxeCoreResult) -> List[Dict[str, Any]]:
        """Run all compliance checks"""
        results = []
        
        for check_id, check_info in self.COMPLIANCE_CHECKS.items():
            check_method = getattr(self, f"_check_{check_id}", None)
            if check_method:
                result = check_method(axe_results)
                results.append({
                    "check_id": check_id,
                    "check_name": check_info["name"],
                    "description": check_info["description"],
                    "passed": result["passed"],
                    "issues": result["issues"],
                    "recommendation": result.get("recommendation")
                })
        
        return results
    
    def _check_meaningful_sequence(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 1: Meaningful Sequence"""
        issues = []
        
        # Check for violations related to reading order
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            if any(keyword in violation_id for keyword in ["reading-order", "sequence", "tab-order", "focus-order"]):
                issues.append(f"Reading order issue: {violation.get('description', 'Unknown')}")
        
        # Check for incomplete tests related to sequence
        for incomplete in axe_results.incomplete:
            incomplete_id = incomplete.get("id", "").lower()
            if any(keyword in incomplete_id for keyword in ["reading-order", "sequence", "tab-order"]):
                issues.append(f"Potential reading order issue: {incomplete.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure that the DOM order matches the visual reading order. "
            "Use semantic HTML and proper heading hierarchy (h1-h6). "
            "Test with screen readers to verify logical flow."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_sensory_characteristics(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 2: Sensory Characteristics"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["color", "colour", "shape", "sound", "sensory", "visual-only"]):
                issues.append(f"Sensory characteristic issue: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Do not rely solely on visual cues like color, shape, or position. "
            "Add text labels, icons with alt text, or other non-visual indicators. "
            "Ensure information is conveyed through multiple means."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_use_of_colour(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 3: Use of Colour"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["color-contrast", "color", "colour", "contrast"]):
                # Specifically check for color-only issues
                help_text = violation.get("help", "").lower()
                if "color" in help_text and ("only" in help_text or "solely" in help_text):
                    issues.append(f"Color-only dependency: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure information is not conveyed by color alone. "
            "Add text labels, icons, patterns, or other visual indicators. "
            "Use sufficient color contrast (WCAG AA: 4.5:1 for normal text, 3:1 for large text)."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_keyboard_accessible(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 4: Keyboard Accessible"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["keyboard", "focus", "tabindex", "interactive", "clickable"]):
                issues.append(f"Keyboard accessibility issue: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure all interactive elements are keyboard accessible. "
            "Add proper tabindex values, ensure focus indicators are visible, "
            "and test navigation using only Tab, Enter, and arrow keys."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_no_keyboard_trap(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 5: No Keyboard Trap"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["focus-trap", "keyboard-trap", "focus-lock", "modal"]):
                issues.append(f"Keyboard trap detected: {violation.get('description', 'Unknown')}")
        
        # Check for focus management issues
        for incomplete in axe_results.incomplete:
            incomplete_id = incomplete.get("id", "").lower()
            if "focus" in incomplete_id and "trap" in incomplete_id:
                issues.append(f"Potential keyboard trap: {incomplete.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure users can navigate away from all components using keyboard. "
            "In modals, provide an Escape key handler and ensure focus returns to the trigger. "
            "Test tab navigation to verify no components trap focus."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_pointer_cancellation(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 6: Pointer Cancellation"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["pointer", "click", "drag", "touch", "mouse"]):
                # Check if it's about cancellation
                help_text = violation.get("help", "").lower()
                if any(keyword in help_text for keyword in ["cancel", "undo", "pointer"]):
                    issues.append(f"Pointer cancellation issue: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure click and drag actions can be cancelled. "
            "For drag operations, allow cancellation by moving outside the drop zone or pressing Escape. "
            "For click actions, provide undo functionality where appropriate."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_label_in_name(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 7: Label in Name"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["label", "name", "accessible-name", "aria-label", "aria-labelledby"]):
                issues.append(f"Label/name mismatch: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Ensure visible labels match accessible names. "
            "Use proper label associations (label for, aria-label, aria-labelledby). "
            "Test with screen readers to verify labels are announced correctly."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_timing_adjustable(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 8: Timing Adjustable"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["timeout", "timing", "session", "auto-refresh", "meta-refresh"]):
                issues.append(f"Timing issue: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Allow users to extend or disable time limits. "
            "Provide warnings before timeouts expire. "
            "Avoid auto-refresh or auto-redirect without user control."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_seizures(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 9: Seizures"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["flash", "blink", "flicker", "seizure", "animation"]):
                issues.append(f"Flashing content detected: {violation.get('description', 'Unknown')}")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Avoid content that flashes more than 3 times per second. "
            "Provide controls to pause, stop, or hide animations. "
            "Respect user preferences for reduced motion (prefers-reduced-motion)."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}
    
    def _check_bypass_blocks(self, axe_results: AxeCoreResult) -> Dict[str, Any]:
        """Check 10: Bypass Blocks"""
        issues = []
        
        for violation in axe_results.violations:
            violation_id = violation.get("id", "").lower()
            description = violation.get("description", "").lower()
            
            if any(keyword in violation_id or keyword in description 
                   for keyword in ["bypass", "skip", "landmark", "region", "main", "navigation"]):
                issues.append(f"Bypass block issue: {violation.get('description', 'Unknown')}")
        
        # Check if there are skip links
        has_skip_links = False
        for pass_check in axe_results.passes:
            pass_id = pass_check.get("id", "").lower()
            if "skip" in pass_id or "bypass" in pass_id:
                has_skip_links = True
                break
        
        if not has_skip_links and len(issues) == 0:
            # No violations but also no skip links detected
            issues.append("No skip links or bypass mechanisms detected")
        
        passed = len(issues) == 0
        recommendation = None if passed else (
            "Provide skip links to bypass repetitive content like navigation menus. "
            "Use ARIA landmarks (main, navigation, banner, contentinfo). "
            "Ensure skip links are visible on focus and work with keyboard navigation."
        )
        
        return {"passed": passed, "issues": issues, "recommendation": recommendation}

