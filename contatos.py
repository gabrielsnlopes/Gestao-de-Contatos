# ==========================================
# GESTÃO DE CONTATOS
# ==========================================
# ==========================================
# Gabriel Lopes
# ==========================================

import csv
import json
import re
import shutil
import unicodedata

from pathlib import Path
from datetime import datetime, date
from difflib import SequenceMatcher


# ==========================================================
# CONFIGURACAO
# ==========================================================

PASTA = Path(__file__).resolve().parent

FICHEIRO = PASTA / "contactos.json"
BACKUP = PASTA / "contactos_backup.json"
EXPORTACAO = PASTA / "contactos_exportados.csv"
TEMPORARIO = PASTA / "contactos_temp.json"

contactos = {}

MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}


# ==========================================================
# FUNCOES AUXILIARES
# ==========================================================

def normalizar(texto):

    texto = str(texto).casefold()
    texto = unicodedata.normalize("NFD", texto)

    return "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    ).strip()


def calcularIdade(nascimento):

    data_nascimento = datetime.strptime(
        nascimento, "%d/%m/%Y"
    ).date()

    hoje = date.today()

    idade = hoje.year - data_nascimento.year

    if (hoje.month, hoje.day) < (
        data_nascimento.month,
        data_nascimento.day
    ):
        idade -= 1

    return idade


def validarData(nascimento):

    nascimento = nascimento.strip()

    try:

        if re.fullmatch(r"\d{8}", nascimento):
            data = datetime.strptime(nascimento, "%d%m%Y")

        elif re.fullmatch(r"\d{2}/\d{2}/\d{4}", nascimento):
            data = datetime.strptime(nascimento, "%d/%m/%Y")

        elif re.fullmatch(r"\d{2}/\d{2}/\d{2}", nascimento):
            data = datetime.strptime(nascimento, "%d/%m/%y")

        else:
            return None

        if data.date() > date.today():
            return None

        return data.strftime("%d/%m/%Y")

    except ValueError:
        return None


def numeroNormalizado(numero):
    return numero.replace("-", "")


def pedirCampoObrigatorio(pergunta):

    while True:

        valor = input(pergunta).strip()

        if valor:
            return valor

        print("Informação incorreta, digite novamente:")


# ==========================================================
# VALIDACAO DOS DADOS
# ==========================================================

def pedirNome():

    while True:

        nome = input("Nome completo: ").strip()

        partes = nome.split()

        if len(partes) >= 2 and all(
            parte.isalpha() for parte in partes
        ):
            return " ".join(partes)

        print("Informação incorreta, digite novamente:")


def pedirSexo():

    while True:

        print("\nSexo:")
        print("1 - Homem")
        print("2 - Mulher")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            return "Homem"

        elif opcao == "2":
            return "Mulher"

        print("Informação incorreta, digite novamente:")


def pedirEstadoCivil():

    estados_civis = {
        "1": "Solteiro(a)",
        "2": "Casado(a)",
        "3": "Divorciado(a)",
        "4": "Viúvo(a)",
        "5": "Separado(a)"
    }

    while True:

        print("\nEstado civil:")
        print("1 - Solteiro(a)")
        print("2 - Casado(a)")
        print("3 - Divorciado(a)")
        print("4 - Viúvo(a)")
        print("5 - Separado(a)")

        opcao = input("Escolha: ").strip()

        if opcao in estados_civis:
            return estados_civis[opcao]

        print("Opção inválida. Escolha um número de 1 a 5.")


def pedirTelemovel():

    while True:

        numero = input("Telemóvel: ").strip()

        formato_valido = re.fullmatch(
            r"\d+(?:-\d+)*", numero
        )

        if formato_valido:

            quantidade = len(numero.replace("-", ""))

            if 9 <= quantidade <= 15:
                return numero

        print("Informação incorreta, digite novamente:")


def pedirNascimento():

    while True:

        nascimento = input(
            "Nascimento (DD/MM/AAAA ou DDMMYYYY): "
        ).strip()

        data = validarData(nascimento)

        if data:
            return data

        print("Informação incorreta, digite novamente:")


def pedirMorada():

    return pedirCampoObrigatorio("Morada: ")


def pedirEmail():

    while True:

        email = input(
            "Email (opcional; Enter ou - para ignorar): "
        ).strip()

        if email in ("", "-"):
            return ""

        padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$"

        if re.fullmatch(padrao, email):
            return email

        print("Informação incorreta, digite novamente:")


def pedirNotas():

    return input("Notas (opcional): ").strip()


# ==========================================================
# CARREGAR E GUARDAR CONTACTOS
# ==========================================================

def carregarContactos():

    global contactos

    if not FICHEIRO.exists():

        contactos = {}

        print("\nAinda não existe uma lista guardada.")
        return

    try:

        with open(
            FICHEIRO, "r", encoding="utf-8"
        ) as ficheiro:

            dados = json.load(ficheiro)

        if not isinstance(dados, dict):
            raise ValueError("Formato de ficheiro inválido.")

        contactos = {}

        for numero, dados_contacto in dados.items():

            if not isinstance(dados_contacto, dict):
                continue

            nascimento = validarData(
                str(dados_contacto.get("nascimento", ""))
            )

            if nascimento is None:

                print(
                    f"Aviso: contacto {numero} ignorado "
                    "por ter uma data inválida."
                )

                continue

            contactos[str(numero)] = {

                "nome": str(dados_contacto.get("nome", "")),

                "sexo": str(
                    dados_contacto.get("sexo", "Não informado")
                ),

                "estado_civil": str(
                    dados_contacto.get("estado_civil", "Não informado")
                ),

                "nascimento": nascimento,

                "morada": str(dados_contacto.get("morada", "")),

                "email": str(dados_contacto.get("email", "")),

                "notas": str(dados_contacto.get("notas", "")),

                "criado": str(
                    dados_contacto.get(
                        "criado",
                        datetime.now().strftime("%d/%m/%Y %H:%M")
                    )
                )
            }

        print(
            f"\n{len(contactos)} contacto(s) carregado(s)."
        )

    except (OSError, json.JSONDecodeError, ValueError) as erro:

        print(f"\nErro ao carregar contactos: {erro}")

        contactos = {}


def guardarContactos():

    try:

        with open(
            TEMPORARIO, "w", encoding="utf-8"
        ) as ficheiro:

            json.dump(
                contactos,
                ficheiro,
                ensure_ascii=False,
                indent=4
            )

        if FICHEIRO.exists():

            shutil.copy2(FICHEIRO, BACKUP)

        TEMPORARIO.replace(FICHEIRO)

    except OSError as erro:

        print(f"Erro ao guardar contactos: {erro}")


# ==========================================================
# MOSTRAR CONTACTO
# ==========================================================

def mostrarContacto(numero):

    dados = contactos[numero]

    print("\n" + "=" * 48)
    print("                 CONTACTO")
    print("=" * 48)

    print(f"Nome: {dados['nome']}")
    print(f"Sexo: {dados['sexo']}")
    print(f"Estado civil: {dados.get('estado_civil', 'Não informado')}")
    print(f"Nascimento: {dados['nascimento']}")

    print(
        f"Idade atual: "
        f"{calcularIdade(dados['nascimento'])} anos"
    )

    print(f"Telemóvel: {numero}")
    print(f"Morada: {dados['morada']}")

    print(
        f"Email: {dados['email'] or 'Não informado'}"
    )

    print(
        f"Notas: {dados['notas'] or 'Sem notas'}"
    )

    print(f"Criado em: {dados['criado']}")

    print("=" * 48)


# ==========================================================
# LISTA COMPLETA
# ==========================================================

def listaCompleta():

    if not contactos:
        print("\nNão existem contactos.")
        return

    lista = sorted(
        contactos.keys(),
        key=lambda numero: normalizar(contactos[numero]["nome"])
    )

    print("\n" + "=" * 145)
    print("LISTA COMPLETA DE CONTACTOS")
    print("=" * 145)

    print(
        f"{'Nº':<5}"
        f"{'NOME':<22}"
        f"{'SEXO':<11}"
        f"{'ESTADO CIVIL':<17}"
        f"{'TELEMÓVEL':<16}"
        f"{'IDADE':<8}"
        f"{'EMAIL':<24}"
        f"{'MORADA':<25}"
    )
    print("-" * 145)

    for indice, numero in enumerate(lista, 1):
        dados = contactos[numero]
        nome = dados["nome"][:20]
        sexo = dados["sexo"][:9]
        estado = dados.get("estado_civil", "Não informado")[:15]
        telefone = numero[:14]
        idade = str(calcularIdade(dados["nascimento"]))
        email = (dados["email"] or "-")[:22]
        morada = dados["morada"][:23]

        print(
            f"{indice:<5}"
            f"{nome:<22}"
            f"{sexo:<11}"
            f"{estado:<17}"
            f"{telefone:<16}"
            f"{idade:<8}"
            f"{email:<24}"
            f"{morada:<25}"
        )

    print("-" * 145)
    print(f"\nTotal: {len(contactos)} contacto(s).")
    print("\nDigite o número do contacto para consultar.")
    print("0 - Voltar")

    while True:
        escolha = input("\nEscolha: ").strip()

        if escolha == "0":
            return

        if escolha.isdigit():
            indice = int(escolha)

            if 1 <= indice <= len(lista):
                numero = lista[indice - 1]
                mostrarContacto(numero)

                print("\n1 - Editar este contacto")
                print("0 - Voltar")
                opcao = input("\nEscolha: ").strip()

                if opcao == "1":
                    editarContacto(numero)
                return

        print("Opção inválida!")


# ==========================================================
# ADICIONAR CONTACTO
# ==========================================================

def adicionarContacto():

    print("\n========== ADICIONAR CONTACTO ==========")

    nome = pedirNome()

    sexo = pedirSexo()

    estado_civil = pedirEstadoCivil()

    while True:

        numero = pedirTelemovel()

        duplicado = any(
            numeroNormalizado(n) == numeroNormalizado(numero)
            for n in contactos
        )

        if not duplicado:
            break

        print("Informação incorreta, digite novamente:")

    nascimento = pedirNascimento()

    morada = pedirMorada()

    email = pedirEmail()

    notas = pedirNotas()

    contactos[numero] = {

        "nome": nome,

        "sexo": sexo,

        "estado_civil": estado_civil,

        "nascimento": nascimento,

        "morada": morada,

        "email": email,

        "notas": notas,

        "criado": datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    }

    guardarContactos()

    print("\nContacto adicionado com sucesso!")


# ==========================================================
# PESQUISA UNIVERSAL
# ==========================================================

def procurarContactos():

    if not contactos:

        print("\nNão existem contactos para pesquisar.")
        return []

    pesquisa = input(
        "\nPesquise por nome, sexo, estado civil, idade, nascimento, "
        "telemóvel, morada, email ou notas: "
    ).strip()

    pesquisa = normalizar(pesquisa)

    if not pesquisa:

        print("Pesquisa vazia!")
        return []

    termos = pesquisa.split()

    exactos = []
    parciais = []
    semelhantes = []

    for numero, dados in contactos.items():

        idade = str(
            calcularIdade(dados["nascimento"])
        )

        campos = [

            numero,

            dados["nome"],

            dados["sexo"],

            dados.get("estado_civil", "Não informado"),

            dados["nascimento"],

            dados["morada"],

            dados["email"],

            dados["notas"],

            idade
        ]

        campos = [
            normalizar(campo)
            for campo in campos
            if campo
        ]

        texto_completo = " ".join(campos)

        # Correspondência exata

        if pesquisa in campos:

            exactos.append(numero)

        # Correspondência parcial

        elif all(
            termo in texto_completo
            for termo in termos
        ):

            parciais.append(numero)

        # Correspondência aproximada

        else:

            pontuacao = max(
                SequenceMatcher(
                    None, pesquisa, campo
                ).ratio()
                for campo in campos
            )

            if pontuacao >= 0.60:

                semelhantes.append(
                    (numero, pontuacao)
                )

    if exactos:

        resultados = exactos

        print("\nCorrespondências encontradas:")

    elif parciais:

        resultados = parciais

        print("\nCorrespondências encontradas:")

    elif semelhantes:

        semelhantes.sort(
            key=lambda item: item[1],
            reverse=True
        )

        sugestoes = semelhantes[:5]

        resultados = [
            numero for numero, _ in sugestoes
        ]

        print("\nVocê quis dizer?")

        for indice, (numero, pontuacao) in enumerate(
            sugestoes, 1
        ):

            print(
                f"{indice} - {contactos[numero]['nome']} "
                f"| {numero} | {pontuacao:.0%} semelhante"
            )

    else:

        print("\nNenhum contacto encontrado.")

        return []

    if exactos or parciais:

        for indice, numero in enumerate(
            resultados, 1
        ):

            dados = contactos[numero]

            print(
                f"{indice} - {dados['nome']} "
                f"| {dados['sexo']} "
                f"| {numero} "
                f"| {calcularIdade(dados['nascimento'])} anos"
            )

    return resultados


# ==========================================================
# SELECIONAR CONTACTO
# ==========================================================

def selecionarContacto(resultados):

    if not resultados:
        return None

    while True:

        escolha = input(
            "\nEscolha o contacto (0 para voltar): "
        ).strip()

        if escolha == "0":
            return None

        if escolha.isdigit():

            indice = int(escolha)

            if 1 <= indice <= len(resultados):

                return resultados[indice - 1]

        print("Opção inválida!")


# ==========================================================
# CONSULTAR CONTACTO
# ==========================================================

def consultarContacto():

    resultados = procurarContactos()
    numero = selecionarContacto(resultados)

    if numero is not None:
        mostrarContacto(numero)

        print("\n1 - Editar este contacto")
        print("0 - Voltar")
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            editarContacto(numero)


# ==========================================================
# EDITAR CONTACTO
# ==========================================================

def editarContacto(numero_selecionado=None):

    print("\n========== EDITAR CONTACTO ==========")

    if numero_selecionado is None:
        resultados = procurarContactos()
        numero = selecionarContacto(resultados)

        if numero is None:
            return
    else:
        numero = numero_selecionado

    mostrarContacto(numero)

    while True:

        print("\nO que pretende alterar?")

        print("1 - Nome")
        print("2 - Sexo")
        print("3 - Estado civil")
        print("4 - Nascimento")
        print("5 - Telemóvel")
        print("6 - Morada")
        print("7 - Email")
        print("8 - Notas")
        print("0 - Terminar edição")

        opcao = input("\nEscolha: ").strip()

        dados = contactos[numero]

        if opcao == "1":

            dados["nome"] = pedirNome()

        elif opcao == "2":

            dados["sexo"] = pedirSexo()

        elif opcao == "3":

            dados["estado_civil"] = pedirEstadoCivil()

        elif opcao == "4":

            dados["nascimento"] = pedirNascimento()

        elif opcao == "5":

            while True:

                novo_numero = pedirTelemovel()

                duplicado = any(
                    numeroNormalizado(n) ==
                    numeroNormalizado(novo_numero)
                    and n != numero
                    for n in contactos
                )

                if not duplicado:
                    break

                print(
                    "Informação incorreta, digite novamente:"
                )

            dados_contacto = contactos.pop(numero)

            contactos[novo_numero] = dados_contacto

            numero = novo_numero

        elif opcao == "6":

            dados["morada"] = pedirMorada()

        elif opcao == "7":

            dados["email"] = pedirEmail()

        elif opcao == "8":

            dados["notas"] = pedirNotas()

        elif opcao == "0":

            print("\nEdição terminada.")
            return

        else:

            print("Opção inválida!")
            continue

        guardarContactos()

        print("Alteração guardada com sucesso!")


# ==========================================================
# REMOVER CONTACTO
# ==========================================================

def removerContacto():

    print("\n========== REMOVER CONTACTO ==========")

    resultados = procurarContactos()

    numero = selecionarContacto(resultados)

    if numero is None:
        return

    mostrarContacto(numero)

    confirmacao = input(
        "\nTem a certeza de que pretende eliminar "
        "este contacto? (S/N): "
    ).strip().casefold()

    if confirmacao == "s":

        del contactos[numero]

        guardarContactos()

        print("\nContacto eliminado com sucesso!")

    else:

        print("\nEliminação cancelada.")


# ==========================================================
# ESTATISTICAS
# ==========================================================

def estatisticas():

    if not contactos:

        print("\nNão existem contactos.")
        return

    idades = {

        numero: calcularIdade(dados["nascimento"])

        for numero, dados in contactos.items()
    }

    idade_media = sum(
        idades.values()
    ) / len(idades)

    mais_velho = max(
        idades, key=idades.get
    )

    mais_novo = min(
        idades, key=idades.get
    )

    print("\n" + "=" * 48)
    print("                 ESTATÍSTICAS")
    print("=" * 48)

    # ESTATISTICAS GERAIS

    print("\n--- GERAL ---")

    print(f"Total de contactos: {len(contactos)}")

    print(f"Idade média: {idade_media:.1f} anos")

    print(
        f"Contacto mais velho: "
        f"{contactos[mais_velho]['nome']} "
        f"({idades[mais_velho]} anos)"
    )

    print(
        f"Contacto mais novo: "
        f"{contactos[mais_novo]['nome']} "
        f"({idades[mais_novo]} anos)"
    )

    # DISTRIBUICAO POR SEXO

    homens = sum(
        1 for dados in contactos.values()
        if dados["sexo"] == "Homem"
    )

    mulheres = sum(
        1 for dados in contactos.values()
        if dados["sexo"] == "Mulher"
    )

    nao_informado = len(contactos) - homens - mulheres

    print("\n--- DISTRIBUIÇÃO POR SEXO ---")

    print(
        f"Homens: {homens} "
        f"({homens / len(contactos) * 100:.1f}%)"
    )

    print(
        f"Mulheres: {mulheres} "
        f"({mulheres / len(contactos) * 100:.1f}%)"
    )

    if nao_informado:

        print(f"Não informado: {nao_informado}")

    # DISTRIBUICAO POR FAIXA ETARIA

    criancas = 0
    adolescentes = 0
    adultos = 0
    idosos = 0

    for idade in idades.values():

        if 0 <= idade <= 12:
            criancas += 1

        elif 13 <= idade <= 17:
            adolescentes += 1

        elif 18 <= idade <= 59:
            adultos += 1

        elif idade >= 60:
            idosos += 1

    print("\n--- DISTRIBUIÇÃO POR FAIXA ETÁRIA ---")

    print(f"Crianças (0-12 anos): {criancas}")

    print(f"Adolescentes (13-17 anos): {adolescentes}")

    print(f"Adultos (18-59 anos): {adultos}")

    print(f"Idosos (60+ anos): {idosos}")

    print("\n" + "=" * 48)


# ==========================================================
# ANIVERSARIANTES DO MES
# ==========================================================

def aniversariantesDoMes():
    hoje = datetime.now()

    print("\n--- ANIVERSARIANTES DO MÊS ---")
    print("1 - Mês atual")
    print("2 - Escolher outro mês")

    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == "1":
        mes = hoje.month
    elif opcao == "2":
        try:
            mes = int(input("Indique o número do mês (1-12): "))
            if mes < 1 or mes > 12:
                print("Mês inválido.")
                return
        except ValueError:
            print("Introduza um número válido.")
            return
    else:
        print("Opção inválida.")
        return

    if not contactos:
        print("\nNão existem contactos guardados.")
        return

    aniversariantes = []

    for numero, contacto in contactos.items():
        try:
            # No resto do programa, o campo chama-se 'nascimento'.
            data = datetime.strptime(contacto["nascimento"], "%d/%m/%Y")
            if data.month == mes:
                aniversariantes.append((data.day, contacto["nome"], numero))
        except (ValueError, KeyError, TypeError):
            continue

    aniversariantes.sort(key=lambda item: (item[0], normalizar(item[1])))

    print(f"\nMês: {MESES[mes]}")
    print(f"Total de aniversariantes: {len(aniversariantes)}")

    if not aniversariantes:
        print("Não existem aniversariantes neste mês.")
        return

    print("\nAniversariantes:")
    for dia, nome, numero in aniversariantes:
        print(f"Dia {dia:02d} — {nome} ({numero})")


# ==========================================================
# EXPORTAR CONTACTOS PARA EXCEL
# ==========================================================

def exportarContactos():

    if not contactos:

        print("\nNão existem contactos para exportar.")

        return

    try:

        with open(
            EXPORTACAO,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as ficheiro:

            campos = [

                "Nome",
                "Sexo",
                "Estado civil",
                "Nascimento",
                "Idade",
                "Telemóvel",
                "Morada",
                "Email",
                "Notas",
                "Criado em"
            ]

            escritor = csv.DictWriter(
                ficheiro,
                fieldnames=campos,
                delimiter=";"
            )

            escritor.writeheader()

            for numero, dados in contactos.items():

                escritor.writerow({

                    "Nome": dados["nome"],

                    "Sexo": dados["sexo"],

                    "Estado civil": dados.get("estado_civil", "Não informado"),

                    "Nascimento": dados["nascimento"],

                    "Idade": calcularIdade(
                        dados["nascimento"]
                    ),

                    "Telemóvel": numero,

                    "Morada": dados["morada"],

                    "Email": dados["email"],

                    "Notas": dados["notas"],

                    "Criado em": dados["criado"]
                })

        print(
            f"\nExportação concluída: "
            f"{EXPORTACAO.name}"
        )

        print(f"Local: {EXPORTACAO}")

    except OSError as erro:

        print(f"Erro ao exportar: {erro}")


# ==========================================================
# MENU PRINCIPAL
# ==========================================================

def menuPrincipal():

    carregarContactos()

    while True:

        print("\n" + "=" * 46)

        print("             GESTÃO DE CONTACTOS")

        print("=" * 46)

        print("1 - Consultar contactos")
        print("2 - Adicionar contacto")
        print("3 - Editar contacto")
        print("4 - Remover contacto")
        print("5 - Lista completa")
        print("6 - Estatísticas")
        print("7 - Exportar contactos")
        print("8 - Aniversariantes do mês")
        print("0 - Sair")

        print("=" * 46)

        opcao = input(
            "Escolha uma opção: "
        ).strip()

        if opcao == "1":

            consultarContacto()

        elif opcao == "2":

            adicionarContacto()

        elif opcao == "3":

            editarContacto()

        elif opcao == "4":

            removerContacto()

        elif opcao == "5":

            listaCompleta()

        elif opcao == "6":

            estatisticas()

        elif opcao == "7":

            exportarContactos()

        elif opcao == "8":

            aniversariantesDoMes()

        elif opcao == "0":

            print("\nPrograma terminado.")

            break

        else:

            print("\nOpção inválida!")


# ==========================================================
# EXECUTAR PROGRAMA
# ==========================================================

if __name__ == "__main__":

    menuPrincipal()
