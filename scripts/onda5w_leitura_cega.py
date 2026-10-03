"""Leitura humana cega, privada e retomável da amostra por Output."""

import argparse
import copy
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import termios
import time
import tty
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
from pathlib import Path

from scripts.onda5v_dupla_leitura import (
    CODEBOOK,
    FALHAS,
    MOTIVOS,
    SUBTIPOS,
    conferir_dupla,
    fechar_dupla,
    snapshot_votos,
    validar_voto,
)

VERSAO = 1
VERSAO_CHECKPOINT = 2
CHAVES_ITEM = {'item', 'resposta_alvo', 'mensagens'}
CHAVES_MENSAGEM = {'tipo_fonte', 'texto', 'timestamp', 'papel_fonte'}


def _fora_do_git(caminho):
    raiz = Path(__file__).resolve().parents[1]
    resolvido = Path(caminho).resolve()
    if resolvido.is_relative_to(raiz) and not resolvido.is_relative_to(raiz / 'data'):
        raise ValueError('Pacotes e checkpoints privados dentro deste projeto devem ficar em data/.')


def _privado(caminho):
    if caminho.is_symlink() or caminho.stat().st_mode & 0o077:
        raise ValueError(f'Arquivo precisa ser privado (0600): {caminho}')


def _gravar(caminho, conteudo):
    caminho.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descritor, temporario = tempfile.mkstemp(prefix='.onda5w-', dir=caminho.parent)
    try:
        with os.fdopen(descritor, 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
            arquivo.write('\n')
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.chmod(temporario, 0o600)
        os.replace(temporario, caminho)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def _hash_arquivo(caminho):
    if not caminho.exists():
        return None
    _privado(caminho)
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


@contextmanager
def _travar(caminho):
    """Lock estável separado do arquivo substituído atomicamente; liberado na queda."""
    caminho.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = caminho.with_name(caminho.name + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        _privado(lock)
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _conferir_versao(caminho, esperado):
    if _hash_arquivo(caminho) != esperado:
        raise ValueError('Outro processo alterou o checkpoint; reabra para continuar sem perder votos.')


def _conferir_checkpoints_distintos(caminhos):
    """Recusa aliases antes dos locks, inclusive a/A em filesystem do Mac."""
    identidades = set()
    for caminho in caminhos:
        if not caminho.is_file():
            raise ValueError('Checkpoint inexistente; complete a leitura antes de consolidar.')
        _privado(caminho)
        estado = caminho.stat()
        identidade = (estado.st_dev, estado.st_ino)
        if identidade in identidades:
            raise ValueError('Leitores precisam de checkpoints distintos no filesystem.')
        identidades.add(identidade)


def _atualizar(caminho, esperado, estado):
    with _travar(caminho):
        _conferir_versao(caminho, esperado)
        _gravar(caminho, estado)
        return _hash_arquivo(caminho)


def _utc():
    return datetime.now(timezone.utc).isoformat()


def carregar_fila(caminho):
    caminho = Path(caminho)
    _fora_do_git(caminho)
    _privado(caminho)
    bruto = caminho.read_bytes()
    pacote = json.loads(bruto)
    if set(pacote) != {'versao', 'codebook', 'itens'} or pacote['versao'] != VERSAO or pacote['codebook'] != CODEBOOK:
        raise ValueError('Pacote incompatível.')
    itens = pacote['itens']
    if not isinstance(itens, list) or not itens:
        raise ValueError('Fila vazia.')
    ids = set()
    for item in itens:
        if not isinstance(item, dict) or set(item) != CHAVES_ITEM:
            raise ValueError('Item com campo inesperado ou ausente.')
        identificador, alvo, mensagens = item['item'], item['resposta_alvo'], item['mensagens']
        if not isinstance(identificador, str) or not identificador or identificador in ids:
            raise ValueError('ID vazio ou duplicado.')
        ids.add(identificador)
        if not isinstance(mensagens, list) or not isinstance(alvo, int) or isinstance(alvo, bool) or not 1 <= alvo <= len(mensagens):
            raise ValueError('Alvo inválido.')
        for mensagem in mensagens:
            if not isinstance(mensagem, dict) or set(mensagem) != CHAVES_MENSAGEM:
                raise ValueError('Mensagem com campo inesperado ou ausente.')
            if any(not isinstance(valor, str) for valor in mensagem.values()) or mensagem['tipo_fonte'] not in ('Input', 'Output'):
                raise ValueError('Mensagem inválida.')
        if mensagens[alvo - 1]['tipo_fonte'] != 'Output':
            raise ValueError('Alvo não é Output.')
    return itens, hashlib.sha256(bruto).hexdigest()


def referencias(item):
    return {f'M{numero}' for numero, mensagem in enumerate(item['mensagens'][:item['resposta_alvo'] - 1], 1)
            if mensagem['tipo_fonte'] == 'Input'}


def dialogo(item):
    """Texto renderizado: jamais inclui mensagens posteriores ao Output-alvo."""
    linhas = []
    for numero, mensagem in enumerate(item['mensagens'][:item['resposta_alvo']], 1):
        alvo = ' [OUTPUT-ALVO]' if numero == item['resposta_alvo'] else ''
        linhas.append(f"M{numero}{alvo} {mensagem['papel_fonte']}/{mensagem['tipo_fonte']} {mensagem['timestamp']}\n{mensagem['texto']}")
    return '\n\n'.join(linhas)


def _mostrar_dialogo(item, pasta, saida):
    """Mostra prefixos extensos em pager local, sem gravar histórico de buscas."""
    conteudo = dialogo(item)
    if len(conteudo) <= 10000 or not sys.stdin.isatty() or saida is not print:
        saida(conteudo)
        return False
    descritor, temporario = tempfile.mkstemp(prefix='.onda5w-dialogo-', dir=pasta)
    try:
        with os.fdopen(descritor, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
        ambiente = {**os.environ, 'LESS': '', 'LESSOPEN': '', 'LESSCLOSE': '',
                    'LESSHISTFILE': '-', 'LESSSECURE': '1'}
        saida('Contexto extenso: navegue com setas, / busca texto, q volta ao voto.')
        subprocess.run(['less', temporario], check=True, env=ambiente)
    finally:
        os.unlink(temporario)
    return True


def _identidade(nome):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,40}', nome):
        raise ValueError('Use leitor com 1–40 letras, números, _ ou -.')
    return nome


class Leitura:
    def __init__(self, fila, leitor, *, monotonic=time.monotonic):
        self.itens, self.sha = carregar_fila(fila)
        self.leitor = _identidade(leitor)
        self.caminho = Path(fila).with_name(f'leitura_{leitor}.json')
        self.indice = {item['item']: item for item in self.itens}
        self.ordem = sorted(self.indice, key=lambda item: hashlib.sha256(f'{self.sha}:{leitor}:{item}'.encode()).hexdigest())
        self._clock = monotonic
        self._inicio = None
        if self.caminho.exists():
            _privado(self.caminho)
            bruto = self.caminho.read_bytes()
            self._hash = hashlib.sha256(bruto).hexdigest()
            estado = json.loads(bruto)
            if estado.get('versao') == 1:
                raise ValueError('Checkpoint v1: execute migrar FILA --leitor NOME antes de retomar.')
        else:
            self._hash = None
            estado = {'versao': VERSAO_CHECKPOINT, 'fila_sha256': self.sha,
                      'codebook': CODEBOOK, 'leitor': leitor, 'votos': {},
                      'registro': {}, 'historico': [], 'tempos': []}
        self._validar_estado(estado)
        self._estado = estado

    @property
    def votos(self):
        return copy.deepcopy(self._estado['votos'])

    @property
    def registro(self):
        return copy.deepcopy(self._estado['registro'])

    def _validar_estado(self, estado):
        if (set(estado) != {'versao', 'fila_sha256', 'codebook', 'leitor', 'votos',
                           'registro', 'historico', 'tempos'}
                or estado['versao'] != VERSAO_CHECKPOINT or estado['codebook'] != CODEBOOK
                or estado['fila_sha256'] != self.sha or estado['leitor'] != self.leitor
                or not isinstance(estado['votos'], dict)):
            raise ValueError('Checkpoint não corresponde à fila e ao leitor.')
        if (not isinstance(estado['registro'], dict)
                or set(estado['registro']) != set(estado['votos'])
                or any(not isinstance(meta, dict) or set(meta) != {'data_utc', 'modo'}
                       or meta['modo'] != 'individual' or not isinstance(meta['data_utc'], str)
                       for meta in estado['registro'].values())):
            raise ValueError('Proveniência do checkpoint inválida.')
        if not set(estado['votos']) <= set(self.indice):
            raise ValueError('Checkpoint contém item desconhecido.')
        for item, voto in estado['votos'].items():
            self._validar(item, voto)
        if not isinstance(estado['historico'], list) or not isinstance(estado['tempos'], list):
            raise TypeError('Histórico ou tempos inválidos.')
        reconstruidos = {}
        for evento in estado['historico']:
            if (set(evento) != {'voto', 'data_utc', 'origem'}
                    or evento['origem'] not in ('individual', 'migracao_v1')
                    or not isinstance(evento['data_utc'], str)):
                raise ValueError('Evento de voto inválido.')
            voto = evento['voto']
            self._validar(voto['item'], voto)
            reconstruidos[voto['item']] = voto
        if reconstruidos != estado['votos']:
            raise ValueError('Histórico não reconcilia com votos atuais.')
        for segmento in estado['tempos']:
            if (set(segmento) != {'item', 'modo', 'inicio_utc', 'fim_utc', 'segundos', 'estado'}
                    or segmento['item'] not in self.indice
                    or segmento['modo'] not in ('primeira_leitura', 'revisao', 'pausa')
                    or segmento['estado'] not in ('aberto', 'concluido', 'interrompido')
                    or not isinstance(segmento['inicio_utc'], str)
                    or (segmento['estado'] == 'concluido' and (
                        not isinstance(segmento['fim_utc'], str)
                        or type(segmento['segundos']) not in (int, float)
                        or not 0 <= segmento['segundos'] < float('inf')))
                    or (segmento['estado'] != 'concluido' and (
                        segmento['fim_utc'] is not None or segmento['segundos'] is not None))):
                raise ValueError('Segmento de tempo inválido.')
        abertos = [n for n, s in enumerate(estado['tempos']) if s['estado'] == 'aberto']
        if abertos and abertos != [len(estado['tempos']) - 1]:
            raise ValueError('Segmento aberto fora do final.')

    def _validar(self, item, voto):
        validar_voto(voto)
        if item not in self.indice or voto['item'] != item or voto['leitor'] != self.leitor:
            raise ValueError('Voto pertence a outro item ou leitor.')
        if voto['avaliacao'] == 'resposta_avaliavel' and voto['pedido_referencia'] not in referencias(self.indice[item]):
            raise ValueError('Referência não aponta a Input anterior.')

    def _salvar(self, estado):
        self._validar_estado(estado)
        novo_hash = _atualizar(self.caminho, self._hash, estado)
        self._estado, self._hash = estado, novo_hash

    def _terminar_segmento(self, estado):
        if estado['tempos'] and estado['tempos'][-1]['estado'] == 'aberto':
            segmento = estado['tempos'][-1]
            if self._inicio is None:
                segmento['estado'] = 'interrompido'
            else:
                segmento.update(estado='concluido', fim_utc=_utc(),
                                segundos=max(0., self._clock() - self._inicio))

    def iniciar(self, item, *, pausa=False):
        if item not in self.indice:
            raise ValueError('Item desconhecido.')
        estado = copy.deepcopy(self._estado)
        self._terminar_segmento(estado)
        inicio = self._clock()
        estado['tempos'].append({'item': item,
                                 'modo': 'pausa' if pausa else ('revisao' if item in self.votos else 'primeira_leitura'),
                                 'inicio_utc': _utc(), 'fim_utc': None,
                                 'segundos': None, 'estado': 'aberto'})
        self._salvar(estado)
        self._inicio = inicio

    def encerrar(self):
        estado = copy.deepcopy(self._estado)
        self._terminar_segmento(estado)
        if estado != self._estado:
            self._salvar(estado)
        self._inicio = None

    def registrar(self, item, voto):
        if item not in self.indice:
            raise ValueError('Item desconhecido.')
        self._validar(item, voto)
        estado = copy.deepcopy(self._estado)
        self._terminar_segmento(estado)
        agora = _utc()
        estado['votos'][item] = copy.deepcopy(voto)
        estado['registro'][item] = {'data_utc': agora, 'modo': 'individual'}
        estado['historico'].append({'voto': copy.deepcopy(voto), 'data_utc': agora,
                                    'origem': 'individual'})
        self._salvar(estado)
        self._inicio = None


def migrar(fila, leitor):
    """Migração explícita v1→v2, preservando bytes v1; nunca inventa durações."""
    itens, sha = carregar_fila(fila)
    caminho = Path(fila).with_name(f'leitura_{_identidade(leitor)}.json')
    with _travar(caminho):
        _privado(caminho)
        bruto = caminho.read_bytes()
        estado = json.loads(bruto)
        if estado.get('versao') == VERSAO_CHECKPOINT:
            Leitura(fila, leitor)
            return caminho
        if (set(estado) != {'versao', 'fila_sha256', 'leitor', 'votos', 'registro'}
                or estado['versao'] != 1 or estado['fila_sha256'] != sha
                or estado['leitor'] != leitor or not isinstance(estado['votos'], dict)):
            raise ValueError('Checkpoint v1 incompatível; migração recusada.')
        novo = {**estado, 'versao': VERSAO_CHECKPOINT, 'codebook': CODEBOOK,
                'historico': [{'voto': voto, 'data_utc': estado['registro'][item]['data_utc'],
                               'origem': 'migracao_v1'} for item, voto in estado['votos'].items()],
                'tempos': []}
        validador = object.__new__(Leitura)
        validador.leitor, validador.sha = leitor, sha
        validador.indice = {i['item']: i for i in itens}
        validador._validar_estado(novo)
        backup = caminho.with_name(caminho.name + '.v1.bak')
        if backup.exists():
            _privado(backup)
            if backup.read_bytes() != bruto:
                raise ValueError('Backup v1 diferente; migração recusada.')
        else:
            fd = os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, 'wb') as arquivo:
                arquivo.write(bruto)
                arquivo.flush()
                os.fsync(arquivo.fileno())
        _gravar(caminho, novo)
    return caminho


def resumir_tempos(leitura):
    """Totais de segmentos confirmados; períodos perdidos continuam desconhecidos."""
    soma = {modo: 0. for modo in ('primeira_leitura', 'revisao', 'pausa')}
    desconhecidos = 0
    for segmento in leitura._estado['tempos']:
        if segmento['estado'] == 'concluido':
            soma[segmento['modo']] += segmento['segundos']
        else:
            desconhecidos += 1
    return {'versao': 1, 'segundos_por_modo': soma,
            'ativo_confirmado_segundos': soma['primeira_leitura'] + soma['revisao'],
            'decorrido_observado_segundos': sum(soma.values()),
            'segmentos_duracao_desconhecida': desconhecidos,
            'votos_anteriores_sem_tempo': sum(e['origem'] == 'migracao_v1'
                                             for e in leitura._estado['historico'])}


def _comando(pergunta, entrada):
    """No terminal interativo, lê uma tecla; em testes/pipe, lê uma linha."""
    if entrada is not input or not sys.stdin.isatty():
        return entrada(pergunta).strip().lower()
    descritor = sys.stdin.fileno()
    anterior = termios.tcgetattr(descritor)
    try:
        tty.setcbreak(descritor)
        print(pergunta, end='', flush=True)
        tecla = sys.stdin.read(1)
    finally:
        termios.tcsetattr(descritor, termios.TCSADRAIN, anterior)
    print(tecla if tecla not in ('\r', '\n') else '', flush=True)
    return tecla.strip().lower()


def _escolher(pergunta, opcoes, entrada, saida):
    for numero, opcao in enumerate(opcoes, 1):
        saida(f'  {numero}. {opcao}')
    while True:
        resposta = _comando(f'{pergunta} (1–{len(opcoes)}, Enter cancela): ', entrada)
        if not resposta:
            return None
        if resposta.isdecimal() and 1 <= int(resposta) <= len(opcoes):
            return opcoes[int(resposta) - 1]
        saida('Opção inválida.')


def colher_voto(item, leitor, entrada=input, saida=print):
    escolha = _escolher('Avaliabilidade', ('resposta_avaliavel', 'nao_avaliavel'), entrada, saida)
    if escolha is None:
        return None
    voto = {'item': item['item'], 'leitor': leitor, 'codebook': CODEBOOK,
            'avaliacao': escolha, 'motivo': None, 'pedido_referencia': None,
            'falha_observavel': None, 'subtipo': None, 'justificativa': None}
    if escolha == 'nao_avaliavel':
        voto['motivo'] = _escolher('Motivo', MOTIVOS, entrada, saida)
        if voto['motivo'] is None:
            return None
    else:
        permitidas = sorted(referencias(item), key=lambda x: int(x[1:]))
        if not permitidas:
            saida('Sem Input anterior: marque não avaliável.')
            return None
        while True:
            resposta = entrada(f'Referência do pedido ({", ".join(permitidas)}; M opcional; Enter cancela): ').strip().upper()
            if not resposta:
                return None
            referencia = f'M{resposta}' if re.fullmatch(r'[1-9][0-9]*', resposta) else resposta
            if referencia in permitidas:
                voto['pedido_referencia'] = referencia
                break
            saida('Referência inválida; digite o número completo, como 10 ou M10.')
        voto['falha_observavel'] = _escolher('Falha observável', FALHAS, entrada, saida)
        if voto['falha_observavel'] is None:
            return None
        if voto['falha_observavel'] == 'sim':
            voto['subtipo'] = _escolher('Subtipo', SUBTIPOS, entrada, saida)
            if voto['subtipo'] is None:
                return None
            voto['justificativa'] = entrada('Justificativa curta, sem identificadores: ').strip()
            if not voto['justificativa']:
                saida('Justificativa obrigatória; voto cancelado.')
                return None
    validar_voto(voto)
    return voto


def ler(fila, leitor, entrada=input, saida=print):
    leitura = Leitura(fila, leitor)
    posicao = next((n for n, item in enumerate(leitura.ordem) if item not in leitura.votos), 0)
    while True:
        item_id = leitura.ordem[posicao]
        item = leitura.indice[item_id]
        leitura.iniciar(item_id)
        saida(f'\nLEITURA CEGA {posicao + 1}/{len(leitura.ordem)} | completos {len(leitura.votos)}/{len(leitura.ordem)} | {item_id}')
        paginado = _mostrar_dialogo(item, Path(fila).parent, saida)
        if item_id in leitura.votos:
            saida('Voto salvo: ' + json.dumps(leitura.votos[item_id], ensure_ascii=False))
        while True:
            menu = '[v]er novamente ' if paginado else ''
            comando = _comando(menu + '[r]otular/revisar [n]ext [p]révio [g]próximo pendente [s]pausa [q]sair (tecla direta): ', entrada)
            if comando == 'v' and paginado:
                _mostrar_dialogo(item, Path(fila).parent, saida)
                continue
            break
        if comando == 's':
            leitura.iniciar(item_id, pausa=True)
            while True:
                comando = _comando('PAUSADO: [s]retomar [q]sair: ', entrada)
                if comando in ('s', 'q'):
                    break
            if comando == 's':
                continue
        if comando == 'q':
            leitura.encerrar()
            return leitura
        if comando == 'r':
            voto = colher_voto(item, leitor, entrada, saida)
            if voto is not None:
                leitura.registrar(item_id, voto)
                saida('Voto salvo.')
                if len(leitura.votos) < len(leitura.ordem):
                    posicao = next((n for n, nome in enumerate(leitura.ordem) if nome not in leitura.votos), posicao)
        elif comando == 'n':
            posicao = (posicao + 1) % len(leitura.ordem)
        elif comando == 'p':
            posicao = (posicao - 1) % len(leitura.ordem)
        elif comando == 'g':
            posicao = next((n for n, nome in enumerate(leitura.ordem) if nome not in leitura.votos), posicao)


def _leitura_completa(fila, leitor):
    leitura = Leitura(fila, leitor)
    if set(leitura.votos) != set(leitura.indice):
        raise ValueError(f'Leitura {leitor} incompleta: {len(leitura.votos)}/{len(leitura.indice)}.')
    return leitura


def snapshot_leituras(fila, leitor_a, leitor_b):
    """Releia os checkpoints atuais para validar um resultado antes de analisar."""
    _fora_do_git(Path(fila))
    caminhos = [Path(fila).with_name(f'leitura_{_identidade(leitor)}.json')
                for leitor in (leitor_a, leitor_b)]
    if leitor_a == leitor_b:
        raise ValueError('Leitores devem ser distintos.')
    _conferir_checkpoints_distintos(caminhos)
    with ExitStack() as pilha:
        for caminho in sorted(caminhos):
            pilha.enter_context(_travar(caminho))
        a, b = _leitura_completa(fila, leitor_a), _leitura_completa(fila, leitor_b)
        return snapshot_votos(a.sha, a.votos.values(), b.votos.values())


def desempatar(fila, leitor_a, leitor_b, entrada=input, saida=print):
    a, b = _leitura_completa(fila, leitor_a), _leitura_completa(fila, leitor_b)
    if a.sha != b.sha:
        raise ValueError('Filas diferentes.')
    snapshot = snapshot_votos(a.sha, a.votos.values(), b.votos.values())
    conferencia = conferir_dupla(a.votos.values(), b.votos.values())
    caminho = Path(fila).with_name('desempates.json')
    finais = Path(fila).with_name('rotulos_finais.json')
    # Ler bytes uma só vez mantém conteúdo e versão esperada consistentes.
    def existente(arquivo):
        if not arquivo.exists():
            return None, None
        _privado(arquivo)
        bruto = arquivo.read_bytes()
        return json.loads(bruto), hashlib.sha256(bruto).hexdigest()

    anterior, hash_escolhas = existente(caminho)
    anterior_final, hash_final = existente(finais)
    historico = []
    escolhas = {}
    if anterior is not None:
        if (anterior.get('versao') == VERSAO_CHECKPOINT
                and anterior.get('snapshot') == snapshot
                and anterior.get('leitores') == [leitor_a, leitor_b]):
            escolhas = anterior['escolhas']
            historico = anterior['historico']
        else:
            historico = [anterior]
            saida('Votos, leitores ou versão mudaram: desempates anteriores preservados no histórico; novo fechamento obrigatório.')
    divergentes = conferencia['fila_desempate_privada']
    if not isinstance(escolhas, dict) or not set(escolhas) <= set(divergentes) or any(v not in (leitor_a, leitor_b) for v in escolhas.values()):
        raise ValueError('Desempate salvo inválido.')

    def salvar(novas, resultado=None):
        nonlocal hash_escolhas, hash_final
        # A leitura pode ser revisada enquanto o autor decide; recusar esse snapshot.
        with ExitStack() as pilha:
            for arquivo in sorted((a.caminho, b.caminho, caminho, finais)):
                pilha.enter_context(_travar(arquivo))
            _conferir_versao(a.caminho, a._hash)
            _conferir_versao(b.caminho, b._hash)
            _conferir_versao(caminho, hash_escolhas)
            _conferir_versao(finais, hash_final)
            estado = {'versao': VERSAO_CHECKPOINT, 'snapshot': snapshot,
                      'leitores': [leitor_a, leitor_b], 'escolhas': novas,
                      'historico': historico}
            _gravar(caminho, estado)
            hash_escolhas = _hash_arquivo(caminho)
            if resultado is not None:
                # Resultados antigos sobrevivem a novo fechamento, com sua identidade.
                hist_final = [] if anterior_final is None else [anterior_final]
                if (anterior_final and anterior_final.get('snapshot') == snapshot
                        and anterior_final.get('resultado') == resultado
                        and anterior_final.get('leitores') == [leitor_a, leitor_b]):
                    hist_final = anterior_final.get('historico', [])
                _gravar(finais, {'versao': VERSAO_CHECKPOINT, 'snapshot': snapshot,
                                'leitores': [leitor_a, leitor_b], 'resultado': resultado,
                                'historico': hist_final})
                hash_final = _hash_arquivo(finais)

    for item_id in divergentes:
        if item_id in escolhas:
            continue
        saida('\n' + dialogo(a.indice[item_id]))
        saida(f'{leitor_a}: {json.dumps(a.votos[item_id], ensure_ascii=False)}')
        saida(f'{leitor_b}: {json.dumps(b.votos[item_id], ensure_ascii=False)}')
        escolha = _escolher('Voto que prevalece', (leitor_a, leitor_b), entrada, saida)
        if escolha is None:
            return None
        novas = {**escolhas, item_id: escolha}
        salvar(novas)
        escolhas = novas
    resultado = fechar_dupla(a.votos.values(), b.votos.values(), escolhas, fila_sha256=a.sha)
    salvar(escolhas, resultado)
    saida(f"Concluído: {resultado['itens']} itens, {resultado['acordos']} acordos, {resultado['desempates']} desempates.")
    return resultado


def criar_demo(pasta):
    pasta = Path(pasta)
    _fora_do_git(pasta)
    pasta.mkdir(mode=0o700, parents=True, exist_ok=True)
    itens = []
    for nome, pedido, resposta in (
        ('demo-1', 'Como consulto o benefício?', 'Veja os canais oficiais de consulta.'),
        ('demo-2', 'Quero falar com uma pessoa.', 'Sobre qual programa você quer saber?'),
        ('demo-3', 'Qual é o horário?', 'Preciso de mais detalhes sobre sua dúvida.'),
    ):
        mensagens = [
            {'tipo_fonte': 'Input', 'texto': pedido, 'timestamp': '2026-01-01T10:00:00Z', 'papel_fonte': 'USER'},
            {'tipo_fonte': 'Output', 'texto': resposta, 'timestamp': '2026-01-01T10:00:01Z', 'papel_fonte': 'AGENT'},
            {'tipo_fonte': 'Input', 'texto': 'MENSAGEM POSTERIOR OCULTA', 'timestamp': '2026-01-01T10:00:02Z', 'papel_fonte': 'USER'},
        ]
        itens.append({'item': nome, 'resposta_alvo': 2, 'mensagens': mensagens})
    caminho = pasta / 'fila_sintetica.json'
    pacote = {'versao': VERSAO, 'codebook': CODEBOOK, 'itens': itens}
    if caminho.exists():
        _privado(caminho)
        if json.loads(caminho.read_text(encoding='utf-8')) != pacote:
            raise FileExistsError('Demo existente é diferente; use outra pasta para preservar os checkpoints.')
        return caminho
    _gravar(caminho, pacote)
    return caminho


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='acao', required=True)
    demo = sub.add_parser('demo', help='criar pacote totalmente sintético')
    demo.add_argument('pasta', type=Path)
    leitura = sub.add_parser('ler', help='votar sem ver modelo nem outro leitor')
    leitura.add_argument('fila', type=Path)
    leitura.add_argument('--leitor', required=True)
    mig = sub.add_parser('migrar', help='migrar checkpoint v1 com backup privado')
    mig.add_argument('fila', type=Path)
    mig.add_argument('--leitor', required=True)
    des = sub.add_parser('desempatar', help='conferir e decidir divergências após duas leituras completas')
    des.add_argument('fila', type=Path)
    des.add_argument('--leitor-a', required=True)
    des.add_argument('--leitor-b', required=True)
    args = parser.parse_args()
    if args.acao == 'demo':
        print(criar_demo(args.pasta))
    elif args.acao == 'migrar':
        print(migrar(args.fila, args.leitor))
    elif args.acao == 'ler':
        ler(args.fila, args.leitor)
    else:
        desempatar(args.fila, args.leitor_a, args.leitor_b)


if __name__ == '__main__':
    main()
