"""Contrato puro da dupla leitura cega; votos e IDs permanecem privados."""

import hashlib
import json
import re
from collections import Counter

CODEBOOK = 'onda5r_falhas_v1'
MOTIVOS = ('sem_pedido_identificavel', 'vinculo_incerto',
           'conteudo_insuficiente', 'autoria_incerta')
FALHAS = ('sim', 'nao', 'indeterminado')
SUBTIPOS = ('nao_responde_ao_pedido', 'repeticao_ou_loop',
            'pedido_de_humano_nao_atendido', 'clarificacao_evitavel', 'outro')
CAMPOS = {'item', 'leitor', 'codebook', 'avaliacao', 'motivo',
          'pedido_referencia', 'falha_observavel', 'subtipo', 'justificativa'}
DECISAO = ('avaliacao', 'motivo', 'pedido_referencia',
           'falha_observavel', 'subtipo')


def validar_voto(voto):
    """Recusa campos de previsão e combinações incompatíveis com o codebook."""
    if set(voto) != CAMPOS:
        raise ValueError('Voto com campos ausentes ou inesperados.')
    if (not isinstance(voto['item'], str) or not voto['item']
            or not isinstance(voto['leitor'], str) or not voto['leitor']
            or voto['codebook'] != CODEBOOK):
        raise ValueError('Identidade ou versão inválida.')
    if voto['avaliacao'] == 'nao_avaliavel':
        if (voto['motivo'] not in MOTIVOS
                or any(voto[c] is not None for c in
                       ('pedido_referencia', 'falha_observavel', 'subtipo'))):
            raise ValueError('Voto não avaliável inconsistente.')
    elif voto['avaliacao'] == 'resposta_avaliavel':
        if (voto['motivo'] is not None
                or not isinstance(voto['pedido_referencia'], str)
                or re.fullmatch(r'M[1-9][0-9]*', voto['pedido_referencia']) is None
                or voto['falha_observavel'] not in FALHAS):
            raise ValueError('Voto avaliável inconsistente.')
        if voto['falha_observavel'] == 'sim':
            if voto['subtipo'] not in SUBTIPOS or not str(voto['justificativa'] or '').strip():
                raise ValueError('Falha sim exige subtipo e justificativa.')
        elif voto['subtipo'] is not None:
            raise ValueError('Subtipo exige falha sim.')
    else:
        raise ValueError('Avaliabilidade inválida.')
    if voto['justificativa'] is not None and not isinstance(voto['justificativa'], str):
        raise ValueError('Justificativa deve ser texto.')
    return True


def _indexar(votos):
    indice = {}
    leitores = set()
    for voto in votos:
        validar_voto(voto)
        if voto['item'] in indice:
            raise ValueError('Voto duplicado para um item.')
        indice[voto['item']] = voto
        leitores.add(voto['leitor'])
    if not indice or len(leitores) != 1:
        raise ValueError('Cada leitura precisa de um único leitor e itens.')
    return indice, leitores.pop()


def conferir_dupla(leitura_a, leitura_b):
    """Retorna apenas contagens e a fila privada de itens em desacordo."""
    a, leitor_a = _indexar(leitura_a)
    b, leitor_b = _indexar(leitura_b)
    if leitor_a == leitor_b or set(a) != set(b):
        raise ValueError('Leitores devem ser distintos e cobrir os mesmos itens.')
    desacordos = sorted(
        item for item in a
        if tuple(a[item][c] for c in DECISAO) != tuple(b[item][c] for c in DECISAO)
    )
    return {'itens': len(a), 'leitores': (leitor_a, leitor_b),
            'acordos': len(a) - len(desacordos),
            'fila_desempate_privada': desacordos}


def snapshot_votos(fila_sha256, leitura_a, leitura_b):
    """Identidade canônica dos votos integrais; relógios não afetam decisões."""
    a, b = list(leitura_a), list(leitura_b)
    conferencia = conferir_dupla(a, b)
    if not isinstance(fila_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', fila_sha256):
        raise ValueError('SHA-256 da fila inválido.')
    identidade = {'versao': 1, 'fila_sha256': fila_sha256, 'codebook': CODEBOOK,
                  'leitores': sorted(conferencia['leitores'])}
    bruto = json.dumps({**identidade, 'votos': sorted(a + b, key=lambda v: (v['leitor'], v['item']))},
                       ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return {**identidade, 'votos_sha256': hashlib.sha256(bruto).hexdigest()}


def fechar_dupla(leitura_a, leitura_b, desempates, *, fila_sha256):
    """Autor escolhe qual voto prevalece em cada desacordo, sem alterar votos."""
    leitura_a, leitura_b = list(leitura_a), list(leitura_b)
    conferencia = conferir_dupla(leitura_a, leitura_b)
    a, _ = _indexar(leitura_a)
    b, _ = _indexar(leitura_b)
    leitor_a, leitor_b = conferencia['leitores']
    divergentes = set(conferencia['fila_desempate_privada'])
    if set(desempates) != divergentes or any(
            escolha not in (leitor_a, leitor_b) for escolha in desempates.values()):
        raise ValueError('Desempates incompletos ou fora da fila.')
    finais = []
    direcao = {leitor_a: 0, leitor_b: 0}
    resultado = {categoria: 0 for categoria in ('nao_avaliavel', *FALHAS)}
    transicoes = Counter()

    def categoria(voto):
        return (voto['falha_observavel'] if voto['avaliacao'] == 'resposta_avaliavel'
                else 'nao_avaliavel')

    for item in sorted(a):
        escolhido = desempates[item] if item in divergentes else leitor_a
        voto = a[item] if escolhido == leitor_a else b[item]
        if item in divergentes:
            direcao[escolhido] += 1
            resultado[categoria(voto)] += 1
            transicoes['|'.join((categoria(a[item]), categoria(b[item]),
                                 categoria(voto)))] += 1
        finais.append({'item': item, **{campo: voto[campo] for campo in DECISAO},
                       'origem': 'desempate_autor' if item in divergentes else 'acordo'})
    return {'snapshot': snapshot_votos(fila_sha256, leitura_a, leitura_b),
            'itens': conferencia['itens'], 'acordos': conferencia['acordos'],
            'desempates': len(divergentes), 'desempates_por_leitor': direcao,
            'desempates_por_resultado': resultado,
            'transicoes_desempate_privadas': dict(transicoes),
            'rotulos_finais_privados': finais}
