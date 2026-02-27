"""
Approval Manager module
Handles human-in-the-loop approval for sensitive or high-risk tasks
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from engine.logger import logger


class ApprovalManager:
    def __init__(self, approval_path: Optional[Path] = None):
        self.approval_path = approval_path or Path("approvals")
        self.approval_path.mkdir(exist_ok=True)
        self.pending_approvals = {}

        logger.info("Approval manager initialized")

    def requires_approval(self, task_data: Dict[str, Any]) -> bool:
        """
        Determine if a task requires human approval

        Args:
            task_data: Task information

        Returns:
            True if approval is required
        """
        # Define criteria for requiring approval
        high_risk_keywords = [
            'delete', 'remove', 'payment', 'transfer', 'send money',
            'confidential', 'sensitive', 'private', 'password'
        ]

        task_content = str(task_data).lower()

        # Check for high-risk keywords
        for keyword in high_risk_keywords:
            if keyword in task_content:
                logger.info(f"Task requires approval due to keyword: {keyword}")
                return True

        # Check task type
        task_type = task_data.get('type', '')
        if task_type in ['financial', 'legal', 'hr']:
            logger.info(f"Task requires approval due to type: {task_type}")
            return True

        return False

    def request_approval(self, task_id: str, task_data: Dict[str, Any], reason: str = "") -> str:
        """
        Create an approval request

        Args:
            task_id: Unique task identifier
            task_data: Task information
            reason: Reason for requiring approval

        Returns:
            Approval request ID
        """
        approval_id = f"APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_id}"

        approval_request = {
            'approval_id': approval_id,
            'task_id': task_id,
            'task_data': task_data,
            'reason': reason,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'approved_at': None,
            'approved_by': None
        }

        # Save to file
        approval_file = self.approval_path / f"{approval_id}.txt"
        self._write_approval_file(approval_file, approval_request)

        # Store in memory
        self.pending_approvals[approval_id] = approval_request

        logger.info(f"Approval requested: {approval_id}")
        return approval_id

    def check_approval_status(self, approval_id: str) -> str:
        """
        Check the status of an approval request

        Args:
            approval_id: Approval request ID

        Returns:
            Status: 'pending', 'approved', 'rejected'
        """
        # Check in-memory first
        if approval_id in self.pending_approvals:
            return self.pending_approvals[approval_id]['status']

        # Check file system
        approval_file = self.approval_path / f"{approval_id}.txt"
        if approval_file.exists():
            approval_data = self._read_approval_file(approval_file)
            return approval_data.get('status', 'pending')

        return 'not_found'

    def approve(self, approval_id: str, approver: str = "user") -> bool:
        """
        Approve a pending request

        Args:
            approval_id: Approval request ID
            approver: Name/ID of approver

        Returns:
            True if successful
        """
        try:
            if approval_id not in self.pending_approvals:
                logger.warning(f"Approval ID not found: {approval_id}")
                return False

            self.pending_approvals[approval_id]['status'] = 'approved'
            self.pending_approvals[approval_id]['approved_at'] = datetime.now().isoformat()
            self.pending_approvals[approval_id]['approved_by'] = approver

            # Update file
            approval_file = self.approval_path / f"{approval_id}.txt"
            self._write_approval_file(approval_file, self.pending_approvals[approval_id])

            logger.info(f"Approval granted: {approval_id} by {approver}")
            return True

        except Exception as e:
            logger.error(f"Error approving request: {e}")
            return False

    def reject(self, approval_id: str, reason: str = "") -> bool:
        """
        Reject a pending request

        Args:
            approval_id: Approval request ID
            reason: Reason for rejection

        Returns:
            True if successful
        """
        try:
            if approval_id not in self.pending_approvals:
                logger.warning(f"Approval ID not found: {approval_id}")
                return False

            self.pending_approvals[approval_id]['status'] = 'rejected'
            self.pending_approvals[approval_id]['rejected_at'] = datetime.now().isoformat()
            self.pending_approvals[approval_id]['rejection_reason'] = reason

            # Update file
            approval_file = self.approval_path / f"{approval_id}.txt"
            self._write_approval_file(approval_file, self.pending_approvals[approval_id])

            logger.info(f"Approval rejected: {approval_id}")
            return True

        except Exception as e:
            logger.error(f"Error rejecting request: {e}")
            return False

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests"""
        return [
            approval for approval in self.pending_approvals.values()
            if approval['status'] == 'pending'
        ]

    def _write_approval_file(self, file_path: Path, approval_data: Dict[str, Any]):
        """Write approval data to file"""
        content = f"""# Approval Request

**Approval ID:** {approval_data['approval_id']}
**Task ID:** {approval_data['task_id']}
**Status:** {approval_data['status']}
**Created:** {approval_data['created_at']}
**Reason:** {approval_data.get('reason', 'N/A')}

## Task Data

{approval_data['task_data']}

## Instructions

To approve: Update status to 'approved'
To reject: Update status to 'rejected'
"""
        file_path.write_text(content, encoding='utf-8')

    def _read_approval_file(self, file_path: Path) -> Dict[str, Any]:
        """Read approval data from file"""
        content = file_path.read_text(encoding='utf-8')

        # Simple parsing (in production, use proper format like JSON)
        approval_data = {'status': 'pending'}

        for line in content.split('\n'):
            if 'Status:**' in line:
                status = line.split('**')[-1].strip()
                approval_data['status'] = status

        return approval_data
