# Política de segurança

## Escopo

Este é um projeto educacional de portfólio. Ele não deve receber dados pessoais reais. CPF, nome completo e data de nascimento são tratados como informações sensíveis mesmo em ambientes de demonstração.

O auto cadastro público existe somente para a demonstração sintética. Contas criadas pela interface recebem exatamente `pessoas.view_pessoa`; não são staff ou superusuários e não podem cadastrar, editar, excluir, exportar ou acessar o admin. Além disso, leitores enxergam somente os 50 identificadores demo canônicos; uma marcação arbitrária não torna um registro público.

## Relato de vulnerabilidades

Não publique detalhes exploráveis em uma issue aberta. Use um GitHub Security Advisory privado no repositório para descrever o impacto, os passos mínimos de reprodução e a versão afetada.

## Controles adotados

- autenticação e permissões de modelo;
- privilégio mínimo e isolamento técnico dos registros demo;
- limitação distribuída de tentativas de signup e campo honeypot;
- mascaramento e validação de CPF;
- proteção CSRF e cookies seguros;
- HTTPS, HSTS, CSP, SRI e headers restritivos;
- ausência de segredos e bancos no Git;
- PostgreSQL com TLS em produção;
- versões fixadas, Dependabot e auditoria de CVEs no CI.

## Limites

Antes de aceitar dados reais, remova o auto cadastro público ou exija verificação e aprovação, além de implementar MFA, rate limiting no login e nas consultas, auditoria de ações, criptografia de campos, gestão de consentimento, retenção/expurgo, backup testado e revisão jurídica de privacidade aplicável.
