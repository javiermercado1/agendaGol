from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Permission schemas
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str  
    action: str    
    is_active: bool = True

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# UserRole schemas
class UserRoleBase(BaseModel):
    user_id: int
    role_id: int

class UserRoleCreate(UserRoleBase):
    assigned_by: Optional[int] = None

class UserRoleResponse(UserRoleBase):
    id: int
    assigned_at: datetime
    assigned_by: Optional[int] = None
    is_active: bool
    role: RoleResponse

    class Config:
        from_attributes = True

# RolePermission schemas
class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int
    granted_by: Optional[int] = None

class RolePermissionResponse(BaseModel):
    id: int
    role_id: int
    permission_id: int
    granted_at: datetime
    granted_by: Optional[int] = None
    role: RoleResponse
    permission: PermissionResponse

    class Config:
        from_attributes = True

# Schemas for validation and responses
class UserPermissionsResponse(BaseModel):
    user_id: int
    role: RoleResponse
    permissions: List[PermissionResponse]

class PermissionValidationRequest(BaseModel):
    user_id: int
    resource: str  # 'users', 'fields', 'reservations', 'roles'
    action: str    # 'view', 'create', 'edit', 'delete', 'manage'

class PermissionValidationResponse(BaseModel):
    has_permission: bool
    user_id: int
    resource: str
    action: str
    role_name: Optional[str] = None

# Role with permissions
class RoleWithPermissions(RoleResponse):
    permissions: List[PermissionResponse]
