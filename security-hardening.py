"""
POS Monitor Security Hardening Module
Implements Windows ACLs and security best practices
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
import win32security
import win32api
import win32con
import ntsecuritycon as con
import pywintypes

class SecurityHardening:
    """Implements security hardening for POS Monitor installation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.install_dir = Path(os.environ.get('ProgramFiles')) / 'UniSight' / 'POS Monitor'
        self.data_dir = Path(os.environ.get('ProgramData')) / 'POSMonitor'
        self.log_dir = self.data_dir / 'logs'
        
    def apply_all_hardening(self):
        """Apply all security hardening measures"""
        try:
            self.logger.info("Starting security hardening...")
            
            # Create directories if needed
            self._ensure_directories()
            
            # Apply ACLs
            self._apply_directory_acls()
            self._apply_file_acls()
            
            # Configure service permissions
            self._configure_service_permissions()
            
            # Set audit policies
            self._configure_audit_policies()
            
            # Validate security settings
            self._validate_security()
            
            self.logger.info("Security hardening completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Security hardening failed: {e}")
            return False
    
    def _ensure_directories(self):
        """Ensure all directories exist"""
        for directory in [self.install_dir, self.data_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _apply_directory_acls(self):
        """Apply restrictive ACLs to directories"""
        
        # Installation directory - Read/Execute for Users, Full for Admins/SYSTEM
        self._set_directory_acl(
            self.install_dir,
            {
                'SYSTEM': con.FILE_ALL_ACCESS,
                'Administrators': con.FILE_ALL_ACCESS,
                'Users': con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE
            }
        )
        
        # Data directory - Full for SYSTEM/Admins only
        self._set_directory_acl(
            self.data_dir,
            {
                'SYSTEM': con.FILE_ALL_ACCESS,
                'Administrators': con.FILE_ALL_ACCESS
            }
        )
        
        # Log directory - Write for SYSTEM, Read for Admins
        self._set_directory_acl(
            self.log_dir,
            {
                'SYSTEM': con.FILE_ALL_ACCESS,
                'Administrators': con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE
            }
        )
    
    def _apply_file_acls(self):
        """Apply restrictive ACLs to specific files"""
        
        # Configuration file - Read for SYSTEM, Full for Admins
        config_file = self.data_dir / 'pos-monitor-config.json'
        if config_file.exists():
            self._set_file_acl(
                config_file,
                {
                    'SYSTEM': con.FILE_GENERIC_READ,
                    'Administrators': con.FILE_ALL_ACCESS
                }
            )
        
        # Executables - Read/Execute for all, no write
        for exe_file in self.install_dir.glob('*.exe'):
            self._set_file_acl(
                exe_file,
                {
                    'SYSTEM': con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE,
                    'Administrators': con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE,
                    'Users': con.FILE_GENERIC_READ | con.FILE_GENERIC_EXECUTE
                }
            )
    
    def _set_directory_acl(self, path: Path, permissions: dict):
        """Set ACL on a directory"""
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                str(path),
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Create new DACL
            dacl = win32security.ACL()
            
            # Add ACEs for each user/group
            for account, access in permissions.items():
                # Get SID for account
                sid = self._get_account_sid(account)
                
                # Add ACE
                dacl.AddAccessAllowedAceEx(
                    win32security.ACL_REVISION,
                    win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE,
                    access,
                    sid
                )
            
            # Set the new DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            
            # Apply to directory
            win32security.SetFileSecurity(
                str(path),
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
            self.logger.info(f"Applied ACL to directory: {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to set ACL on {path}: {e}")
            raise
    
    def _set_file_acl(self, path: Path, permissions: dict):
        """Set ACL on a file"""
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                str(path),
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Create new DACL
            dacl = win32security.ACL()
            
            # Add ACEs for each user/group
            for account, access in permissions.items():
                # Get SID for account
                sid = self._get_account_sid(account)
                
                # Add ACE
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    access,
                    sid
                )
            
            # Set the new DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            
            # Apply to file
            win32security.SetFileSecurity(
                str(path),
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
            self.logger.info(f"Applied ACL to file: {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to set ACL on {path}: {e}")
            raise
    
    def _get_account_sid(self, account_name: str):
        """Get SID for an account name"""
        try:
            # Handle well-known accounts
            if account_name == 'SYSTEM':
                return win32security.ConvertStringSidToSid('S-1-5-18')
            elif account_name == 'Administrators':
                return win32security.ConvertStringSidToSid('S-1-5-32-544')
            elif account_name == 'Users':
                return win32security.ConvertStringSidToSid('S-1-5-32-545')
            else:
                # Look up account
                return win32security.LookupAccountName(None, account_name)[0]
                
        except Exception as e:
            self.logger.error(f"Failed to get SID for {account_name}: {e}")
            raise
    
    def _configure_service_permissions(self):
        """Configure service-specific permissions"""
        try:
            # Set service to run as Local System (most secure for monitoring)
            subprocess.run([
                'sc', 'config', 'POSMonitor',
                'obj=', 'LocalSystem'
            ], check=True, capture_output=True)
            
            # Set service permissions (only admins can control)
            subprocess.run([
                'sc', 'sdset', 'POSMonitor',
                'D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)'
            ], check=True, capture_output=True)
            
            self.logger.info("Service permissions configured")
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Could not configure service permissions: {e}")
    
    def _configure_audit_policies(self):
        """Configure audit policies for security monitoring"""
        try:
            # Enable auditing on sensitive directories
            self._enable_directory_auditing(self.data_dir)
            self._enable_directory_auditing(self.log_dir)
            
            self.logger.info("Audit policies configured")
            
        except Exception as e:
            self.logger.warning(f"Could not configure audit policies: {e}")
    
    def _enable_directory_auditing(self, path: Path):
        """Enable auditing on a directory"""
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                str(path),
                win32security.SACL_SECURITY_INFORMATION
            )
            
            # Create SACL
            sacl = win32security.ACL()
            
            # Audit everyone for write/delete
            everyone_sid = win32security.ConvertStringSidToSid('S-1-1-0')
            
            # Add audit ACE
            sacl.AddAuditAccessAce(
                win32security.ACL_REVISION,
                con.FILE_WRITE_DATA | con.FILE_APPEND_DATA | con.DELETE,
                everyone_sid,
                1,  # Success
                1   # Failure
            )
            
            # Set SACL
            sd.SetSecurityDescriptorSacl(1, sacl, 0)
            
            # Apply to directory
            win32security.SetFileSecurity(
                str(path),
                win32security.SACL_SECURITY_INFORMATION,
                sd
            )
            
        except Exception as e:
            # Audit configuration requires special privileges
            self.logger.debug(f"Could not enable auditing on {path}: {e}")
    
    def _validate_security(self):
        """Validate security settings"""
        issues = []
        
        # Check directory permissions
        for directory in [self.install_dir, self.data_dir, self.log_dir]:
            if not self._check_directory_security(directory):
                issues.append(f"Insecure permissions on {directory}")
        
        # Check service configuration
        if not self._check_service_security():
            issues.append("Service security configuration issue")
        
        # Report issues
        if issues:
            self.logger.warning(f"Security validation issues: {issues}")
        else:
            self.logger.info("Security validation passed")
        
        return len(issues) == 0
    
    def _check_directory_security(self, path: Path) -> bool:
        """Check if directory has secure permissions"""
        try:
            # Get current ACL
            sd = win32security.GetFileSecurity(
                str(path),
                win32security.DACL_SECURITY_INFORMATION | 
                win32security.OWNER_SECURITY_INFORMATION
            )
            
            # Check owner is SYSTEM or Administrators
            owner_sid = sd.GetSecurityDescriptorOwner()
            owner_name = win32security.LookupAccountSid(None, owner_sid)[0]
            
            if owner_name not in ['SYSTEM', 'Administrators']:
                self.logger.warning(f"Unexpected owner for {path}: {owner_name}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Could not check security for {path}: {e}")
            return False
    
    def _check_service_security(self) -> bool:
        """Check service security configuration"""
        try:
            # Query service configuration
            result = subprocess.run(
                ['sc', 'qc', 'POSMonitor'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
            
            # Check running as LocalSystem
            if 'LocalSystem' not in result.stdout:
                self.logger.warning("Service not running as LocalSystem")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Could not check service security: {e}")
            return False
    
    def generate_security_report(self) -> dict:
        """Generate security configuration report"""
        report = {
            'timestamp': win32api.GetSystemTime(),
            'directories': {},
            'service': {},
            'recommendations': []
        }
        
        # Check each directory
        for directory in [self.install_dir, self.data_dir, self.log_dir]:
            report['directories'][str(directory)] = {
                'exists': directory.exists(),
                'secure': self._check_directory_security(directory) if directory.exists() else False
            }
        
        # Check service
        report['service'] = {
            'secure_config': self._check_service_security()
        }
        
        # Add recommendations
        if not all(d['secure'] for d in report['directories'].values()):
            report['recommendations'].append("Run security hardening to fix directory permissions")
        
        if not report['service']['secure_config']:
            report['recommendations'].append("Reconfigure service security settings")
        
        return report


def main():
    """Main function for standalone execution"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    hardening = SecurityHardening()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--report':
        # Generate security report
        report = hardening.generate_security_report()
        print(json.dumps(report, indent=2, default=str))
    else:
        # Apply hardening
        success = hardening.apply_all_hardening()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()