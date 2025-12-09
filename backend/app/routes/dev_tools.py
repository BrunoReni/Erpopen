"""
Dev Tools API - Endpoints para monitoramento de qualidade e completude de features.
Apenas acessível para administradores com permissão admin:read.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.dependencies import require_permission
from app.feature_flags import (
    get_all_features,
    get_feature_by_id,
    get_features_by_module,
    get_features_by_status,
    get_incomplete_features,
    get_backend_only_features,
    get_features_statistics,
    FeatureStatus
)

router = APIRouter()


@router.get("/features/gaps")
def get_feature_gaps(
    _: bool = Depends(require_permission("admin:read"))
):
    """
    Retorna todas as features com gaps de implementação (backend sem frontend ou vice-versa).
    
    Útil para identificar trabalhos pendentes e inconsistências.
    """
    incomplete = get_incomplete_features()
    backend_only = get_backend_only_features()
    
    return {
        "critical_gaps": len(backend_only),  # Backend sem frontend é crítico
        "total_gaps": len(incomplete),
        "backend_only": [f.to_dict() for f in backend_only],
        "all_incomplete": [f.to_dict() for f in incomplete]
    }


@router.get("/features/stats")
def get_feature_statistics(
    _: bool = Depends(require_permission("admin:read"))
):
    """
    Retorna estatísticas gerais sobre o status de implementação das features.
    
    Útil para dashboards e métricas de qualidade.
    """
    stats = get_features_statistics()
    
    # Adicionar lista de módulos
    all_features = get_all_features()
    modules = {}
    
    for feature in all_features:
        if feature.module not in modules:
            modules[feature.module] = {
                "total": 0,
                "complete": 0,
                "incomplete": 0
            }
        
        modules[feature.module]["total"] += 1
        
        if feature.status == FeatureStatus.COMPLETE:
            modules[feature.module]["complete"] += 1
        elif feature.status in [FeatureStatus.BACKEND_ONLY, FeatureStatus.FRONTEND_ONLY, FeatureStatus.PARTIAL]:
            modules[feature.module]["incomplete"] += 1
    
    return {
        **stats,
        "modules": modules,
        "status_breakdown": {
            "complete": stats["complete"],
            "backend_only": stats["backend_only"],
            "frontend_only": stats["frontend_only"],
            "partial": stats["partial"],
            "disabled": stats["disabled"]
        }
    }


@router.get("/features/modules/{module}")
def get_module_features(
    module: str,
    _: bool = Depends(require_permission("admin:read"))
):
    """
    Retorna todas as features de um módulo específico.
    
    Path Parameters:
    - module: Nome do módulo (financeiro, vendas, compras, materiais)
    """
    features = get_features_by_module(module)
    
    if not features:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhuma feature encontrada para o módulo '{module}'"
        )
    
    complete = len([f for f in features if f.status == FeatureStatus.COMPLETE])
    
    return {
        "module": module,
        "total": len(features),
        "complete": complete,
        "incomplete": len(features) - complete,
        "completion_rate": round((complete / len(features) * 100), 2),
        "features": [f.to_dict() for f in features]
    }


@router.get("/features")
def list_all_features(
    module: Optional[str] = None,
    status: Optional[str] = None,
    _: bool = Depends(require_permission("admin:read"))
):
    """
    Lista todas as features registradas no sistema.
    
    Query Parameters:
    - module: Filtrar por módulo (financeiro, vendas, compras, materiais)
    - status: Filtrar por status (complete, backend_only, frontend_only, partial, disabled)
    
    Retorna lista de features com seus detalhes de implementação.
    """
    features = get_all_features()
    
    # Aplicar filtros
    if module:
        features = [f for f in features if f.module == module]
    
    if status:
        try:
            status_filter = FeatureStatus(status)
            features = [f for f in features if f.status == status_filter]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Status inválido. Valores válidos: {[s.value for s in FeatureStatus]}"
            )
    
    return {
        "total": len(features),
        "features": [f.to_dict() for f in features]
    }


@router.get("/features/{feature_id}")
def get_feature_detail(
    feature_id: str,
    _: bool = Depends(require_permission("admin:read"))
):
    """
    Retorna detalhes de uma feature específica.
    
    Path Parameters:
    - feature_id: ID da feature
    """
    feature = get_feature_by_id(feature_id)
    
    if not feature:
        raise HTTPException(
            status_code=404,
            detail=f"Feature '{feature_id}' não encontrada"
        )
    
    return feature.to_dict()


@router.get("/health")
def health_check():
    """
    Health check endpoint - não requer autenticação.
    Retorna status geral do sistema de quality gates.
    """
    stats = get_features_statistics()
    backend_only = len(get_backend_only_features())
    
    # Sistema está "unhealthy" se houver features com apenas backend
    is_healthy = backend_only == 0
    
    return {
        "status": "healthy" if is_healthy else "warning",
        "message": "Sistema OK" if is_healthy else f"{backend_only} feature(s) com apenas backend implementado",
        "total_features": stats["total"],
        "complete_features": stats["complete"],
        "critical_gaps": backend_only,
        "completion_rate": stats["completion_rate"]
    }
