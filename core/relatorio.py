def gerar_relatorio(datas, alunos, total_faltas=None):
    print("\n" + "="*65)
    print("RELATÓRIO DE FALTAS".center(65))
    print("="*65)

    if total_faltas is None:
        total_faltas = {}

    for nome, pres in alunos.items():
        if len(pres) != len(datas):
            continue

        faltas_dias = [datas[i] for i, p in enumerate(pres) if p == "F"]
        if faltas_dias:
            calc = len(faltas_dias)
            ofc = total_faltas.get(nome)  # retorna None se não existir

            if ofc is not None:
                status = "OK" if ofc == calc else f"ERRO ({ofc})"
            else:
                status = ""  # não marca erro se não houver total oficial

            print(f"{nome}")
            print(f"   Faltou: {', '.join(faltas_dias)}")
            if status:
                print(f"   Total: {calc} | Oficial: {ofc} → {status}\n")
            else:
                print(f"   Total: {calc}\n")
