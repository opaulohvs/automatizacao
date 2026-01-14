"""
Script principal para execução via linha de comando
"""
from processador import ProcessadorAutomatizacao
import sys


def main():
    print("=" * 60)
    print("SISTEMA DE AUTOMAÇÃO - SALDO DE INFO PARA BM")
    print("=" * 60)
    print()
    
    processador = ProcessadorAutomatizacao()
    
    try:
        # Processa todas as pessoas
        resultados = processador.processar()
        
        if not resultados:
            print("\nNenhum resultado encontrado.")
            return
        
        # Gera relatório
        print("\n" + "=" * 60)
        print("GERANDO RELATÓRIO PARA BM")
        print("=" * 60)
        
        relatorio = processador.gerar_relatorio_bm()
        
        if relatorio:
            print(f"\nTotal processado: {relatorio['total_processado']}")
            print(f"Total relevante (TIM/Algar disponíveis): {relatorio['total_relevante']}")
            
            # Salva relatório
            arquivo = processador.salvar_relatorio(formato='json')
            
            if arquivo:
                print(f"\nRelatório salvo com sucesso!")
                print(f"Arquivo: {arquivo}")
        
        # Mostra resumo
        print("\n" + "=" * 60)
        print("RESUMO DOS RESULTADOS")
        print("=" * 60)
        
        for r in resultados[:10]:  # Mostra primeiros 10
            status = "✓" if r.get('is_target') and r.get('disponivel') else "✗"
            print(f"{status} CPF: {r['cpf']} | Número: {r.get('numero', 'N/A')} | Operadora: {r.get('operadora', 'N/A')}")
        
        if len(resultados) > 10:
            print(f"... e mais {len(resultados) - 10} resultados")
        
        # Fecha conexões
        processador.close()
        
    except KeyboardInterrupt:
        print("\n\nProcessamento interrompido pelo usuário.")
        try:
            processador.close()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"\nErro durante processamento: {e}")
        import traceback
        traceback.print_exc()
        try:
            processador.close()
        except:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()

