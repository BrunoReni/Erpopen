#!/usr/bin/env python3
"""
Script para verificar completude de features localmente antes de commit/push.
Uso: python scripts/check_feature_completeness.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.feature_flags import (
    get_all_features,
    get_backend_only_features,
    get_features_statistics,
    FeatureStatus
)


def print_colored(text, color='default'):
    """Print colored text to terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'default': '\033[0m'
    }
    reset = '\033[0m'
    print(f"{colors.get(color, colors['default'])}{text}{reset}")


def print_header(text):
    """Print section header"""
    print("\n" + "=" * 70)
    print_colored(f"  {text}", 'cyan')
    print("=" * 70)


def main():
    """Main function"""
    print_header("🔍 Feature Completeness Check")
    
    # Get statistics
    stats = get_features_statistics()
    backend_only = get_backend_only_features()
    all_features = get_all_features()
    
    # Print overall statistics
    print_header("📊 Estatísticas Gerais")
    print(f"  Total de Features: {stats['total']}")
    print(f"  ✅ Completas: {stats['complete']} ({stats['completion_rate']:.1f}%)")
    print(f"  ⚠️  Incompletas: {stats['incomplete']}")
    print(f"  🔴 Backend Only: {stats['backend_only']}")
    print(f"  🟡 Parciais: {stats['partial']}")
    print(f"  ⚪ Desabilitadas: {stats['disabled']}")
    print(f"  📈 Média de Completude: {stats['average_completeness']:.1f}%")
    
    # Check for critical gaps
    if backend_only:
        print_header("🚨 GAPS CRÍTICOS - Features com apenas Backend")
        print_colored("  ⚠️  ATENÇÃO: As seguintes features têm apenas backend implementado:", 'red')
        print_colored("  Usuários NÃO podem acessar estas funcionalidades!\n", 'red')
        
        for feature in backend_only:
            print_colored(f"  🔴 {feature.name}", 'red')
            print(f"     ID: {feature.id}")
            print(f"     Módulo: {feature.module}")
            print(f"     Completude: {feature.completeness_percentage:.0f}%")
            if feature.issue_number:
                print(f"     Issue: #{feature.issue_number}")
            print(f"     Endpoints: {len(feature.backend_endpoints)}")
            print(f"     ⚠️  Faltando: Frontend implementation")
            print()
        
        print_colored("  ⚠️  AÇÃO NECESSÁRIA:", 'yellow')
        print("     1. Implementar componentes frontend para estas features")
        print("     2. Atualizar feature_flags.py com has_frontend=True")
        print("     3. Rodar este script novamente\n")
        
        # Exit with error code for pre-commit hooks
        return 1
    
    # Show incomplete features
    incomplete = [f for f in all_features if f.status in [
        FeatureStatus.FRONTEND_ONLY,
        FeatureStatus.PARTIAL
    ]]
    
    if incomplete:
        print_header("⚠️  Features Incompletas (Parciais)")
        for feature in incomplete:
            status_color = 'yellow' if feature.status == FeatureStatus.PARTIAL else 'blue'
            print_colored(f"  🟡 {feature.name}", status_color)
            print(f"     Módulo: {feature.module}")
            print(f"     Status: {feature.status.value}")
            print(f"     Completude: {feature.completeness_percentage:.0f}%")
            print(f"     Backend: {'✅' if feature.has_backend else '❌'}")
            print(f"     Frontend: {'✅' if feature.has_frontend else '❌'}")
            print(f"     Testes: {'✅' if feature.has_tests else '❌'}")
            print(f"     Docs: {'✅' if feature.has_docs else '❌'}")
            print()
    
    # Show complete features summary
    complete_features = [f for f in all_features if f.status == FeatureStatus.COMPLETE]
    if complete_features:
        print_header(f"✅ Features Completas ({len(complete_features)})")
        by_module = {}
        for f in complete_features:
            if f.module not in by_module:
                by_module[f.module] = []
            by_module[f.module].append(f.name)
        
        for module, features in sorted(by_module.items()):
            print_colored(f"  {module.upper()}: {len(features)} features", 'green')
            for name in features:
                print(f"    - {name}")
    
    # Final summary
    print_header("🎯 Resumo Final")
    if backend_only:
        print_colored("  ❌ FALHOU: Existem features com apenas backend", 'red')
        print_colored(f"     {len(backend_only)} feature(s) crítica(s) encontrada(s)", 'red')
        return 1
    elif stats['completion_rate'] < 50:
        print_colored("  ⚠️  AVISO: Taxa de completude baixa", 'yellow')
        print(f"     Completude atual: {stats['completion_rate']:.1f}%")
        print(f"     Recomendado: > 50%")
        return 0  # Warning but not error
    else:
        print_colored("  ✅ SUCESSO: Todas as features estão integradas!", 'green')
        print(f"     Taxa de completude: {stats['completion_rate']:.1f}%")
        print(f"     Média: {stats['average_completeness']:.1f}%")
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        print()  # Extra line for readability
        sys.exit(exit_code)
    except Exception as e:
        print_colored(f"\n❌ Erro ao executar verificação: {e}", 'red')
        import traceback
        traceback.print_exc()
        sys.exit(1)
